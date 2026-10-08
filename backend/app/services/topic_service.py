from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


class TopicService:
    """
    Topic classification service using sentence embeddings.

    Primary classifier:
        sentence-transformers/all-MiniLM-L6-v2

    The classifier compares a mention against semantic topic
    prototypes.

    Topic V4 adds targeted domain-specific signals for topics
    that are difficult to distinguish using embeddings alone.

    Supported topics:

        Product
        Pricing
        Customer service
        Quality
        Competitors
        Complaints
        Features
        Security
        Other
    """

    MODEL_NAME = "all-MiniLM-L6-v2"

    # =========================================================
    # TOPIC EXAMPLES
    # =========================================================

    TOPIC_EXAMPLES = {

        # =====================================================
        # PRODUCT
        # =====================================================

        "Product": [
            "The phone itself looks great.",
            "I like the design of the product.",
            "The smartphone feels comfortable to hold.",
            "I bought the Galaxy S26 and like the phone.",
            "The device has a premium design.",
            "The Galaxy S26 is a well designed smartphone.",
            "I really like the phone.",
            "The product feels premium and well made.",
            "The phone is attractive and well designed.",
            "The smartphone has a good overall design.",
        ],

        # =====================================================
        # PRICING
        # =====================================================

        "Pricing": [
            "The phone is too expensive.",
            "The price of the Galaxy S26 is too high.",
            "Samsung increased the price.",
            "The phone is available at a discount.",
            "The product is affordable.",
            "The price dropped after the discount.",
            "Samsung raised the cost of the phone.",
            "The Galaxy S26 is expensive for its specifications.",
            "The price increased by 17 percent.",
            "The phone became cheaper after a discount.",
            "Samsung reduced the price of the phone.",
            "The product costs more than before.",
        ],

        # =====================================================
        # CUSTOMER SERVICE
        # =====================================================

        "Customer service": [
            "Samsung customer support helped me.",
            "The customer care team solved my problem.",
            "I contacted support about my issue.",
            "Customer service took three days to respond.",
            "The support representative was helpful.",
            "Samsung support responded to my complaint.",
            "The customer service team handled my issue.",
            "I contacted Samsung customer care.",
            "Samsung support provided the release date.",
            "The support team helped resolve my problem.",
            "Customer service refused to help me.",
        ],

        # =====================================================
        # QUALITY
        # =====================================================

        "Quality": [
            "The camera quality is excellent.",
            "The display quality is disappointing.",
            "The phone has poor build quality.",
            "The battery quality is good.",
            "The device is reliable and well built.",
            "The phone overheats and has poor performance.",
            "The Galaxy S26 has excellent build quality and reliability.",
            "The phone has poor durability.",
            "The device feels cheaply built.",
            "The hardware quality is disappointing.",
            "Samsung needs to improve the build quality.",
            "The phone has excellent hardware quality.",
            "The product has reliability problems.",
            "The Galaxy S26 has bad build quality.",
            "The phone has serious hardware problems.",
            "The phone keeps crashing.",
            "The phone has performance problems.",
            "The device has a battery problem.",
            "The camera has poor image quality.",
        ],

        # =====================================================
        # COMPETITORS
        # =====================================================

        "Competitors": [
            "The Galaxy S26 is better than the iPhone.",
            "I would choose the Pixel instead.",
            "Samsung is competing with Apple.",
            "Compared with the iPhone, this phone is better.",
            "The Galaxy S26 competes with Google Pixel.",
            "The iPhone is a competitor to Samsung.",
            "The Galaxy S26 is competing against the Pixel.",
            "Samsung and Apple are competing in the smartphone market.",
            "I prefer the iPhone over the Galaxy S26.",
            "The Pixel is an alternative to the Galaxy S26.",
            "Compared with the previous iPhone, the Galaxy is better.",
            "Samsung is competing against Google.",
        ],

        # =====================================================
        # COMPLAINTS
        # =====================================================

        "Complaints": [
            "I am very disappointed with this phone.",
            "This phone keeps freezing and needs to be fixed.",
            "I am unhappy with the product.",
            "The phone stopped working after two weeks.",
            "Samsung needs to fix this problem.",
            "I have a serious problem with this product.",
            "The Galaxy S26 keeps crashing.",
            "I am frustrated because the phone does not work properly.",
            "The product has a serious issue.",
            "I regret buying this phone.",
            "The product does not work as expected.",
            "I am unhappy with the way this issue was handled.",
        ],

        # =====================================================
        # FEATURES
        # =====================================================

        "Features": [
            "The phone has a new AI feature.",
            "Samsung added new camera features.",
            "The Galaxy S26 supports satellite connectivity.",
            "I like the new AI editing tools.",
            "The phone has a new camera mode.",
            "This device supports a new technology.",
            "The Galaxy S26 supports non-protected virtual machines.",
            "The Snapdragon chip supports new virtualization capabilities.",
            "The phone has a new technical capability.",
            "Samsung introduced a new hardware capability.",
            "The Galaxy S26 supports advanced virtualization.",
            "The device has a new connectivity capability.",
            "The phone supports a new software feature.",
            "The smartphone introduces new technical functionality.",
            "The phone has a new capability.",
            "Samsung added a new function to the phone.",
        ],

        # =====================================================
        # SECURITY
        # =====================================================

        "Security": [
            "The phone has a security vulnerability.",
            "Google Pixel phones were exploited in a targeted attack.",
            "The device was affected by a zero-day vulnerability.",
            "Hackers attacked the smartphone.",
            "The phone has a critical security flaw.",
            "There is a permission bypass vulnerability.",
            "The modem has a security issue.",
            "The device was compromised by attackers.",
            "A zero-click attack affects the phone.",
            "The vulnerability allows attackers to bypass permissions.",
            "Security researchers discovered a flaw in the device.",
            "The phone was targeted in a cyber attack.",
            "A security patch fixes a vulnerability.",
            "The device has a serious software security flaw.",
            "The device has a permission bypass.",
            "Attackers can bypass permissions on the device.",
        ],

        # =====================================================
        # OTHER
        # =====================================================

        "Other": [
            "Samsung announced the launch event.",
            "The Galaxy S26 is available in India.",
            "Samsung released a company announcement.",
            "More information will be released next week.",
            "The company announced a new event.",
            "Samsung announced its quarterly results.",
            "The company released a general announcement.",
            "Samsung announced a new product launch event.",
            "The company published a general update.",
            "More details will be announced later.",
        ],
    }

    # =========================================================
    # CONFIGURATION
    # =========================================================

    CONFIDENCE_THRESHOLD = 0.50

    DOMAIN_SIGNAL_BOOST = 0.10

    # Strong domain signals.
    STRONG_SECURITY_BOOST = 0.20
    STRONG_COMPLAINT_BOOST = 0.10
    STRONG_COMPETITOR_BOOST = 0.15

    def __init__(self):

        self.model = self._load_model()

        self.topic_embeddings = (
            self._build_topic_embeddings()
        )

    # =========================================================
    # MODEL LOADING
    # =========================================================

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_model():

        print(
            f"Loading topic embedding model: "
            f"{TopicService.MODEL_NAME}"
        )

        return SentenceTransformer(
            TopicService.MODEL_NAME
        )

    # =========================================================
    # BUILD TOPIC PROTOTYPES
    # =========================================================

    def _build_topic_embeddings(self):

        topic_embeddings = {}

        for topic, examples in self.TOPIC_EXAMPLES.items():

            embeddings = self.model.encode(
                examples,
                normalize_embeddings=True,
            )

            prototype = np.mean(
                embeddings,
                axis=0,
            )

            prototype = (
                prototype
                / np.linalg.norm(prototype)
            )

            topic_embeddings[topic] = prototype

        return topic_embeddings

    # =========================================================
    # TOPIC ANALYSIS
    # =========================================================

    def analyze(self, text: str) -> dict:

        text = text.strip()

        if not text:

            return {
                "topic": "Other",
                "confidence": 0.0,
            }

        normalized_text = self._normalize_text(
            text
        )

        # -----------------------------------------------------
        # Generate embedding
        # -----------------------------------------------------

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        # -----------------------------------------------------
        # Semantic similarity
        # -----------------------------------------------------

        scores = {}

        for topic, prototype in self.topic_embeddings.items():

            score = float(
                np.dot(
                    embedding,
                    prototype,
                )
            )

            scores[topic] = score

        # -----------------------------------------------------
        # Domain-specific signals
        # -----------------------------------------------------

        signal_topics = self._detect_domain_topics(
            text
        )

        for topic in signal_topics:

            if topic in scores:

                scores[topic] += (
                    self.DOMAIN_SIGNAL_BOOST
                )

        # -----------------------------------------------------
        # Strong security signals
        # -----------------------------------------------------

        if self._contains_any(
            normalized_text,
            self.SECURITY_STRONG_SIGNALS,
        ):

            scores["Security"] += (
                self.STRONG_SECURITY_BOOST
            )

        # -----------------------------------------------------
        # Strong complaint signals
        # -----------------------------------------------------

        if self._contains_any(
            normalized_text,
            self.COMPLAINT_STRONG_SIGNALS,
        ):

            # -------------------------------------------------
            # Important distinction:
            #
            # "I am disappointed with my phone"
            #       -> Complaints
            #
            # "The display quality is disappointing"
            #       -> Quality
            #
            # Topic and sentiment are separate dimensions.
            # -------------------------------------------------

            quality_context = self._contains_any(
                normalized_text,
                self.QUALITY_CONTEXT_SIGNALS,
            )

            if not quality_context:

                scores["Complaints"] += (
                    self.STRONG_COMPLAINT_BOOST
                )

        # -----------------------------------------------------
        # Strong competitor comparison signals
        # -----------------------------------------------------

        if self._contains_any(
            normalized_text,
            self.COMPETITOR_COMPARISON_SIGNALS,
        ):

            scores["Competitors"] += (
                self.STRONG_COMPETITOR_BOOST
            )

        # -----------------------------------------------------
        # Select topic
        # -----------------------------------------------------

        predicted_topic = max(
            scores,
            key=scores.get,
        )

        confidence = scores[
            predicted_topic
        ]

        # -----------------------------------------------------
        # Clamp confidence
        # -----------------------------------------------------

        confidence = max(
            -1.0,
            min(
                confidence,
                1.0,
            ),
        )

        # -----------------------------------------------------
        # Low-confidence fallback
        # -----------------------------------------------------

        if confidence < self.CONFIDENCE_THRESHOLD:

            predicted_topic = "Other"

        return {
            "topic": predicted_topic,
            "confidence": round(
                confidence,
                4,
            ),
        }

    # =========================================================
    # DOMAIN SIGNALS
    # =========================================================

    SECURITY_STRONG_SIGNALS = {
        "attack",
        "attacked",
        "attacker",
        "attackers",
        "hack",
        "hacked",
        "hacker",
        "hackers",
        "exploit",
        "exploited",
        "exploits",
        "vulnerability",
        "vulnerabilities",
        "security flaw",
        "security issue",
        "security vulnerability",
        "zero day",
        "zero-day",
        "zero click",
        "zero-click",
        "permission bypass",
        "cyber attack",
        "compromised",
        "malware",
        "security patch",
    }

    COMPLAINT_STRONG_SIGNALS = {
        "disappointed",
        "disappointing",
        "extremely disappointed",
        "very disappointed",
        "unhappy",
        "frustrated",
        "regret buying",
        "does not work",
        "doesn't work",
        "stopped working",
        "serious problem",
        "serious issue",
        "keeps crashing",
        "keeps freezing",
    }

    # ---------------------------------------------------------
    # Quality context
    #
    # These signals indicate that negative language is describing
    # a specific quality attribute rather than expressing a
    # general complaint.
    # ---------------------------------------------------------

    QUALITY_CONTEXT_SIGNALS = {
        "build quality",
        "hardware quality",
        "camera quality",
        "display quality",
        "battery quality",
        "image quality",
        "screen quality",
        "sound quality",
        "audio quality",
        "performance quality",
        "material quality",
        "poor quality",
        "high quality",
        "low quality",
        "well built",
        "poor build",
        "bad build",
    }

    # IMPORTANT:
    #
    # Product names such as "iPhone" and "Pixel" are deliberately
    # NOT included here.
    #
    # A competitor topic requires comparison context.
    #
    COMPETITOR_COMPARISON_SIGNALS = {
        "better than",
        "worse than",
        "compared with",
        "compared to",
        "compare with",
        "compare to",
        "versus",
        " vs ",
        "instead of",
        "over the iphone",
        "over iphone",
        "over the pixel",
        "choose the iphone",
        "choose iphone",
        "choose the pixel",
        "choose pixel",
        "competing with",
        "competing against",
        "competes with",
        "competes against",
        "competitor",
        "competitors",
        "alternative to",
        "prefer the iphone",
        "prefer iphone",
        "prefer the pixel",
        "prefer pixel",
    }

    # =========================================================
    # DOMAIN TOPIC DETECTION
    # =========================================================

    @classmethod
    def _detect_domain_topics(
        cls,
        text: str,
    ) -> list[str]:

        normalized_text = cls._normalize_text(
            text
        )

        detected_topics = []

        # -----------------------------------------------------
        # SECURITY
        # -----------------------------------------------------

        if cls._contains_any(
            normalized_text,
            cls.SECURITY_STRONG_SIGNALS,
        ):

            detected_topics.append(
                "Security"
            )

        # -----------------------------------------------------
        # PRICING
        # -----------------------------------------------------

        if cls._contains_any(
            normalized_text,
            {
                "price",
                "pricing",
                "cost",
                "expensive",
                "cheaper",
                "cheap",
                "discount",
                "discounted",
                "sale",
                "price increase",
                "price increased",
                "price dropped",
                "price decreased",
                "cost increased",
                "cost decreased",
                "raised the price",
                "lowered the price",
            },
        ):

            detected_topics.append(
                "Pricing"
            )

        # -----------------------------------------------------
        # CUSTOMER SERVICE
        # -----------------------------------------------------

        if cls._contains_any(
            normalized_text,
            {
                "customer support",
                "customer service",
                "customer care",
                "support team",
                "support representative",
                "contacted support",
                "contacted samsung support",
                "support refused",
                "support helped",
            },
        ):

            detected_topics.append(
                "Customer service"
            )

        # -----------------------------------------------------
        # COMPETITORS
        # -----------------------------------------------------

        if cls._contains_any(
            normalized_text,
            cls.COMPETITOR_COMPARISON_SIGNALS,
        ):

            detected_topics.append(
                "Competitors"
            )

        # -----------------------------------------------------
        # FEATURES
        # -----------------------------------------------------

        if cls._contains_any(
            normalized_text,
            {
                "feature",
                "features",
                "supports",
                "support for",
                "connectivity",
                "capability",
                "capabilities",
                "functionality",
                "ai editing",
                "camera mode",
                "satellite connectivity",
                "virtualization",
            },
        ):

            detected_topics.append(
                "Features"
            )

        # -----------------------------------------------------
        # QUALITY
        # -----------------------------------------------------

        if cls._contains_any(
            normalized_text,
            {
                "build quality",
                "hardware quality",
                "durability",
                "reliability",
                "overheats",
                "overheating",
                "performance problem",
                "performance problems",
                "battery problem",
                "battery problems",
                "camera quality",
                "display quality",
                "hardware problem",
                "hardware problems",
                "well built",
                "high quality",
            },
        ):

            detected_topics.append(
                "Quality"
            )

        # -----------------------------------------------------
        # COMPLAINTS
        # -----------------------------------------------------

        if cls._contains_any(
            normalized_text,
            cls.COMPLAINT_STRONG_SIGNALS,
        ):

            detected_topics.append(
                "Complaints"
            )

        return detected_topics

    # =========================================================
    # UTILITY METHODS
    # =========================================================

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:

        text = text.lower()

        return " ".join(
            text.split()
        )

    @classmethod
    def _contains_any(
        cls,
        text: str,
        signals: set[str],
    ) -> bool:

        for signal in signals:

            normalized_signal = (
                cls._normalize_text(
                    signal
                )
            )

            if normalized_signal in text:

                return True

        return False