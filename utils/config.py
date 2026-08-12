from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

import yaml

VALID_SPECIALS = frozenset(
    {"full_straight", "low_straight", "high_straight"}
)


@dataclass(frozen=True, slots=True)
class RuleSet:
    name: str
    num_dice: int
    target_score: int
    min_first_bank: int
    final_round: bool
    hot_dice: bool
    singles: Mapping[int, int]
    triple: Mapping[int, int]
    multiplier: Mapping[int, int]
    specials: Mapping[str, int] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "RuleSet":
        raw = yaml.safe_load(Path(path).read_text())

        enabled = set(raw["specials"]["enabled"])
        unknown = enabled - VALID_SPECIALS
        if unknown:
            raise ValueError(f"unknown specials: {sorted(unknown)}")

        cfg = cls(
            name=raw["name"],
            num_dice=raw["num_dice"],
            target_score=raw["target_score"],
            min_first_bank=raw["min_first_bank"],
            final_round=raw["final_round"],
            hot_dice=raw["hot_dice"],
            singles={int(k): v for k, v in raw["singles"].items()},
            triple={int(k): v for k, v in raw["n_of_a_kind"]["triple"].items()},
            multiplier={
                int(k): v for k, v in raw["n_of_a_kind"]["multiplier"].items()
            },
            specials={
                k: raw["specials"]["values"][k] for k in sorted(enabled)
            },
        )
        cfg.validate()
        return cfg

    def validate(self) -> None:
        if self.num_dice < 1:
            raise ValueError("num_dice must be positive")
        if not set(self.triple) == {1, 2, 3, 4, 5, 6}:
            raise ValueError("triple values must cover all six faces")
        missing = set(range(3, self.num_dice + 1)) - set(self.multiplier)
        if missing:
            raise ValueError(f"no multiplier for set sizes {sorted(missing)}")
        if "full_straight" in self.specials and self.num_dice < 6:
            raise ValueError("straight requires six dice")

    def n_of_a_kind_score(self, face: int, count: int) -> int:
        return self.triple[face] * self.multiplier[count]