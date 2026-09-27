"""Deterministic confidence routing independent of any model framework."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Normalized result returned by a visual recognition tool."""

    model: str
    label: str
    confidence: float
    latency_ms: float = 0.0
    metadata: Mapping[str, str | int | float | bool] | None = None

    def __post_init__(self) -> None:
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if not self.label.strip():
            raise ValueError("label must not be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.latency_ms < 0:
            raise ValueError("latency_ms must not be negative")


@dataclass(frozen=True, slots=True)
class RouteDecision:
    """Final routing outcome, including safe abstention."""

    label: str | None
    confidence: float
    used_models: tuple[str, ...]
    abstained: bool
    reason: str


class ConfidenceRouter:
    """Resolve primary and verifier results with explicit, testable rules."""

    def __init__(
        self,
        accept_threshold: float = 0.75,
        verification_threshold: float = 0.65,
        conflict_margin: float = 0.20,
    ) -> None:
        for name, value in {
            "accept_threshold": accept_threshold,
            "verification_threshold": verification_threshold,
            "conflict_margin": conflict_margin,
        }.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        self.accept_threshold = accept_threshold
        self.verification_threshold = verification_threshold
        self.conflict_margin = conflict_margin

    def resolve(
        self,
        primary: ToolResult,
        verifier: ToolResult | None = None,
    ) -> RouteDecision:
        """Accept, verify, select a clear winner, or abstain."""

        if primary.confidence >= self.accept_threshold:
            return RouteDecision(
                label=primary.label,
                confidence=primary.confidence,
                used_models=(primary.model,),
                abstained=False,
                reason="primary confidence met the acceptance threshold",
            )

        if verifier is None:
            return RouteDecision(
                label=None,
                confidence=primary.confidence,
                used_models=(primary.model,),
                abstained=True,
                reason="primary confidence was low and no verifier result was available",
            )

        used_models = (primary.model, verifier.model)
        if primary.label == verifier.label:
            combined_confidence = (primary.confidence + verifier.confidence) / 2.0
            if combined_confidence >= self.verification_threshold:
                return RouteDecision(
                    label=primary.label,
                    confidence=combined_confidence,
                    used_models=used_models,
                    abstained=False,
                    reason="primary and verifier agreed",
                )
            return RouteDecision(
                label=None,
                confidence=combined_confidence,
                used_models=used_models,
                abstained=True,
                reason="models agreed but their combined confidence remained low",
            )

        winner = max((primary, verifier), key=lambda result: result.confidence)
        confidence_gap = abs(primary.confidence - verifier.confidence)
        if (
            winner.confidence >= self.verification_threshold
            and confidence_gap >= self.conflict_margin
        ):
            return RouteDecision(
                label=winner.label,
                confidence=winner.confidence,
                used_models=used_models,
                abstained=False,
                reason="models disagreed but one result won by the configured margin",
            )

        return RouteDecision(
            label=None,
            confidence=winner.confidence,
            used_models=used_models,
            abstained=True,
            reason="models disagreed without a decisive confidence margin",
        )
