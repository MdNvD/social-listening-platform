import re
from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.collectors.models import CollectedMention


class DeduplicationService:
    """
    Lightweight duplicate detection service.

    Uses:
    1. Normalized URL matching
    2. Normalized content matching
    3. Samsung Galaxy model conflict detection
    4. TF-IDF cosine similarity

    This replaces the previous SentenceTransformer-based
    semantic similarity model to reduce memory usage.
    """

    def __init__(self, similarity_threshold: float = 0.82):
        self.similarity_threshold = similarity_threshold

    def find_duplicate(
        self,
        mention: CollectedMention,
        existing_mentions: list[CollectedMention],
    ) -> Optional[int]:
        """
        Return the index of an existing duplicate mention.

        Returns:
            int: index of duplicate mention
            None: if no duplicate is found
        """

        if not existing_mentions:
            return None

        current_url = self._normalize_url(mention.url)
        current_content = self._normalize_content(
            mention.content
        )

        for index, existing in enumerate(existing_mentions):
            existing_url = self._normalize_url(existing.url)

            # -------------------------------------------------
            # 1. Exact normalized URL match
            # -------------------------------------------------
            if current_url and existing_url:
                if current_url == existing_url:
                    return index

            # -------------------------------------------------
            # 2. Exact normalized content match
            # -------------------------------------------------
            existing_content = self._normalize_content(
                existing.content
            )

            if (
                current_content
                and existing_content
                and current_content == existing_content
            ):
                return index

            # -------------------------------------------------
            # 3. Galaxy model conflict
            # -------------------------------------------------
            if self._has_model_conflict(
                mention,
                existing,
            ):
                continue

            # -------------------------------------------------
            # 4. Lightweight semantic similarity
            # -------------------------------------------------
            if (
                current_content
                and existing_content
                and self._is_semantically_similar(
                    mention,
                    existing,
                )
            ):
                return index

        return None

    def _is_semantically_similar(
        self,
        current: CollectedMention,
        existing: CollectedMention,
    ) -> bool:
        """
        Compare two mentions using TF-IDF cosine similarity.
        """

        current_text = self._build_embedding_text(current)
        existing_text = self._build_embedding_text(existing)

        if not current_text or not existing_text:
            return False

        try:
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                sublinear_tf=True,
            )

            vectors = vectorizer.fit_transform(
                [current_text, existing_text]
            )

            similarity = cosine_similarity(
                vectors[0:1],
                vectors[1:2],
            )[0][0]

            return float(similarity) >= self.similarity_threshold

        except ValueError:
            # Happens when there are no usable terms.
            return False

    @staticmethod
    def _build_embedding_text(
        mention: CollectedMention,
    ) -> str:
        """
        Build text used for similarity comparison.

        Title is repeated so important title terms have
        slightly more influence.
        """

        title = (mention.title or "").strip()
        content = (mention.content or "").strip()

        return f"{title} {title} {content}".strip()

    @staticmethod
    def _normalize_content(text: str) -> str:
        """
        Normalize article content for exact comparison.
        """

        if not text:
            return ""

        text = text.lower()

        # Remove URLs
        text = re.sub(
            r"https?://\S+|www\.\S+",
            " ",
            text,
        )

        # Normalize whitespace
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        # Remove punctuation
        text = re.sub(
            r"[^\w\s]",
            "",
            text,
        )

        return text.strip()

    @staticmethod
    def _normalize_url(url: str) -> str:
        """
        Normalize URLs by removing tracking parameters.
        """

        if not url:
            return ""

        url = url.strip().lower()

        # Remove fragments
        url = url.split("#")[0]

        # Remove common tracking parameters
        url = re.sub(
            r"[?&](utm_[^=&]+|fbclid|gclid)=[^&]*",
            "",
            url,
        )

        # Remove trailing ?
        url = url.rstrip("?")

        # Remove trailing slash
        if url.endswith("/"):
            url = url[:-1]

        return url

    @staticmethod
    def _extract_galaxy_models(
        text: str,
    ) -> set[str]:
        """
        Extract Samsung Galaxy S-series model numbers.

        Example:
            'Samsung Galaxy S26 Ultra and S26 FE'
            -> {'s26'}
        """

        if not text:
            return set()

        matches = re.findall(
            r"\bGalaxy\s+S(\d+)\b",
            text,
            flags=re.IGNORECASE,
        )

        return {
            f"s{number.lower()}"
            for number in matches
        }

    @staticmethod
    def _has_model_conflict(
        first: CollectedMention,
        second: CollectedMention,
    ) -> bool:
        """
        Return True when two mentions refer to different
        Samsung Galaxy S-series models.
        """

        first_text = (
            f"{first.title or ''} "
            f"{first.content or ''}"
        )

        second_text = (
            f"{second.title or ''} "
            f"{second.content or ''}"
        )

        first_models = (
            DeduplicationService._extract_galaxy_models(
                first_text
            )
        )

        second_models = (
            DeduplicationService._extract_galaxy_models(
                second_text
            )
        )

        if not first_models or not second_models:
            return False

        return first_models.isdisjoint(second_models)