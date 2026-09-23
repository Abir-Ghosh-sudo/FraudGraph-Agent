from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SimilarityResult:
    """Similarity between two investigation feature sets."""

    score: float
    matched_features: tuple[str, ...]
    compared_features: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "score": self.score,
            "matched_features": list(self.matched_features),
            "compared_features": list(self.compared_features),
        }


class CaseSimilarity:
    """Calculate deterministic similarity between investigation cases."""

    def compare(
        self,
        left: dict[str, object],
        right: dict[str, object],
    ) -> SimilarityResult:
        left_features = self._normalise(left)
        right_features = self._normalise(right)

        if not left_features and not right_features:
            return SimilarityResult(
                score=1.0,
                matched_features=(),
                compared_features=(),
            )

        compared = tuple(
            sorted(
                set(left_features) | set(right_features)
            )
        )

        matched = tuple(
            sorted(
                feature
                for feature in compared
                if self._values_match(
                    left_features.get(feature),
                    right_features.get(feature),
                )
            )
        )

        if not compared:
            score = 0.0
        else:
            score = len(matched) / len(compared)

        return SimilarityResult(
            score=round(score, 6),
            matched_features=matched,
            compared_features=compared,
        )

    def score(
        self,
        left: dict[str, object],
        right: dict[str, object],
    ) -> float:
        return self.compare(left, right).score

    def compare_findings(
        self,
        left: Iterable[str],
        right: Iterable[str],
    ) -> SimilarityResult:
        left_set = self._normalise_set(left)
        right_set = self._normalise_set(right)

        union = left_set | right_set
        intersection = left_set & right_set

        score = (
            len(intersection) / len(union)
            if union
            else 1.0
        )

        return SimilarityResult(
            score=round(score, 6),
            matched_features=tuple(sorted(intersection)),
            compared_features=tuple(sorted(union)),
        )

    def compare_entities(
        self,
        left: Iterable[str],
        right: Iterable[str],
    ) -> SimilarityResult:
        return self.compare_findings(left, right)

    def _normalise(
        self,
        features: dict[str, object],
    ) -> dict[str, object]:
        return {
            str(key).strip().lower(): value
            for key, value in features.items()
            if str(key).strip()
        }

    def _normalise_set(
        self,
        values: Iterable[str],
    ) -> set[str]:
        return {
            str(value).strip().lower()
            for value in values
            if str(value).strip()
        }

    def _values_match(
        self,
        left: object,
        right: object,
    ) -> bool:
        if left is None or right is None:
            return False

        if isinstance(left, (list, tuple, set)):
            left_values = self._normalise_set(
                str(item) for item in left
            )
            right_values = self._normalise_set(
                str(item) for item in (
                    right
                    if isinstance(right, (list, tuple, set))
                    else [right]
                )
            )
            return bool(left_values & right_values)

        if isinstance(right, (list, tuple, set)):
            return self._values_match(right, left)

        return str(left).strip().lower() == str(right).strip().lower()