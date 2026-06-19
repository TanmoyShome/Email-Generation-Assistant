import re
from typing import Dict


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.split(r"[.!?]+", text) if sentence.strip()]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 3)))


class Metric:
    name = "metric"
    description = "Custom email quality metric."

    def score(self, generated: str, context: Dict) -> float:
        raise NotImplementedError


class FactRecallMetric(Metric):
    name = "fact_recall"
    description = "Measures how many required key facts are present in the email."

    def score(self, generated: str, context: Dict) -> float:
        facts = context.get("facts", [])
        if not facts:
            return 1.0

        email_words = _words(generated)
        matched_facts = 0

        for fact in facts:
            fact_words = _words(fact)
            if not fact_words:
                matched_facts += 1
                continue

            overlap = len(fact_words & email_words) / len(fact_words)
            important_tokens = {
                token for token in fact_words if token.isdigit() or len(token) > 4
            }
            important_overlap = (
                len(important_tokens & email_words) / len(important_tokens)
                if important_tokens
                else overlap
            )

            if overlap >= 0.55 and important_overlap >= 0.5:
                matched_facts += 1

        return _clamp(matched_facts / len(facts))


class ToneAccuracyMetric(Metric):
    name = "tone_accuracy"
    description = "Checks whether wording matches the requested email tone."

    tone_markers = {
        "formal": {"dear", "sincerely", "regards", "please", "appreciate", "kindly"},
        "direct": {"please", "confirm", "provide", "required", "deadline"},
        "casual": {"hi", "thanks", "happy", "glad", "best"},
        "urgent": {"urgent", "immediately", "today", "critical", "prompt", "asap"},
        "empathetic": {"sorry", "understand", "appreciate", "support", "apologize"},
        "accountable": {"responsibility", "resolved", "ensure", "apologize", "sorry"},
        "proactive": {"next", "share", "follow", "available", "schedule"},
        "warm": {"thank", "grateful", "appreciate", "wonderful", "support"},
        "appreciative": {"thank", "grateful", "appreciate", "invaluable", "support"},
        "concise": {"brief", "quick", "summary", "confirm", "needed"},
        "professional": {"dear", "please", "regards", "appreciate", "thank"},
    }

    def score(self, generated: str, context: Dict) -> float:
        requested_tone = context.get("tone", "").lower()
        email_words = _words(generated)
        requested_categories = [
            tone for tone in self.tone_markers if tone in requested_tone
        ]

        if not requested_categories:
            return 0.75

        category_scores = []
        for tone in requested_categories:
            markers = self.tone_markers[tone]
            category_scores.append(len(markers & email_words) / len(markers))

        return _clamp(0.45 + max(category_scores))


class ConcisenessFluencyMetric(Metric):
    name = "conciseness_fluency"
    description = "Scores concise length, readable sentence flow, and basic email fluency."

    def score(self, generated: str, context: Dict) -> float:
        words = generated.split()
        sentences = _sentences(generated)
        word_count = len(words)
        avg_sentence_length = word_count / max(len(sentences), 1)

        checks = [
            45 <= word_count <= 220,
            8 <= avg_sentence_length <= 28,
            bool(re.search(r"^subject\s*:", generated, re.I | re.M)),
            bool(re.search(r"\b(hi|hello|dear)\b", generated, re.I)),
            bool(re.search(r"\b(sincerely|regards|best|thank you|thanks)\b", generated, re.I)),
            not re.search(r"\s{3,}", generated),
            generated.strip().endswith((".", "!", "]", ")")) or "\n" in generated.strip(),
        ]

        return _clamp(sum(checks) / len(checks))


class Evaluator:
    def __init__(self, metrics=None):
        self.metrics = metrics or [
            FactRecallMetric(),
            ToneAccuracyMetric(),
            ConcisenessFluencyMetric(),
        ]

    def evaluate(self, generated: str, context: Dict) -> Dict[str, float]:
        scores = {metric.name: metric.score(generated, context) for metric in self.metrics}
        scores["overall"] = _clamp(sum(scores.values()) / len(scores))
        return scores

    def definitions(self) -> Dict[str, str]:
        return {metric.name: metric.description for metric in self.metrics}
