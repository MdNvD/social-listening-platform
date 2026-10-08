import re
from typing import Tuple

from app.collectors.models import CollectedMention


class RelevanceService:
    """
    Determines whether a collected mention is genuinely relevant
    to the user's search keyword.

    Relevance V3 focuses on high precision for multi-word searches.

    Signals used:

    1. Exact keyword phrase in title
    2. Exact keyword phrase in content
    3. Keyword term coverage
    4. Important/product/model terms
    5. Keyword terms appearing close together
    6. Keyword/model variants
    7. Conflicting model numbers
    8. Repeated body-only mentions
    9. Incidental body-only mention protection

    Examples
    --------

    Search:
        Google Pixel

    Relevant:
        "Google Pixel 10 review"

    Relevant:
        "Google Pixel phones receive a major update"

    Usually irrelevant:
        "T-Mobile brings back its iconic referral discount"

    if "Google Pixel" appears only incidentally in the
    article body.

    Search:
        Samsung Galaxy S26

    Relevant:
        "Samsung Galaxy S26 review"

    Irrelevant:
        "Samsung Galaxy S27 announced"
    """

    # =========================================================
    # Configuration
    # =========================================================

    DEFAULT_THRESHOLD = 0.60

    # Maximum number of tokens between keyword terms
    # for a proximity match.
    PROXIMITY_WINDOW = 5

    # Additional weight for important terms such as
    # product/model numbers.
    IMPORTANT_TERM_WEIGHT = 0.30

    def __init__(
        self,
        relevance_threshold: float = DEFAULT_THRESHOLD,
    ):
        self.relevance_threshold = (
            relevance_threshold
        )

    # =========================================================
    # Main relevance analysis
    # =========================================================

    def analyze(
        self,
        mention: CollectedMention,
    ) -> Tuple[float, bool]:

        # -----------------------------------------------------
        # Normalize input
        # -----------------------------------------------------

        keyword = self._normalize_text(
            mention.keyword
        )

        title = self._normalize_text(
            mention.title or ""
        )

        content = self._normalize_text(
            mention.content or ""
        )

        # -----------------------------------------------------
        # Basic validation
        # -----------------------------------------------------

        if not keyword:
            return 0.0, False

        if not title and not content:
            return 0.0, False

        # -----------------------------------------------------
        # Extract keyword terms
        # -----------------------------------------------------

        keyword_terms = (
            self._extract_terms(keyword)
        )

        if not keyword_terms:
            return 0.0, False

        # -----------------------------------------------------
        # Searchable text
        # -----------------------------------------------------

        searchable_text = (
            f"{title} {content}"
        ).strip()

        # =====================================================
        # Exact phrase matching
        # =====================================================

        exact_title_match = (
            keyword in title
        )

        exact_content_match = (
            keyword in content
        )

        exact_phrase_match = (
            exact_title_match
            or exact_content_match
        )

        # =====================================================
        # Keyword term matching
        # =====================================================

        matched_terms = [
            term
            for term in keyword_terms
            if self._term_exists(
                term,
                searchable_text,
            )
        ]

        matched_count = len(
            matched_terms
        )

        # =====================================================
        # Title term matching
        # =====================================================

        title_matched_terms = [
            term
            for term in keyword_terms
            if self._term_exists(
                term,
                title,
            )
        ]

        title_match_count = len(
            title_matched_terms
        )

        # =====================================================
        # Important terms
        # =====================================================

        important_terms = (
            self._identify_important_terms(
                keyword_terms
            )
        )

        important_matches = [
            term
            for term in important_terms
            if self._term_exists(
                term,
                searchable_text,
            )
        ]

        important_match_count = len(
            important_matches
        )

        # =====================================================
        # Proximity
        # =====================================================

        proximity_match = (
            self._terms_are_close(
                keyword_terms,
                title,
                self.PROXIMITY_WINDOW,
            )
            or
            self._terms_are_close(
                keyword_terms,
                content,
                self.PROXIMITY_WINDOW,
            )
        )

        # =====================================================
        # Variant matching
        # =====================================================

        variant_match = (
            self._has_variant_match(
                keyword_terms,
                searchable_text,
            )
        )

        # =====================================================
        # Model conflict
        # =====================================================

        title_model_conflict = (
            self._has_conflicting_model_in_title(
                keyword_terms,
                title,
            )
        )

        # =====================================================
        # Initial score
        # =====================================================

        score = 0.0

        # -----------------------------------------------------
        # Exact phrase score
        # -----------------------------------------------------
        #
        # Exact phrase in title:
        # Strong signal.
        #
        # Exact phrase only in content:
        # Weak signal because the phrase may be an incidental
        # reference.
        # -----------------------------------------------------

        if exact_title_match:

            score += 0.65

        elif exact_content_match:

            score += 0.10

        # -----------------------------------------------------
        # Term coverage
        # -----------------------------------------------------

        term_coverage = (
            matched_count
            / len(keyword_terms)
        )

        score += (
            term_coverage * 0.15
        )

        # -----------------------------------------------------
        # Important term coverage
        # -----------------------------------------------------

        if important_terms:

            important_coverage = (
                important_match_count
                / len(important_terms)
            )

            score += (
                important_coverage
                * self.IMPORTANT_TERM_WEIGHT
            )

        # -----------------------------------------------------
        # Title coverage
        # -----------------------------------------------------

        if title:

            title_coverage = (
                title_match_count
                / len(keyword_terms)
            )

            score += min(
                title_coverage * 0.15,
                0.15,
            )

        # -----------------------------------------------------
        # Proximity
        # -----------------------------------------------------
        #
        # Proximity is useful when the keyword terms occur
        # together.
        #
        # We only award this additional score when a title
        # exists. This prevents body-only incidental references
        # from becoming too strong.
        # -----------------------------------------------------

        if proximity_match:

            if title:

                score += 0.20

        # -----------------------------------------------------
        # Variant match
        # -----------------------------------------------------

        if variant_match:

            score += 0.10

        # =====================================================
        # Missing important terms
        # =====================================================

        missing_important_terms = [
            term
            for term in important_terms
            if not self._term_exists(
                term,
                searchable_text,
            )
        ]

        if missing_important_terms:

            score -= 0.35

        # =====================================================
        # Conflicting model protection
        # =====================================================

        if title_model_conflict:

            print(
                "\nMODEL CONFLICT IN TITLE"
            )

            print(
                f"Keyword : {mention.keyword}"
            )

            print(
                f"Title   : {mention.title}"
            )

            print(
                "Result  : "
                "Title focuses on a different model."
            )

            score -= 0.70

        # =====================================================
        # Multi-word precision rules
        # =====================================================

        if len(keyword_terms) >= 2:

            # -------------------------------------------------
            # All terms present anywhere
            # -------------------------------------------------

            all_terms_present = (
                matched_count
                == len(keyword_terms)
            )

            # -------------------------------------------------
            # All terms present in title
            # -------------------------------------------------

            strong_title_match = (
                title_match_count
                == len(keyword_terms)
            )

            # -------------------------------------------------
            # Strong content match
            # -------------------------------------------------
            #
            # The complete keyword must occur in content,
            # every term must exist, and the terms must be
            # close together.
            # -------------------------------------------------

            strong_content_match = (
                exact_content_match
                and all_terms_present
                and proximity_match
            )

            # -------------------------------------------------
            # Body-only exact phrase
            # -------------------------------------------------
            #
            # If the exact keyword occurs in the content but
            # not in the title, we need additional evidence.
            # -------------------------------------------------

            body_only_exact_match = (
                exact_content_match
                and not exact_title_match
            )

            if body_only_exact_match:

                # Count exact phrase occurrences.
                phrase_occurrences = len(
                    re.findall(
                        rf"\b{re.escape(keyword)}\b",
                        content,
                    )
                )

                # -------------------------------------------------
                # One body-only occurrence
                # -------------------------------------------------
                #
                # This is treated as a likely incidental mention.
                # Apply a strong penalty.
                # -------------------------------------------------

                if phrase_occurrences <= 1:

                    score -= 0.70

                # -------------------------------------------------
                # Multiple body occurrences
                # -------------------------------------------------

                elif phrase_occurrences >= 2:

                    # Repeated references provide some evidence
                    # that the searched topic is actually relevant.
                    score += 0.05

            # -------------------------------------------------
            # General multi-word precision rule
            # -------------------------------------------------
            #
            # A multi-word search must have strong structural
            # evidence.
            # -------------------------------------------------

            if not (
                exact_title_match
                or strong_title_match
                or strong_content_match
            ):

                score -= 0.50

        # =====================================================
        # Single-word keyword handling
        # =====================================================

        if len(keyword_terms) == 1:

            term = keyword_terms[0]

            if not self._term_exists(
                term,
                searchable_text,
            ):

                score = 0.0

        # =====================================================
        # Score normalization
        # =====================================================

        score = max(
            0.0,
            min(
                score,
                1.0,
            ),
        )

        # =====================================================
        # Final decision
        # =====================================================

        is_relevant = (
            score
            >= self.relevance_threshold
        )

        return (
            round(
                score,
                4,
            ),
            is_relevant,
        )

    # =========================================================
    # Text normalization
    # =========================================================

    @staticmethod
    def _normalize_text(
        value: str,
    ) -> str:

        if not value:
            return ""

        value = value.lower()

        # Remove URLs.
        value = re.sub(
            r"https?://\S+",
            " ",
            value,
        )

        # Keep only letters, numbers and whitespace.
        value = re.sub(
            r"[^a-z0-9\s]",
            " ",
            value,
        )

        # Collapse repeated whitespace.
        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    # =========================================================
    # Keyword extraction
    # =========================================================

    @staticmethod
    def _extract_terms(
        keyword: str,
    ) -> list[str]:

        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "for",
            "of",
            "to",
            "in",
            "on",
            "with",
            "is",
            "are",
        }

        return [
            term
            for term in keyword.split()
            if term not in stop_words
        ]

    # =========================================================
    # Important term identification
    # =========================================================

    @staticmethod
    def _identify_important_terms(
        terms: list[str],
    ) -> list[str]:

        important_terms = []

        # Product/model numbers are highly important.
        #
        # Examples:
        #   s26
        #   pixel10
        #   iphone17
        #   model3
        #
        for term in terms:

            if any(
                character.isdigit()
                for character in term
            ):

                important_terms.append(
                    term
                )

        # If no model number exists, treat the final
        # meaningful keyword as important.
        #
        # Example:
        #   Google Pixel
        #
        # Important term:
        #   Pixel
        #
        if (
            not important_terms
            and terms
        ):

            important_terms.append(
                terms[-1]
            )

        return important_terms

    # =========================================================
    # Term existence
    # =========================================================

    @staticmethod
    def _term_exists(
        term: str,
        text: str,
    ) -> bool:

        pattern = (
            rf"\b{re.escape(term)}\b"
        )

        return (
            re.search(
                pattern,
                text,
            )
            is not None
        )

    # =========================================================
    # Proximity matching
    # =========================================================

    @classmethod
    def _terms_are_close(
        cls,
        keyword_terms: list[str],
        text: str,
        window: int,
    ) -> bool:

        if not keyword_terms:
            return False

        if not text:
            return False

        tokens = text.split()

        positions = {}

        # Find every occurrence of every keyword term.
        for index, token in enumerate(
            tokens
        ):

            for term in keyword_terms:

                if token == term:

                    positions.setdefault(
                        term,
                        [],
                    ).append(
                        index
                    )

        # Every keyword term must exist.
        if any(
            term not in positions
            for term in keyword_terms
        ):

            return False

        first_term = keyword_terms[0]

        # Try every occurrence of the first keyword term.
        for first_position in positions[
            first_term
        ]:

            min_position = (
                first_position
            )

            max_position = (
                first_position
            )

            # Find the closest occurrence of every other
            # keyword term.
            for term in keyword_terms[1:]:

                closest_position = min(
                    positions[term],
                    key=lambda position: abs(
                        position
                        - first_position
                    ),
                )

                min_position = min(
                    min_position,
                    closest_position,
                )

                max_position = max(
                    max_position,
                    closest_position,
                )

            distance = (
                max_position
                - min_position
            )

            if distance <= window:

                return True

        return False

    # =========================================================
    # Conflicting model detection
    # =========================================================

    @classmethod
    def _has_conflicting_model_in_title(
        cls,
        keyword_terms: list[str],
        title: str,
    ) -> bool:

        target_models = (
            cls._extract_model_numbers(
                keyword_terms
            )
        )

        title_models = (
            cls._extract_model_numbers(
                title.split()
            )
        )

        # No model in keyword -> no model conflict.
        if not target_models:
            return False

        # No model in title -> nothing to compare.
        if not title_models:
            return False

        # If title contains a model number that does not
        # belong to the searched model, treat it as a conflict.
        for title_model in title_models:

            if title_model not in target_models:

                return True

        return False

    # =========================================================
    # Model number extraction
    # =========================================================

    @staticmethod
    def _extract_model_numbers(
        terms: list[str],
    ) -> set[str]:

        models = set()

        for term in terms:

            matches = re.findall(
                r"\b[a-z]*\d+[a-z0-9]*\b",
                term.lower(),
            )

            for match in matches:

                models.add(
                    match
                )

        return models

    # =========================================================
    # Variant matching
    # =========================================================

    @classmethod
    def _has_variant_match(
        cls,
        keyword_terms: list[str],
        searchable_text: str,
    ) -> bool:

        if not keyword_terms:
            return False

        # Find keyword terms containing numbers.
        model_terms = [
            term
            for term in keyword_terms
            if any(
                character.isdigit()
                for character in term
            )
        ]

        # No model/product number.
        if not model_terms:
            return False

        # A matching model term counts as a variant signal.
        for model_term in model_terms:

            if cls._term_exists(
                model_term,
                searchable_text,
            ):

                return True

        return False