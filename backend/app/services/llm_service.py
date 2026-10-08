import hashlib
import json
import re
import threading
import time
from typing import Any

import requests


class LLMService:
    """
    Generates evidence-grounded AI insights using Ollama.

    The LLM receives structured evidence instead of the complete
    database.

    Pipeline:

        Evidence
            ↓
        Ollama
            ↓
        JSON parsing
            ↓
        Evidence-ID validation
            ↓
        Deterministic completion/fallback
            ↓
        Cache
            ↓
        Frontend

    Reliability features:

        - Local Ollama only
        - No paid API
        - Evidence-grounded prompting
        - Strict evidence-ID validation
        - Deterministic fallback
        - Request timeout
        - One Ollama generation at a time
        - In-memory result cache
    """

    OLLAMA_URL = (
        "http://127.0.0.1:11434/api/generate"
    )

    MODEL_NAME = "llama3.2:3b"

    # 45 seconds is enough for a small local model while
    # preventing the API from blocking for two minutes.
    TIMEOUT_SECONDS = 45

    # Keep identical AI insight results in memory for 10 minutes.
    CACHE_TTL_SECONDS = 600

    # Maximum number of cached insight results.
    MAX_CACHE_SIZE = 50

    # ---------------------------------------------------------
    # Ollama concurrency protection
    # ---------------------------------------------------------
    #
    # llama3.2:3b running locally on CPU can become very slow
    # if several generations happen simultaneously.
    #
    # Only one generation is allowed at a time.
    #
    _generation_lock = threading.Lock()

    # ---------------------------------------------------------
    # In-memory cache
    # ---------------------------------------------------------

    _cache: dict[
        str,
        tuple[float, dict[str, Any]],
    ] = {}

    # =========================================================
    # Generate insights
    # =========================================================

    def generate_insights(
        self,
        keyword: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generate structured AI insights from collected evidence.

        If the local LLM fails, deterministic evidence-based
        insights are returned instead of failing the entire API.

        Identical evidence is served from an in-memory cache.
        """

        total_mentions = int(
            evidence.get(
                "total_mentions",
                0,
            )
            or 0
        )

        # -----------------------------------------------------
        # No evidence
        # -----------------------------------------------------

        if total_mentions <= 0:
            return self._build_no_evidence_response(
                keyword=keyword
            )

        # -----------------------------------------------------
        # Build cache key
        # -----------------------------------------------------

        cache_key = self._build_cache_key(
            keyword=keyword,
            evidence=evidence,
        )

        # -----------------------------------------------------
        # Check cache
        # -----------------------------------------------------

        cached_response = self._get_cached(
            cache_key
        )

        if cached_response is not None:
            print(
                "AI insights cache hit."
            )

            return cached_response

        # -----------------------------------------------------
        # Build prompt
        # -----------------------------------------------------

        prompt = self._build_prompt(
            keyword=keyword,
            evidence=evidence,
        )

        # -----------------------------------------------------
        # Serialize Ollama generation
        # -----------------------------------------------------
        #
        # This prevents multiple simultaneous browser/API
        # requests from competing for the same local model.
        #
        # If another request already generated the same result
        # while this request was waiting, the cache is checked
        # again after acquiring the lock.
        # -----------------------------------------------------

        with self._generation_lock:

            cached_response = self._get_cached(
                cache_key
            )

            if cached_response is not None:
                print(
                    "AI insights cache hit after waiting."
                )

                return cached_response

            result = self._generate_with_ollama(
                prompt=prompt,
                keyword=keyword,
                evidence=evidence,
            )

            # -------------------------------------------------
            # Cache result
            # -------------------------------------------------

            self._store_cached(
                cache_key=cache_key,
                response=result,
            )

            return result

    # =========================================================
    # Ollama generation
    # =========================================================

    def _generate_with_ollama(
        self,
        prompt: str,
        keyword: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Perform one Ollama generation.

        Any failure falls back to deterministic evidence-based
        insights.
        """

        payload = {
            "model": self.MODEL_NAME,

            "prompt": prompt,

            "stream": False,

            "format": "json",

            "options": {
                "temperature": 0.1,

                # Smaller context reduces CPU inference time.
                "num_ctx": 4096,

                # Prevent excessively long model responses.
                "num_predict": 400,

                # Keep the model loaded for repeated requests.
                "keep_alive": "5m",
            },
        }

        try:

            response = requests.post(
                self.OLLAMA_URL,
                json=payload,
                timeout=self.TIMEOUT_SECONDS,
            )

            response.raise_for_status()

            data = response.json()

            raw_response = (
                data.get("response")
                or ""
            ).strip()

            if not raw_response:
                raise ValueError(
                    "Ollama returned an empty response."
                )

            # -------------------------------------------------
            # Robust JSON parsing
            # -------------------------------------------------

            parsed_response = (
                self._parse_json_response(
                    raw_response
                )
            )

            # -------------------------------------------------
            # Validate response
            # -------------------------------------------------

            validated_response = (
                self._validate_response(
                    parsed_response,
                    evidence=evidence,
                )
            )

            # -------------------------------------------------
            # Complete missing sections
            # -------------------------------------------------

            return self._complete_missing_sections(
                validated_response,
                evidence=evidence,
            )

        except requests.exceptions.Timeout:

            print(
                "\n"
                "WARNING: Ollama request timed out.\n"
                f"Reason: timeout after "
                f"{self.TIMEOUT_SECONDS} seconds.\n"
                "Using deterministic evidence fallback.\n"
            )

            return self._build_fallback_response(
                keyword=keyword,
                evidence=evidence,
            )

        except requests.exceptions.ConnectionError as error:

            print(
                "\n"
                "WARNING: Ollama connection failed.\n"
                f"Reason: {error}\n"
                "Using deterministic evidence fallback.\n"
            )

            return self._build_fallback_response(
                keyword=keyword,
                evidence=evidence,
            )

        except requests.RequestException as error:

            print(
                "\n"
                "WARNING: Ollama request failed.\n"
                f"Reason: {error}\n"
                "Using deterministic evidence fallback.\n"
            )

            return self._build_fallback_response(
                keyword=keyword,
                evidence=evidence,
            )

        except Exception as error:

            print(
                "\n"
                "WARNING: LLM insight generation failed.\n"
                f"Reason: {error}\n"
                "Using deterministic evidence fallback.\n"
            )

            return self._build_fallback_response(
                keyword=keyword,
                evidence=evidence,
            )

    # =========================================================
    # JSON parser
    # =========================================================

    @staticmethod
    def _parse_json_response(
        raw_response: str,
    ) -> dict[str, Any]:
        """
        Parse JSON returned by Ollama.

        Attempts:

            1. Direct JSON parsing
            2. Markdown fence removal
            3. JSON object extraction
        """

        # -----------------------------------------------------
        # Attempt 1
        # -----------------------------------------------------

        try:

            parsed = json.loads(
                raw_response
            )

            if not isinstance(
                parsed,
                dict,
            ):
                raise ValueError(
                    "LLM JSON response is not an object."
                )

            return parsed

        except json.JSONDecodeError:
            pass

        # -----------------------------------------------------
        # Attempt 2
        # -----------------------------------------------------

        cleaned = raw_response.strip()

        cleaned = re.sub(
            r"^```json\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"^```\s*",
            "",
            cleaned,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

        cleaned = cleaned.strip()

        try:

            parsed = json.loads(
                cleaned
            )

            if not isinstance(
                parsed,
                dict,
            ):
                raise ValueError(
                    "LLM JSON response is not an object."
                )

            return parsed

        except json.JSONDecodeError:
            pass

        # -----------------------------------------------------
        # Attempt 3
        # -----------------------------------------------------

        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if (
            start != -1
            and end != -1
            and end > start
        ):

            candidate = cleaned[
                start:end + 1
            ]

            try:

                parsed = json.loads(
                    candidate
                )

                if not isinstance(
                    parsed,
                    dict,
                ):
                    raise ValueError(
                        "Extracted JSON is not an object."
                    )

                return parsed

            except json.JSONDecodeError:
                pass

        raise ValueError(
            "The LLM returned invalid JSON."
        )

    # =========================================================
    # Prompt
    # =========================================================

    def _build_prompt(
        self,
        keyword: str,
        evidence: dict[str, Any],
    ) -> str:
        """
        Build an evidence-grounded prompt.

        The prompt remains intentionally conservative because
        the project uses a small local model.
        """

        # -----------------------------------------------------
        # Keep the prompt reasonably small.
        #
        # The complete evidence object can become large when
        # scheduled monitoring has accumulated many searches.
        # The LLM does not need every raw field.
        # -----------------------------------------------------

        compact_evidence = {
            "total_mentions": evidence.get(
                "total_mentions",
                0,
            ),

            "negative_mention_count": evidence.get(
                "negative_mention_count",
                0,
            ),

            "source_distribution": evidence.get(
                "source_distribution",
                [],
            ),

            "sentiment_distribution": evidence.get(
                "sentiment_distribution",
                [],
            ),

            "topic_distribution": evidence.get(
                "topic_distribution",
                [],
            ),

            "representative_mentions": [
                {
                    "id": mention.get("id"),
                    "source": mention.get("source"),
                    "title": self._truncate(
                        mention.get("title"),
                        180,
                    ),
                    "content": self._truncate(
                        mention.get("content"),
                        500,
                    ),
                    "sentiment": mention.get(
                        "sentiment"
                    ),
                    "topic": mention.get(
                        "topic"
                    ),
                }
                for mention in (
                    evidence.get(
                        "representative_mentions",
                        [],
                    )
                    or []
                )[:12]
            ],

            "positive_observations": [
                {
                    "id": mention.get("id"),
                    "title": self._truncate(
                        mention.get("title"),
                        180,
                    ),
                    "content": self._truncate(
                        mention.get("content"),
                        400,
                    ),
                }
                for mention in (
                    evidence.get(
                        "positive_observations",
                        [],
                    )
                    or []
                )[:3]
            ],

            "negative_observations": [
                {
                    "id": mention.get("id"),
                    "title": self._truncate(
                        mention.get("title"),
                        180,
                    ),
                    "content": self._truncate(
                        mention.get("content"),
                        400,
                    ),
                }
                for mention in (
                    evidence.get(
                        "negative_observations",
                        [],
                    )
                    or []
                )[:3]
            ],
        }

        evidence_json = json.dumps(
            compact_evidence,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

        return f"""
You are the AI insights analyst for a social listening platform.

Analyze ONLY the supplied evidence for:

KEYWORD:
{keyword}

Produce a concise evidence-grounded analysis.

STRICT RULES:

1. Use only information contained in EVIDENCE.

2. Never invent facts, events, statistics, users, sources,
   technical details, or opinions.

3. Every key theme MUST include evidence_ids.

4. Every pain point MUST include evidence_ids.

5. Every opportunity MUST include evidence_ids.

6. evidence_ids must refer only to actual evidence IDs.

7. Never invent evidence IDs.

8. Do not claim that an issue is widespread unless the
   supplied evidence directly supports that statement.

9. Do not claim that a source represents all users.

10. Treat sentiment and topic labels as analytical
    classifications, not independently verified facts.

11. Do not present a source-reported claim as independently
    verified.

12. If the sample is small, acknowledge the limitation.

13. Keep unrelated issues separate.

14. Do not create an opportunity simply because a mention
    is negative.

15. Recommended actions must be practical and conservative.

16. Do not recommend a specific technical solution unless
    the evidence explicitly supports it.

17. Do not rank competitors or declare a winner.

18. Prefer cautious wording such as:
    "The collected mentions indicate..."
    "The available evidence includes..."
    "One collected mention reports..."

IMPORTANT:

Produce useful themes when supported by evidence.

Produce pain points when negative or concern-related evidence
supports them.

Produce opportunities only when the evidence gives a reasonable
area to investigate.

If there is insufficient evidence for an opportunity, return [].

Return ONLY valid JSON.

OUTPUT EXACTLY THIS STRUCTURE:

{{
  "summary": "A concise 2-4 sentence evidence-grounded summary.",

  "key_themes": [
    {{
      "theme": "Short theme name",
      "description": "What the collected evidence indicates.",
      "evidence_ids": [123]
    }}
  ],

  "pain_points": [
    {{
      "title": "Short concern title",
      "description": "What the collected evidence reports.",
      "evidence_ids": [123]
    }}
  ],

  "opportunities": [
    {{
      "title": "Potential area to investigate",
      "description": "Why the evidence suggests this may be worth investigating.",
      "evidence_ids": [123]
    }}
  ],

  "recommended_actions": [
    "A cautious evidence-based action."
  ],

  "limitations": [
    "The analysis is based on the available collected mentions.",
    "The sample may not represent all users."
  ]
}}

EVIDENCE:

{evidence_json}
""".strip()

    # =========================================================
    # Validate response
    # =========================================================

    @staticmethod
    def _validate_response(
        data: Any,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "LLM response must be a JSON object."
            )

        summary = data.get(
            "summary",
            "",
        )

        key_themes = data.get(
            "key_themes",
            [],
        )

        pain_points = data.get(
            "pain_points",
            [],
        )

        opportunities = data.get(
            "opportunities",
            [],
        )

        recommended_actions = data.get(
            "recommended_actions",
            [],
        )

        limitations = data.get(
            "limitations",
            [],
        )

        # -----------------------------------------------------
        # Normalize types
        # -----------------------------------------------------

        if not isinstance(
            summary,
            str,
        ):
            summary = str(summary)

        if not isinstance(
            key_themes,
            list,
        ):
            key_themes = []

        if not isinstance(
            pain_points,
            list,
        ):
            pain_points = []

        if not isinstance(
            opportunities,
            list,
        ):
            opportunities = []

        if not isinstance(
            recommended_actions,
            list,
        ):
            recommended_actions = []

        if not isinstance(
            limitations,
            list,
        ):
            limitations = []

        # -----------------------------------------------------
        # Valid evidence IDs
        # -----------------------------------------------------

        valid_evidence_ids = (
            LLMService._get_valid_evidence_ids(
                evidence
            )
        )

        # -----------------------------------------------------
        # Key themes
        # -----------------------------------------------------

        key_themes = [
            item
            for item in key_themes
            if (
                isinstance(item, dict)
                and LLMService._has_valid_evidence_ids(
                    item,
                    valid_evidence_ids,
                )
                and LLMService._has_text(
                    item,
                    "theme",
                    "description",
                )
            )
        ]

        # -----------------------------------------------------
        # Pain points
        # -----------------------------------------------------

        pain_points = [
            item
            for item in pain_points
            if (
                isinstance(item, dict)
                and LLMService._has_valid_evidence_ids(
                    item,
                    valid_evidence_ids,
                )
                and LLMService._has_text(
                    item,
                    "title",
                    "description",
                )
            )
        ]

        # -----------------------------------------------------
        # Opportunities
        # -----------------------------------------------------

        opportunities = [
            item
            for item in opportunities
            if (
                isinstance(item, dict)
                and LLMService._has_valid_evidence_ids(
                    item,
                    valid_evidence_ids,
                )
                and LLMService._has_text(
                    item,
                    "title",
                    "description",
                )
            )
        ]

        # -----------------------------------------------------
        # Recommended actions
        # -----------------------------------------------------

        recommended_actions = [
            str(item).strip()
            for item in recommended_actions
            if (
                item is not None
                and str(item).strip()
            )
        ]

        # -----------------------------------------------------
        # Limitations
        # -----------------------------------------------------

        limitations = [
            str(item).strip()
            for item in limitations
            if (
                item is not None
                and str(item).strip()
            )
        ]

        # -----------------------------------------------------
        # Summary fallback
        # -----------------------------------------------------

        if not summary.strip():

            total_mentions = int(
                evidence.get(
                    "total_mentions",
                    0,
                )
                or 0
            )

            summary = (
                f"The collected evidence contains "
                f"{total_mentions} relevant unique mentions. "
                "The findings represent the available "
                "collected sample and should not be treated "
                "as representative of all users."
            )

        # -----------------------------------------------------
        # Sample limitation
        # -----------------------------------------------------

        total_mentions = int(
            evidence.get(
                "total_mentions",
                0,
            )
            or 0
        )

        sample_limitation = (
            f"The analysis is based on {total_mentions} "
            "relevant unique collected mentions and may "
            "not represent the broader user population."
        )

        if not any(
            "relevant unique collected mentions"
            in limitation.lower()
            for limitation in limitations
        ):

            limitations.insert(
                0,
                sample_limitation,
            )

        return {
            "summary": summary.strip(),

            "key_themes": key_themes,

            "pain_points": pain_points,

            "opportunities": opportunities,

            "recommended_actions":
                recommended_actions,

            "limitations": limitations,
        }

    # =========================================================
    # Complete missing sections
    # =========================================================

    @staticmethod
    def _complete_missing_sections(
        response: dict[str, Any],
        evidence: dict[str, Any],
    ) -> dict[str, Any]:

        if not response["key_themes"]:

            response["key_themes"] = (
                LLMService._build_theme_fallback(
                    evidence
                )
            )

        if not response["pain_points"]:

            response["pain_points"] = (
                LLMService._build_pain_point_fallback(
                    evidence
                )
            )

        if not response["recommended_actions"]:

            response["recommended_actions"] = (
                LLMService._build_action_fallback(
                    evidence
                )
            )

        # -----------------------------------------------------
        # Opportunities are intentionally NOT generated
        # automatically.
        #
        # Empty is safer than inventing an opportunity.
        # -----------------------------------------------------

        return response

    # =========================================================
    # Deterministic fallback after LLM failure
    # =========================================================

    @staticmethod
    def _build_fallback_response(
        keyword: str,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Complete evidence-based fallback.

        No invented facts are used.
        """

        total_mentions = int(
            evidence.get(
                "total_mentions",
                0,
            )
            or 0
        )

        source_distribution = (
            evidence.get(
                "source_distribution",
                [],
            )
            or []
        )

        negative_count = int(
            evidence.get(
                "negative_mention_count",
                0,
            )
            or 0
        )

        source_count = len(
            source_distribution
        )

        summary_parts = [
            f"The collected evidence for {keyword} "
            f"contains {total_mentions} relevant unique mentions."
        ]

        if source_count:

            summary_parts.append(
                f"The evidence comes from "
                f"{source_count} source"
                f"{'s' if source_count != 1 else ''}."
            )

        if negative_count:

            summary_parts.append(
                f"{negative_count} of the collected "
                "mentions were classified as negative."
            )

        summary_parts.append(
            "These findings describe the available "
            "collected sample and should not be treated "
            "as representative of all users."
        )

        return {
            "summary": " ".join(
                summary_parts
            ),

            "key_themes": (
                LLMService._build_theme_fallback(
                    evidence
                )
            ),

            "pain_points": (
                LLMService._build_pain_point_fallback(
                    evidence
                )
            ),

            "opportunities": [],

            "recommended_actions": (
                LLMService._build_action_fallback(
                    evidence
                )
            ),

            "limitations": [
                "The local LLM did not return usable structured JSON, so deterministic evidence-based fallbacks were used.",
                (
                    f"The analysis is based on "
                    f"{total_mentions} relevant unique "
                    "collected mentions and may not "
                    "represent the broader user population."
                ),
            ],
        }

    # =========================================================
    # Theme fallback
    # =========================================================

    @staticmethod
    def _build_theme_fallback(
        evidence: dict[str, Any],
    ) -> list[dict[str, Any]]:

        themes = []

        topic_distribution = (
            evidence.get(
                "topic_distribution",
                [],
            )
            or []
        )

        representative_mentions = {
            mention.get("id"): mention
            for mention in evidence.get(
                "representative_mentions",
                [],
            )
            if mention.get("id") is not None
        }

        for topic in topic_distribution:

            if not isinstance(
                topic,
                dict,
            ):
                continue

            topic_name = str(
                topic.get(
                    "topic",
                    "",
                )
            ).strip()

            count = int(
                topic.get(
                    "count",
                    0,
                )
                or 0
            )

            if not topic_name or count <= 0:
                continue

            matching_ids = []

            for (
                mention_id,
                mention,
            ) in representative_mentions.items():

                if (
                    mention.get("topic")
                    == topic_name
                ):
                    matching_ids.append(
                        mention_id
                    )

            if not matching_ids:
                continue

            themes.append(
                {
                    "theme": topic_name,

                    "description": (
                        f"The collected evidence contains "
                        f"{count} relevant mention"
                        f"{'s' if count != 1 else ''} "
                        f"classified under "
                        f"{topic_name}."
                    ),

                    "evidence_ids": (
                        matching_ids[:5]
                    ),
                }
            )

        return themes[:5]

    # =========================================================
    # Pain point fallback
    # =========================================================

    @staticmethod
    def _build_pain_point_fallback(
        evidence: dict[str, Any],
    ) -> list[dict[str, Any]]:

        pain_points = []

        negative_observations = (
            evidence.get(
                "negative_observations",
                [],
            )
            or []
        )

        for observation in negative_observations:

            if not isinstance(
                observation,
                dict,
            ):
                continue

            mention_id = observation.get(
                "id"
            )

            if mention_id is None:
                continue

            title = (
                observation.get("title")
                or observation.get("content")
                or "Negative mention"
            )

            topic = (
                observation.get("topic")
                or "Other"
            )

            pain_points.append(
                {
                    "title": (
                        f"{topic} concern"
                    ),

                    "description": (
                        "A collected mention classified "
                        "as negative reports the following: "
                        f"{str(title).strip()}"
                    ),

                    "evidence_ids": [
                        mention_id
                    ],
                }
            )

        return pain_points[:5]

    # =========================================================
    # Action fallback
    # =========================================================

    @staticmethod
    def _build_action_fallback(
        evidence: dict[str, Any],
    ) -> list[str]:

        actions = []

        total_mentions = int(
            evidence.get(
                "total_mentions",
                0,
            )
            or 0
        )

        negative_count = int(
            evidence.get(
                "negative_mention_count",
                0,
            )
            or 0
        )

        source_distribution = (
            evidence.get(
                "source_distribution",
                [],
            )
            or []
        )

        if total_mentions > 0:

            actions.append(
                "Review the supporting source mentions "
                "before drawing broader conclusions."
            )

        if negative_count > 0:

            actions.append(
                "Investigate the negative observations "
                "using the linked original sources."
            )

        if len(source_distribution) <= 1:

            actions.append(
                "Collect mentions from additional sources "
                "before treating the findings as broadly "
                "representative."
            )

        if total_mentions < 10:

            actions.append(
                "Collect additional mentions to increase "
                "the evidence sample."
            )

        return actions[:4]

    # =========================================================
    # No evidence
    # =========================================================

    @staticmethod
    def _build_no_evidence_response(
        keyword: str,
    ) -> dict[str, Any]:

        return {
            "summary": (
                "There is not enough collected evidence "
                f"to generate meaningful AI insights for "
                f"{keyword}."
            ),

            "key_themes": [],

            "pain_points": [],

            "opportunities": [],

            "recommended_actions": [
                "Collect additional mentions before "
                "drawing broader conclusions."
            ],

            "limitations": [
                "No relevant, non-duplicate mentions "
                "were available for this keyword."
            ],
        }

    # =========================================================
    # Evidence ID collection
    # =========================================================

    @staticmethod
    def _get_valid_evidence_ids(
        evidence: dict[str, Any],
    ) -> set[int]:

        valid_ids: set[int] = set()

        collections = (
            "representative_mentions",
            "positive_observations",
            "negative_observations",
            "potential_pain_points",
            "potential_opportunities",
        )

        for collection_name in collections:

            collection = evidence.get(
                collection_name,
                [],
            )

            if not isinstance(
                collection,
                list,
            ):
                continue

            for item in collection:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                mention_id = item.get(
                    "id"
                )

                if mention_id is None:
                    continue

                try:

                    valid_ids.add(
                        int(mention_id)
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    continue

        return valid_ids

    # =========================================================
    # Text validation
    # =========================================================

    @staticmethod
    def _has_text(
        item: dict[str, Any],
        *fields: str,
    ) -> bool:

        for field in fields:

            value = item.get(
                field,
                "",
            )

            if not isinstance(
                value,
                str,
            ):
                return False

            if not value.strip():
                return False

        return True

    # =========================================================
    # Evidence ID validation
    # =========================================================

    @staticmethod
    def _has_valid_evidence_ids(
        item: dict[str, Any],
        valid_evidence_ids: set[int],
    ) -> bool:

        evidence_ids = item.get(
            "evidence_ids",
            [],
        )

        if not isinstance(
            evidence_ids,
            list,
        ):
            return False

        normalized_ids = []

        for evidence_id in evidence_ids:

            try:

                normalized_id = int(
                    evidence_id
                )

            except (
                TypeError,
                ValueError,
            ):

                return False

            normalized_ids.append(
                normalized_id
            )

        if not normalized_ids:
            return False

        if not all(
            evidence_id
            in valid_evidence_ids
            for evidence_id in normalized_ids
        ):
            return False

        item["evidence_ids"] = list(
            dict.fromkeys(
                normalized_ids
            )
        )

        return True

    # =========================================================
    # Cache key
    # =========================================================

    @classmethod
    def _build_cache_key(
        cls,
        keyword: str,
        evidence: dict[str, Any],
    ) -> str:
        """
        Create a stable hash from the actual evidence used
        for insight generation.

        Search IDs themselves are intentionally excluded so
        that identical accumulated evidence from different
        search records can reuse the same result.
        """

        cache_data = {
            "keyword": keyword,

            "total_mentions": evidence.get(
                "total_mentions",
                0,
            ),

            "negative_mention_count": evidence.get(
                "negative_mention_count",
                0,
            ),

            "source_distribution": evidence.get(
                "source_distribution",
                [],
            ),

            "sentiment_distribution": evidence.get(
                "sentiment_distribution",
                [],
            ),

            "topic_distribution": evidence.get(
                "topic_distribution",
                [],
            ),

            "representative_mentions": evidence.get(
                "representative_mentions",
                [],
            ),

            "positive_observations": evidence.get(
                "positive_observations",
                [],
            ),

            "negative_observations": evidence.get(
                "negative_observations",
                [],
            ),
        }

        serialized = json.dumps(
            cache_data,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )

        return hashlib.sha256(
            serialized.encode(
                "utf-8"
            )
        ).hexdigest()

    # =========================================================
    # Cache read
    # =========================================================

    @classmethod
    def _get_cached(
        cls,
        cache_key: str,
    ) -> dict[str, Any] | None:

        cached = cls._cache.get(
            cache_key
        )

        if cached is None:
            return None

        created_at, response = cached

        if (
            time.time()
            - created_at
            > cls.CACHE_TTL_SECONDS
        ):

            cls._cache.pop(
                cache_key,
                None,
            )

            return None

        return response

    # =========================================================
    # Cache write
    # =========================================================

    @classmethod
    def _store_cached(
        cls,
        cache_key: str,
        response: dict[str, Any],
    ):

        # Prevent unlimited memory growth.
        if (
            len(cls._cache)
            >= cls.MAX_CACHE_SIZE
        ):

            oldest_key = min(
                cls._cache,
                key=lambda key:
                    cls._cache[key][0],
            )

            cls._cache.pop(
                oldest_key,
                None,
            )

        cls._cache[
            cache_key
        ] = (
            time.time(),
            response,
        )

    # =========================================================
    # Text truncation
    # =========================================================

    @staticmethod
    def _truncate(
        value: Any,
        max_length: int,
    ) -> str:

        if value is None:
            return ""

        text = str(
            value
        ).strip()

        if len(text) <= max_length:
            return text

        return (
            text[: max_length - 3]
            + "..."
        )