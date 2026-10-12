from __future__ import annotations

from math import sqrt


class Retriever:
    @staticmethod
    def cosine_similarity(left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        left_norm = sqrt(sum(v * v for v in left))
        right_norm = sqrt(sum(v * v for v in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        dot_product = sum(a * b for a, b in zip(left, right))
        return dot_product / (left_norm * right_norm)
