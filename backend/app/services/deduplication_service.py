import re
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.collectors.models import CollectedMention


class DeduplicationService:
    """
    Detects duplicate and near-duplicate mentions.

    Detection order:
    1. Exact normalized URL
    2. Exact normalized content
    3. Product/model conflict detection
    4. Semantic similarity using sentence embeddings

    Important:
    Two articles about different product models should not
    automatically become duplicates simply because their wording
    is very similar.

    Example:

        Galaxy S26 review
        Galaxy S25 review

    These are different mentions and should remain separate.
    """

    MODEL_NAME = "all-MiniLM-L6-v2"

    def __init__(
        self,
        similarity_threshold: float = 0.82,
    ):
        self.similarity_threshold = similarity_threshold
        self.model = self._load_model()

    # ==================================================
    # MODEL
    # ==================================================

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_model():
        print(
            f"Loading deduplication model: "
            f"{DeduplicationService.MODEL_NAME}"
        )

        return SentenceTransformer(
            DeduplicationService.MODEL_NAME
        )

    # ==================================================
    # MAIN DUPLICATE DETECTION
    # ==================================================

    def find_duplicate(
        self,
        mention: CollectedMention,
        existing_mentions: list[CollectedMention],
    ) -> int | None:

        normalized_url = self._normalize_url(
            mention.url
        )

        normalized_content = (
            self._normalize_text(
                mention.content
            )
        )

        # ------------------------------------------
        # 1. EXACT NORMALIZED URL
        # ------------------------------------------

        for index, existing in enumerate(
            existing_mentions
        ):

            existing_url = self._normalize_url(
                existing.url
            )

            if (
                normalized_url
                and normalized_url == existing_url
            ):

                print(
                    "\nDuplicate detected by "
                    "exact normalized URL."
                )

                return index

        # ------------------------------------------
        # 2. EXACT NORMALIZED CONTENT
        # ------------------------------------------

        for index, existing in enumerate(
            existing_mentions
        ):

            existing_content = (
                self._normalize_text(
                    existing.content
                )
            )

            if (
                normalized_content
                and normalized_content == existing_content
            ):

                print(
                    "\nDuplicate detected by "
                    "exact normalized content."
                )

                return index

        # ------------------------------------------
        # 3. PRODUCT / MODEL CONFLICT CHECK
        # ------------------------------------------

        for index, existing in enumerate(
            existing_mentions
        ):

            model_conflict = (
                self._has_model_conflict(
                    mention,
                    existing,
                )
            )

            if model_conflict:

                print(
                    "\nMODEL CONFLICT DETECTED"
                )

                print(
                    f"Current title : "
                    f"{mention.title}"
                )

                print(
                    f"Existing title: "
                    f"{existing.title}"
                )

                print(
                    "Result: NOT a duplicate."
                )

                return None

        # ------------------------------------------
        # 4. SEMANTIC SIMILARITY
        # ------------------------------------------

        if not existing_mentions:
            return None

        current_text = self._build_embedding_text(
            mention
        )

        existing_texts = [
            self._build_embedding_text(existing)
            for existing in existing_mentions
        ]

        current_embedding = self.model.encode(
            current_text,
            normalize_embeddings=True,
        )

        existing_embeddings = self.model.encode(
            existing_texts,
            normalize_embeddings=True,
        )

        similarities = (
            existing_embeddings
            @ current_embedding
        )

        best_index = int(
            similarities.argmax()
        )

        best_score = float(
            similarities[best_index]
        )

        print(
            "\nSEMANTIC DEDUPLICATION"
        )

        print(
            f"Best index : {best_index}"
        )

        print(
            f"Best score : {best_score:.4f}"
        )

        print(
            f"Threshold  : "
            f"{self.similarity_threshold:.4f}"
        )

        is_duplicate = (
            best_score
            >= self.similarity_threshold
        )

        print(
            f"Decision   : {is_duplicate}"
        )

        if is_duplicate:

            print(
                "RESULT: Duplicate because "
                "semantic similarity exceeds "
                "the configured threshold."
            )

            return best_index

        print(
            "RESULT: Not a duplicate because "
            "semantic similarity is below "
            "the configured threshold."
        )

        return None

    # ==================================================
    # MODEL CONFLICT DETECTION
    # ==================================================

    @classmethod
    def _has_model_conflict(
        cls,
        first: CollectedMention,
        second: CollectedMention,
    ) -> bool:
        """
        Detect whether two mentions explicitly refer to
        different product models.

        Example:

            Galaxy S26
            Galaxy S25

        returns True.

        Example:

            Galaxy S26
            Galaxy S26

        returns False.

        This prevents semantic similarity from incorrectly
        merging different product generations.
        """

        first_text = cls._normalize_text(
            f"{first.title or ''} "
            f"{first.content or ''}"
        )

        second_text = cls._normalize_text(
            f"{second.title or ''} "
            f"{second.content or ''}"
        )

        first_models = cls._extract_galaxy_models(
            first_text
        )

        second_models = cls._extract_galaxy_models(
            second_text
        )

        # If either mention does not contain an
        # identifiable Galaxy S model, we cannot
        # establish a model conflict.
        if not first_models or not second_models:
            return False

        # If there is at least one model in each mention
        # and there is no common model, treat them as
        # different product mentions.
        common_models = (
            first_models.intersection(
                second_models
            )
        )

        return len(common_models) == 0

    @staticmethod
    def _extract_galaxy_models(
        text: str,
    ) -> set[str]:
        """
        Extract Samsung Galaxy S-series model numbers.

        Examples detected:

            Galaxy S25
            Galaxy S26
            Galaxy S26 Ultra
            Galaxy S26 Plus
            Galaxy S26 FE

        The returned value uses the base model number,
        for example:

            Galaxy S26 Ultra -> s26
            Galaxy S26 FE    -> s26
        """

        pattern = r"\bgalaxy\s+(s\d+)\b"

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        return {
            match.lower()
            for match in matches
        }

    # ==================================================
    # EMBEDDING TEXT
    # ==================================================

    @classmethod
    def _build_embedding_text(
        cls,
        mention: CollectedMention,
    ) -> str:
        """
        Build the text used by the embedding model.

        The title is repeated deliberately so important
        information from the title receives stronger
        influence during similarity comparison.
        """

        title = cls._normalize_text(
            mention.title or ""
        )

        content = cls._normalize_text(
            mention.content or ""
        )

        if title and content:

            return (
                f"{title}. "
                f"{title}. "
                f"{content}"
            )

        return title or content

    # ==================================================
    # TEXT NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_text(
        value: str,
    ) -> str:
        """
        Normalize text for comparison and embeddings.
        """

        if not value:
            return ""

        value = value.lower()

        # Remove URLs.
        value = re.sub(
            r"https?://\S+",
            " ",
            value,
        )

        # Keep letters, numbers and spaces.
        value = re.sub(
            r"[^a-z0-9\s]",
            " ",
            value,
        )

        # Normalize whitespace.
        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    # ==================================================
    # URL NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_url(
        url: str,
    ) -> str:
        """
        Normalize URLs before comparison.

        Removes:
        - fragments
        - common tracking parameters
        """

        if not url:
            return ""

        url = url.strip().lower()

        # Remove fragment.
        url = url.split("#")[0]

        # Remove tracking parameters.
        url = re.sub(
            r"[?&]"
            r"(utm_[^=&]+|"
            r"fbclid|"
            r"gclid|"
            r"oc)="
            r"[^&]*",
            "",
            url,
        )

        # Remove leftover ? or &.
        url = url.rstrip("?&")

        return url