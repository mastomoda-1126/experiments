"""
school_ecosystem_sim_safe.py

A tongue-in-cheek *fictional* simulation of:
- A protected school ecosystem (not any real school)
- An external world with strong selection pressure (AI, DX, macro change)
- Legacy actors surviving inside while the ecosystem itself quietly degrades
- Burned-out staff choosing their own opportunity cost (stay vs leave)
- Organization-level suppression that sometimes kills seeds of change
  from high adapters and forces systemic opportunity costs on everyone
- A few high-adaptability students who become "future hope"
- A legacy organization relying on external systems instead of analyzing
  internal infra & talent, causing:
    * wasted monetary cost
    * rising learning cost
    * increasing system complexity
    * rising workload
- Productivity falling as useless systems are added
- True efficiency existing but not being what the organization actually evaluates

Safer design in this version:
- No deterministic “everyone who leaves becomes a casualty” logic.
- External world has explicit constraints (budget, regulation, demographics).
- Suppression is a *level* (0–1), not a binary good/evil flag.
- Random noise is injected into transitions to avoid “fate is fixed”.
- Dynamics (“physics”) are separated from value judgements (stakeholder utilities).
- Future hope for students is determined probabilistically, with:
    * a small but non-zero chance even in negative scenarios
    * a higher probability in positive scenarios

Note:
- This is a neutral systems-toy, not an ideological statement.
- All schools and people inside it are fictional.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Literal, Tuple, Optional
import random
import math


Role = Literal["teacher", "admin", "student"]
OpportunityChoice = Literal["none", "stay_inside", "leave_outside"]
ChangeAttitude = Literal["resist", "neutral", "support"]


# -------------------------
# Individual actors
# -------------------------

@dataclass
class Actor:
    name: str
    role: Role
    os_version: str          # e.g. "LegacyOS-1985", "HighAdaptOS-2025"
    adaptability: float      # 0.0–1.0
    protected: bool = True   # protected from market selection

    # メンタル / 状態
    change_attitude: ChangeAttitude = "neutral"
    burned_out: bool = False
    has_left_system: bool = False

    # 学校外の人生
    rebooted_outside: bool = False
    casualty_of_system: bool = False

    # 機会費用（その人が払う「代償」の抽象値）
    opportunity_cost: float = 0.0
    opportunity_choice: OpportunityChoice = "none"

    # 学生用: future hope に関する情報（報告用）
    future_hope_probability: float = 0.0
    is_future_hope: bool = False

    def __repr__(self) -> str:
        status = []
        if self.casualty_of_system:
            status.append("casualty")
        elif self.rebooted_outside:
            status.append("rebooted")
        elif self.has_left_system:
            status.append("left")
        elif self.burned_out:
            status.append("burned_out")
        else:
            status.append("in_system")

        if self.opportunity_choice != "none":
            status.append(f"opp:{self.opportunity_choice}")

        return (
            f"<{self.role}:{self.name} os={self.os_version} "
            f"adapt={self.adaptability:.2f} "
            f"oc={self.opportunity_cost:.2f} "
            f"{'/'.join(status)}>"
        )


# -------------------------
# External world
# -------------------------

@dataclass
class ExternalWorld:
    """
    Represents the outside environment where AI, DX, and macro change
    create real selection pressure.
    """

    selection_pressure: float = 0.8  # 0.0–1.0 (high = harsh)
    ai_shift_speed: float = 0.9      # speed of paradigm shift

    def required_threshold(self) -> float:
        """
        Required "effective adaptability" to survive outside,
        taking into account AI shift.
        """
        return self.selection_pressure + (self.ai_shift_speed * 0.1)

    def base_effective_adaptability(self, actor: Actor) -> float:
        """
        Compute effective adaptability before burnout penalties.
        """
        base = actor.adaptability

        # Legacy OS is just slightly disadvantaged, not doomed
        if "LegacyOS" in actor.os_version:
            base -= 0.15

        # High-adapt "OS" patterns – generic, not about any one person
        if any(tag in actor.os_version for tag in ("HighAdaptOS", "MasOS", "LLM-aware")):
            base += 0.15

        # Change attitude has a modest effect
        if actor.change_attitude == "support":
            base += 0.05
        elif actor.change_attitude == "resist":
            base -= 0.05

        return base

    def evaluate_actor(self, actor: Actor) -> bool:
        """
        Returns True if the actor can *likely* survive in the external world
        (ignoring burnout). This is still a simplified check.

        NOTE:
        - This deterministic check is mainly used for staff and as a baseline.
        - Students' "future hope" is computed with an additional probabilistic
          layer that accounts for the school environment.
        """
        base = self.base_effective_adaptability(actor)
        required = self.required_threshold()
        return base >= required

    def reintegration_outcome(self, actor: Actor) -> str:
        """
        Determine whether a leaving actor can successfully reboot outside
        or becomes a casualty of the system.

        This is *not* deterministic fate:
        - burnout applies an extra penalty
        - then random noise is added
        """
        base = self.base_effective_adaptability(actor)
        if actor.burned_out:
            base -= 0.2

        # small random wiggle to avoid fatalism
        base += random.uniform(-0.1, 0.1)

        required = self.required_threshold()
        return "rebooted" if base >= required else "casualty"


# -------------------------
# Macro constraints (budget, regulation, demographics)
# -------------------------

@dataclass
class EnvironmentConstraints:
    budget_pressure: float = 0.5        # 0–1, high = little money
    regulation_rigidity: float = 0.5    # 0–1, high = reforms are hard
    demographic_pressure: float = 0.5   # 0–1, high = student pool shrinking etc.


# -------------------------
# Dynamics coefficients (value-neutral "physics" parameters)
# -------------------------

@dataclass
class DynamicsCoefficients:
    """
    Coefficients that define how strongly each factor influences
    burnout, productivity, and efficiency.

    These are factored out so that different value systems can reuse
    the same structural dynamics with different parameter sets.
    """

    # Burnout drivers
    infra_to_burnout: float = 0.1
    dxclarity_to_burnout: float = 0.1
    workload_to_burnout: float = 0.05
    complexity_to_burnout: float = 0.05
    trustlack_to_burnout: float = 0.05
    personalization_to_burnout: float = 0.05

    # Burnout relief
    llm_relief_to_burnout: float = 0.04
    ai_service_relief_to_burnout: float = 0.03

    # Productivity drivers (negative contributions)
    external_system_to_productivity: float = 0.03
    complexity_to_productivity: float = 0.04
    workload_to_productivity: float = 0.02
    infra_bad_to_productivity: float = 0.02
    fragmentation_to_productivity: float = 0.03
    personalization_to_productivity: float = 0.03

    # Productivity gains
    llm_to_productivity: float = 0.05
    ai_access_to_productivity: float = 0.03

    # Base efficiency components
    base_eff_infra_weight: float = 0.4
    base_eff_dxclarity_weight: float = 0.3
    suppression_bonus_to_eff: float = 0.1    # added when suppression is low
    llm_to_efficiency: float = 0.1
    db_to_efficiency: float = 0.05
    portal_to_efficiency: float = 0.05
    personalization_to_efficiency: float = 0.05


# -------------------------
# Stakeholder utilities (explicit "value" layer)
# -------------------------

@dataclass
class StakeholderUtility:
    """
    Simple linear utility function over SchoolEcosystem state.

    This is the "value" layer: different stakeholders can define
    different weights over the same underlying state variables.
    """
    name: str
    weights: dict[str, float]

    def score(self, school: "SchoolEcosystem") -> float:
        s = 0.0
        for attr, w in self.weights.items():
            v = getattr(school, attr)
            s += w * v
        return s


# -------------------------
# School ecosystem ("physics" layer)
# -------------------------

@dataclass
class SchoolEcosystem:
    """
    A protected ecosystem where legacy OS can survive longer than they would
    in the external world… but the ecosystem itself quietly degrades.

    This version:
    - suppression is a float 0–1 (suppression_level)
    - environment constraints explicitly shape what is feasible
    - random noise is applied so nothing is 100% deterministic
    - dynamics coefficients are separated from the value layer
    """

    name: str
    env: EnvironmentConstraints
    dynamics: DynamicsCoefficients = field(default_factory=DynamicsCoefficients)

    actors: List[Actor] = field(default_factory=list)

    infrastructure_health: float = 0.4  # 0.0–1.0
    dx_clarity: float = 0.1             # DX vision / roadmap clarity
    burnout_index: float = 0.0
    student_exit_rate: float = 0.0
    recruitment_difficulty: float = 0.3
    years_simulated: int = 0

    # Organization-level suppression of change (0–1)
    suppression_level: float = 0.8
    systemic_opportunity_cost: float = 0.0
    change_seeds_planted: int = 0
    change_seeds_suppressed: int = 0

    # External-system dependent DXごっこ
    external_system_dependency: float = 0.0
    external_spend: float = 0.0
    learning_cost_index: float = 0.0
    system_complexity: float = 0.3
    workload_index: float = 0.5

    # Productivity & efficiency
    productivity_index: float = 0.7
    efficiency_index_true: float = 0.4
    efficiency_index_recognized: float = 0.1

    # Strategy & marketing view
    has_swot: bool = False
    strategic_consistency: float = 0.2
    change_request_intensity: float = 0.3
    change_rejection_rate: float = 0.6
    rhetorical_change_slogans: int = 0

    # Education assets & competitiveness
    educational_asset_index: float = 0.1
    central_repository_level: float = 0.0
    student_learning_efficiency: float = 0.4
    competitor_gap_index: float = 0.1

    # Innovative infra & local LLM
    innovation_potential_index: float = 0.0
    local_llm_infra_level: float = 0.0
    ai_service_quality_index: float = 0.0
    ai_accessibility_index: float = 0.0

    # Portal / DB / PM / Trust
    portal_maturity: float = 0.1
    database_foundation: float = 0.1
    process_fragmentation_index: float = 0.7
    pm_capability: float = 0.2
    grand_design_clarity: float = 0.1
    leadership_trust_battery: float = 0.4
    info_transparency: float = 0.3

    # Task personalization / 属人性
    task_personalization_index: float = 0.85

    # Randomness level
    randomness: float = 0.05  # 0 = fully deterministic

    def add_actor(self, actor: Actor) -> None:
        self.actors.append(actor)

    # ---------- small helper ----------

    def _noise(self, scale: float) -> float:
        if self.randomness <= 0.0 or scale <= 0.0:
            return 0.0
        return random.uniform(-scale, scale) * self.randomness

    # ---------- internal dynamics ----------

    def _tick_infrastructure(self) -> None:
        self.infrastructure_health += -0.03 + self._noise(0.02)
        self.infrastructure_health = max(0.0, min(1.0, self.infrastructure_health))

    def _tick_dx_clarity(self) -> None:
        self.dx_clarity += -0.02 + self._noise(0.02)
        self.dx_clarity = max(0.0, min(1.0, self.dx_clarity))

    def _tick_strategy_layer(self) -> None:
        strong_suppression = self.suppression_level > 0.6

        if not self.has_swot and strong_suppression:
            self.change_request_intensity += 0.03 * self.suppression_level
            self.change_rejection_rate += 0.02 * self.suppression_level
            self.strategic_consistency -= 0.03 * self.suppression_level
            self.rhetorical_change_slogans += 1
            self.burnout_index += 0.02 * self.suppression_level
            self.systemic_opportunity_cost += 0.1 * self.suppression_level

        if self.has_swot and self.suppression_level < 0.4 and self.dx_clarity > 0.5:
            self.change_request_intensity -= 0.02
            self.change_rejection_rate -= 0.03
            self.strategic_consistency += 0.05

        for attr in ("change_request_intensity", "change_rejection_rate", "strategic_consistency"):
            v = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, v)))

    def _tick_portal_and_db(self) -> None:
        # Negative path
        if (
            self.portal_maturity < 0.4
            and self.database_foundation < 0.4
            and self.dx_clarity < 0.3
        ):
            self.process_fragmentation_index += 0.04 + self._noise(0.02)
            self.workload_index += 0.02
            self.system_complexity += 0.03
            self.student_learning_efficiency -= 0.02
            self.productivity_index -= 0.01
            self.task_personalization_index += 0.03

        # Positive path (regulation can slow it)
        if (
            self.suppression_level < 0.4
            and self.dx_clarity > 0.5
            and self.infrastructure_health > 0.4
        ):
            factor = 1.0 - 0.5 * self.env.regulation_rigidity
            if factor > 0.0:
                self.portal_maturity += 0.05 * factor
                self.database_foundation += 0.05 * factor
                self.process_fragmentation_index -= 0.05 * factor
                self.educational_asset_index += 0.03 * factor
                self.task_personalization_index -= 0.05 * factor

        for attr in (
            "portal_maturity", "database_foundation", "process_fragmentation_index",
            "student_learning_efficiency", "productivity_index",
            "task_personalization_index", "workload_index", "system_complexity",
            "educational_asset_index"
        ):
            v = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, v)))

    def _tick_pm_and_design(self) -> None:
        # Negative PM world
        if (
            self.pm_capability < 0.4
            and self.grand_design_clarity < 0.4
            and self.change_request_intensity > 0.4
            and self.change_rejection_rate > 0.5
        ):
            self.burnout_index += 0.03
            self.productivity_index -= 0.02
            self.leadership_trust_battery -= 0.03
            self.strategic_consistency -= 0.02

        # Positive PM world
        if (
            self.pm_capability > 0.6
            and self.grand_design_clarity > 0.6
            and self.dx_clarity > 0.5
            and self.suppression_level < 0.4
        ):
            self.burnout_index -= 0.02
            self.productivity_index += 0.03
            self.leadership_trust_battery += 0.05
            self.strategic_consistency += 0.03

        for attr in (
            "burnout_index", "productivity_index", "leadership_trust_battery",
            "strategic_consistency"
        ):
            v = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, v)))

    def _tick_change_dynamics(self) -> None:
        high_adapters = [
            a for a in self.actors
            if a.role in ("teacher", "admin") and a.adaptability >= 0.7
        ]
        seeds = len(high_adapters)
        if seeds == 0:
            return

        self.change_seeds_planted += seeds
        s = self.suppression_level

        if s > 0.5:
            self.change_seeds_suppressed += seeds
            self.systemic_opportunity_cost += seeds * 0.4 * s
            self.burnout_index += 0.04 * s
            self.dx_clarity -= 0.02 * s

            for stud in self.actors:
                if stud.role == "student":
                    stud.adaptability -= 0.01 * s
                    stud.adaptability = max(0.0, stud.adaptability)
        else:
            openness = 1.0 - s
            self.infrastructure_health += 0.04 * openness
            self.dx_clarity += 0.08 * openness
            self.burnout_index -= 0.02 * openness

        self.dx_clarity = max(0.0, min(1.0, self.dx_clarity))
        self.infrastructure_health = max(0.0, min(1.0, self.infrastructure_health))
        self.burnout_index = max(0.0, min(1.0, self.burnout_index))

    def _tick_education_assets(self) -> None:
        # Negative path
        if (
            self.educational_asset_index < 0.5
            and self.central_repository_level < 0.3
            and self.dx_clarity < 0.3
        ):
            self.student_learning_efficiency -= 0.03
            self.competitor_gap_index += 0.05

        # Positive path (budget can slow it)
        if self.suppression_level < 0.4 and self.dx_clarity > 0.5:
            factor = 1.0 - 0.5 * self.env.budget_pressure
            if factor > 0.0:
                self.educational_asset_index += 0.05 * factor
                self.central_repository_level += 0.05 * factor
                self.student_learning_efficiency += 0.04 * factor
                self.competitor_gap_index -= 0.03 * factor

        # Local LLM infra boosts learning efficiency & reduces gap
        if self.local_llm_infra_level > 0.0:
            boost = 0.03 * self.local_llm_infra_level
            self.student_learning_efficiency += boost
            self.competitor_gap_index -= 0.02 * self.local_llm_infra_level

        for attr in (
            "student_learning_efficiency", "competitor_gap_index",
            "educational_asset_index", "central_repository_level"
        ):
            v = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, v)))

    def _tick_innovation(self) -> None:
        ready_for_innovation = (
            self.educational_asset_index >= 0.5
            and self.central_repository_level >= 0.5
            and self.dx_clarity >= 0.6
            and self.suppression_level < 0.4
            and self.infrastructure_health >= 0.5
            and self.env.budget_pressure < 0.8
        )

        if ready_for_innovation:
            self.innovation_potential_index += 0.05
            self.innovation_potential_index = min(1.0, self.innovation_potential_index)

            budget_factor = 1.0 - 0.5 * self.env.budget_pressure
            if budget_factor > 0:
                self.local_llm_infra_level += (
                    0.04 * self.innovation_potential_index * budget_factor
                )
            self.local_llm_infra_level = min(1.0, max(0.0, self.local_llm_infra_level))

            self.ai_service_quality_index += 0.05 * self.local_llm_infra_level
            self.ai_accessibility_index += 0.04 * self.local_llm_infra_level
        else:
            decay = 0.02
            if self.suppression_level > 0.6 or self.dx_clarity < 0.3:
                self.innovation_potential_index -= decay

            self.local_llm_infra_level -= 0.01
            self.ai_service_quality_index -= 0.01
            self.ai_accessibility_index -= 0.01

        for attr in (
            "innovation_potential_index", "local_llm_infra_level",
            "ai_service_quality_index", "ai_accessibility_index"
        ):
            v = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, v)))

    def _tick_external_systems(self) -> None:
        if self.infrastructure_health < 0.6 and self.dx_clarity < 0.3:
            self.external_system_dependency += 0.05
            self.external_spend += 0.10
            self.learning_cost_index += 0.05
            self.system_complexity += 0.04
            self.workload_index += 0.03
            self.infrastructure_health += 0.01
            self.burnout_index += 0.02

        if self.suppression_level < 0.4 and self.dx_clarity > 0.5:
            self.external_system_dependency -= 0.03
            self.system_complexity -= 0.03
            self.workload_index -= 0.02
            self.learning_cost_index -= 0.02

        for attr in (
            "external_system_dependency", "learning_cost_index",
            "system_complexity", "workload_index", "infrastructure_health",
            "burnout_index"
        ):
            v = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, v)))

    def _tick_trust_and_transparency(self) -> None:
        if self.suppression_level > 0.6 or self.info_transparency < 0.4 or self.dx_clarity < 0.3:
            self.leadership_trust_battery -= 0.03

        if (
            self.suppression_level < 0.4
            and self.info_transparency > 0.6
            and self.pm_capability > 0.5
            and self.grand_design_clarity > 0.5
            and self.portal_maturity > 0.5
        ):
            self.leadership_trust_battery += 0.05

        if self.suppression_level > 0.6:
            self.info_transparency -= 0.02
        elif self.suppression_level < 0.4:
            self.info_transparency += 0.02

        for attr in ("leadership_trust_battery", "info_transparency"):
            v = getattr(self, attr)
            setattr(self, attr, max(0.0, min(1.0, v)))

    def _tick_burnout(self) -> None:
        d = self.dynamics

        # Burnout drivers
        self.burnout_index += d.infra_to_burnout * (1.0 - self.infrastructure_health)
        self.burnout_index += d.dxclarity_to_burnout * (1.0 - self.dx_clarity)
        self.burnout_index += d.workload_to_burnout * self.workload_index
        self.burnout_index += d.complexity_to_burnout * self.system_complexity
        self.burnout_index += d.trustlack_to_burnout * (1.0 - self.leadership_trust_battery)
        self.burnout_index += d.personalization_to_burnout * self.task_personalization_index

        # Relief from good AI infra
        relief = d.llm_relief_to_burnout * self.local_llm_infra_level
        relief += d.ai_service_relief_to_burnout * self.ai_service_quality_index
        self.burnout_index -= relief

        self.burnout_index += self._noise(0.02)
        self.burnout_index = max(0.0, min(1.0, self.burnout_index))

        self.recruitment_difficulty = min(
            1.0,
            0.3
            + self.burnout_index * 0.2
            + self.system_complexity * 0.2
            + (1.0 - self.leadership_trust_battery) * 0.2
            + 0.1 * self.env.demographic_pressure,
        )

        for a in self.actors:
            if a.role in ("teacher", "admin") and not a.has_left_system:
                threshold = 0.5 + (0.5 - a.adaptability)
                if not a.burned_out and self.burnout_index > threshold:
                    a.burned_out = True
                    if a.adaptability > 0.6:
                        a.has_left_system = True
                        a.opportunity_choice = "leave_outside"
                        a.opportunity_cost += 1.0
                    else:
                        a.opportunity_choice = "stay_inside"
                        a.opportunity_cost += 0.7

    def _tick_students(self) -> None:
        raw = (
            (1.0 - self.infrastructure_health) * 0.2
            + self.burnout_index * 0.2
            + self.competitor_gap_index * 0.2
            + max(0.0, 0.5 - self.student_learning_efficiency) * 0.2
            + (1.0 - self.leadership_trust_battery) * 0.1
            + 0.1 * self.env.demographic_pressure
        )

        raw -= 0.1 * self.ai_accessibility_index
        raw -= 0.1 * self.ai_service_quality_index
        raw += self._noise(0.05)

        self.student_exit_rate = max(0.0, min(1.0, raw))

    def _tick_productivity_and_efficiency(self) -> None:
        d = self.dynamics

        # Productivity: negative contributions
        self.productivity_index -= d.external_system_to_productivity * self.external_system_dependency
        self.productivity_index -= d.complexity_to_productivity * self.system_complexity
        self.productivity_index -= d.workload_to_productivity * self.workload_index
        self.productivity_index -= d.infra_bad_to_productivity * (1.0 - self.infrastructure_health)
        self.productivity_index -= d.fragmentation_to_productivity * self.process_fragmentation_index
        self.productivity_index -= d.personalization_to_productivity * self.task_personalization_index

        # Positive contributions
        self.productivity_index += d.llm_to_productivity * self.local_llm_infra_level
        self.productivity_index += d.ai_access_to_productivity * self.ai_accessibility_index

        self.productivity_index += self._noise(0.03)
        self.productivity_index = max(0.0, min(1.0, self.productivity_index))

        # "True" efficiency is derived from infra, clarity, etc.
        base = 0.2
        base += d.base_eff_infra_weight * self.infrastructure_health
        base += d.base_eff_dxclarity_weight * self.dx_clarity
        if self.suppression_level < 0.4:
            base += d.suppression_bonus_to_eff
        base += d.llm_to_efficiency * self.local_llm_infra_level
        base += d.db_to_efficiency * self.database_foundation
        base += d.portal_to_efficiency * self.portal_maturity
        base -= d.personalization_to_efficiency * self.task_personalization_index

        base += self._noise(0.03)
        self.efficiency_index_true = max(0.0, min(1.0, base))

        # Recognized efficiency (KPI) – how leadership *believes*
        self.efficiency_index_recognized += 0.03 * self.external_system_dependency
        self.efficiency_index_recognized += 0.02 * self.system_complexity
        self.efficiency_index_recognized = max(0.0, min(1.0, self.efficiency_index_recognized))

    # ---------- simulation step ----------

    def simulate_year(self) -> None:
        """
        Simulate one "school year" step.
        """
        self.years_simulated += 1
        self._tick_infrastructure()
        self._tick_dx_clarity()
        self._tick_strategy_layer()
        self._tick_portal_and_db()
        self._tick_pm_and_design()
        self._tick_change_dynamics()
        self._tick_education_assets()
        self._tick_innovation()
        self._tick_external_systems()
        self._tick_trust_and_transparency()
        self._tick_burnout()
        self._tick_students()
        self._tick_productivity_and_efficiency()

    # ---------- reporting ----------

    def summary(self) -> str:
        teachers = [a for a in self.actors if a.role == "teacher"]
        admins = [a for a in self.actors if a.role == "admin"]
        students = [a for a in self.actors if a.role == "student"]

        active_teachers = [t for t in teachers if not t.has_left_system]
        left_teachers = [t for t in teachers if t.has_left_system]
        burned_teachers = [t for t in teachers if t.burned_out]
        casualties = [t for t in teachers if t.casualty_of_system]
        rebooted = [t for t in teachers if t.rebooted_outside]

        lines = [
            f"=== {self.name} Ecosystem after {self.years_simulated} year(s) ===",
            f"Infrastructure health        : {self.infrastructure_health:.2f}",
            f"DX clarity (roadmap)         : {self.dx_clarity:.2f}",
            f"Staff burnout index          : {self.burnout_index:.2f}",
            f"Student exit rate (est.)     : {self.student_exit_rate:.2f}",
            f"Recruitment difficulty       : {self.recruitment_difficulty:.2f}",
            "",
            f"Portal maturity (nav DX)     : {self.portal_maturity:.2f}",
            f"Database foundation          : {self.database_foundation:.2f}",
            f"Process fragmentation index  : {self.process_fragmentation_index:.2f}",
            f"Task personalization index   : {self.task_personalization_index:.2f}",
            "  (high = tasks are highly person-dependent; proxy execution is hard)",
            "",
            f"External system dependency   : {self.external_system_dependency:.2f}",
            f"External spend (relative)    : {self.external_spend:.2f}",
            f"Learning cost index          : {self.learning_cost_index:.2f}",
            f"System complexity            : {self.system_complexity:.2f}",
            f"Workload index               : {self.workload_index:.2f}",
            "",
            f"Educational asset index      : {self.educational_asset_index:.2f}",
            f"Central repository level     : {self.central_repository_level:.2f}",
            f"Student learning efficiency  : {self.student_learning_efficiency:.2f}",
            f"Competitor gap index         : {self.competitor_gap_index:.2f}",
            "",
            f"Innovation potential index   : {self.innovation_potential_index:.2f}",
            f"Local LLM infra level        : {self.local_llm_infra_level:.2f}",
            f"AI service quality index     : {self.ai_service_quality_index:.2f}",
            f"AI accessibility index       : {self.ai_accessibility_index:.2f}",
            "",
            f"Productivity index (real)    : {self.productivity_index:.2f}",
            f"Efficiency (true)            : {self.efficiency_index_true:.2f}",
            f"Efficiency (recognized KPI)  : {self.efficiency_index_recognized:.2f}",
            "",
            f"Has SWOT / marketing view    : {self.has_swot}",
            f"Strategic consistency        : {self.strategic_consistency:.2f}",
            f"Change request intensity     : {self.change_request_intensity:.2f}",
            f"Change rejection rate        : {self.change_rejection_rate:.2f}",
            f"Rhetorical change slogans    : {self.rhetorical_change_slogans}",
            "",
            f"PM capability                : {self.pm_capability:.2f}",
            f"Grand design clarity         : {self.grand_design_clarity:.2f}",
            f"Leadership trust battery     : {self.leadership_trust_battery:.2f}",
            f"Info transparency            : {self.info_transparency:.2f}",
            "",
            f"Suppression level (0–1)      : {self.suppression_level:.2f}",
            f"Change seeds planted         : {self.change_seeds_planted}",
            f"Change seeds suppressed      : {self.change_seeds_suppressed}",
            f"Systemic opportunity cost    : {self.systemic_opportunity_cost:.2f}",
            "",
            f"Teachers total               : {len(teachers)}",
            f"Teachers active              : {len(active_teachers)}",
            f"Teachers burned out          : {len(burned_teachers)}",
            f"Teachers who left            : {len(left_teachers)}",
            f"Teachers rebooted outside    : {len(rebooted)}",
            f"Teacher casualties           : {len(casualties)}",
            "",
            "Sample actors snapshot:",
        ]
        for a in self.actors[:5]:
            lines.append(f"  - {a!r}")
        return "\n".join(lines)


# -------------------------
# Future hope probability (students)
# -------------------------

def student_future_hope_probability(
    school: SchoolEcosystem,
    world: ExternalWorld,
    actor: Actor,
) -> float:
    """
    Compute probabilistic "future hope" probability for a student.

    Design:
    - Base term: difference between student's effective adaptability and
      external world's required threshold (delta = base - required).
    - Environment term: aggregate score from school state representing
      negative vs positive scenarios.
    - Logistic function to map to [0, 1].

    Intuition:
    - Even in negative environments, high-adaptability students still have a
      small but non-zero probability (few %) to become future hope.
    - In positive environments, especially for high-adaptability students,
      probabilities can rise to several tens of percent.
    """
    # Base adaptability vs external requirement
    base = world.base_effective_adaptability(actor)
    required = world.required_threshold()
    delta = base - required  # can be negative

    # Environment score: 0 (very negative) ~ 1 (very positive)
    env_components = [
        1.0 - school.suppression_level,          # low suppression is good
        school.dx_clarity,                       # clarity of DX roadmap
        school.student_learning_efficiency,      # learning efficiency
        school.ai_accessibility_index,           # access to AI services
    ]
    env_score = sum(env_components) / len(env_components)
    env_score = max(0.0, min(1.0, env_score))

    # Logistic parameters
    # baseline_logit:
    #   env_score ≈ 0.2  -> p ≈ 0.05–0.15 (very negative)
    #   env_score ≈ 0.7  -> p ≈ 0.3–0.5  (reasonably positive)
    baseline_logit = -2.5 + 3.0 * env_score

    # delta term: rank by adaptability relative to requirement
    # k=5.0 makes ±0.2 difference in delta matter quite a bit
    logit = baseline_logit + 5.0 * delta

    p = 1.0 / (1.0 + math.exp(-logit))
    return max(0.0, min(1.0, p))


# -------------------------
# Demo setup & helpers
# -------------------------

def build_demo_scenario(random_seed: Optional[int] = None) -> Tuple[SchoolEcosystem, ExternalWorld]:
    """
    Build a demo scenario for a fictional school.

    Notes:
    - HighAdaptTeacher* actors are generic high-adapt "test particles".
      In practice, anyone can mentally map themselves onto them.
    """
    if random_seed is not None:
        random.seed(random_seed)

    world = ExternalWorld(selection_pressure=0.8, ai_shift_speed=0.9)

    env = EnvironmentConstraints(
        budget_pressure=0.6,
        regulation_rigidity=0.5,
        demographic_pressure=0.4,
    )

    school = SchoolEcosystem(
        name="ProtectedSchool",
        env=env,
    )

    # Legacy admin / teachers
    school.add_actor(
        Actor(
            name="LegacyDXChief",
            role="admin",
            os_version="LegacyOS-1995",
            adaptability=0.3,
            protected=True,
            change_attitude="neutral",
        )
    )
    school.add_actor(
        Actor(
            name="LegacyTeacherA",
            role="teacher",
            os_version="LegacyOS-2000",
            adaptability=0.4,
            protected=True,
            change_attitude="support",
        )
    )
    school.add_actor(
        Actor(
            name="LegacyTeacherB",
            role="teacher",
            os_version="LegacyOS-2005",
            adaptability=0.35,
            protected=True,
            change_attitude="resist",
        )
    )

    # 高適応の教員たち（ヒーローではなく、ただのサンプル粒子）
    school.add_actor(
        Actor(
            name="HighAdaptTeacher1",
            role="teacher",
            os_version="HighAdaptOS-2025 (LLM-aware)",
            adaptability=0.9,
            protected=False,
            change_attitude="support",
        )
    )
    school.add_actor(
        Actor(
            name="HighAdaptTeacher2",
            role="teacher",
            os_version="HighAdaptOS-2022",
            adaptability=0.8,
            protected=False,
            change_attitude="support",
        )
    )
    school.add_actor(
        Actor(
            name="HighAdaptTeacher3",
            role="teacher",
            os_version="HighAdaptOS-2020",
            adaptability=0.75,
            protected=True,
            change_attitude="neutral",
        )
    )

    # 100名の学生を追加（適応度は分布を持たせる）
    for i in range(100):
        # おおよそ平均0.5、標準偏差0.15くらいの分布（0.1〜0.9にクリップ）
        adapt = random.gauss(0.5, 0.15)
        adapt = max(0.1, min(0.9, adapt))

        # 態度はほとんどがneutral、一部support/resist
        r = random.random()
        if r < 0.15:
            att = "support"
        elif r > 0.85:
            att = "resist"
        else:
            att = "neutral"

        school.add_actor(
            Actor(
                name=f"Student{i+1}",
                role="student",
                os_version="StudentOS-1.0",
                adaptability=adapt,
                protected=True,
                change_attitude=att,  # mostly neutral
            )
        )

    return school, world


def print_world_comparison(school: SchoolEcosystem, world: ExternalWorld) -> None:
    print("\n=== External World Survival Check (Staff) ===")
    for actor in school.actors:
        if actor.role in ("teacher", "admin"):
            survive = world.evaluate_actor(actor)
            tag = "SURVIVES_OUTSIDE" if survive else "ONLY_SAFE_INSIDE"
            print(f"{actor.name:20s} ({actor.os_version:30s}) -> {tag}")


def print_reintegration_report(school: SchoolEcosystem, world: ExternalWorld) -> None:
    print("\n=== Reintegration Outcomes (Teachers/Admins) ===")
    for actor in school.actors:
        if actor.role in ("teacher", "admin") and actor.has_left_system:
            outcome = world.reintegration_outcome(actor)
            if outcome == "rebooted":
                actor.rebooted_outside = True
                tag = "REBOOTED_OUTSIDE (found new path)"
            else:
                actor.casualty_of_system = True
                tag = "CASUALTY_OF_SYSTEM (could not reintegrate)"

            print(
                f"{actor.name:20s} ({actor.os_version:30s}) "
                f"[choice={actor.opportunity_choice}, oc={actor.opportunity_cost:.2f}] "
                f"-> {tag}"
            )

    print("\n=== Future Trajectories (Students) ===")
    students = [a for a in school.actors if a.role == "student"]
    future_hope_students: List[Actor] = []

    for actor in students:
        p_future = student_future_hope_probability(school, world, actor)
        actor.future_hope_probability = p_future
        actor.is_future_hope = random.random() < p_future

        if actor.is_future_hope:
            future_hope_students.append(actor)

        tag = (
            "FUTURE_HOPE (can likely thrive)"
            if actor.is_future_hope
            else "AT_RISK (needs better support / ecosystem)"
        )
        print(
            f"{actor.name:12s} adapt={actor.adaptability:.2f} "
            f"p_future={p_future:.2f} -> {tag}"
        )

    total = len(students)
    fh = len(future_hope_students)
    ratio = fh / total if total > 0 else 0.0
    print(f"\nFuture hope count : {fh} / {total} students")
    print(f"Future hope ratio : {ratio:.3f} (~{ratio*100:.1f}%)")


# -------------------------
# Stakeholder utility presets
# -------------------------

def build_default_utilities() -> list[StakeholderUtility]:
    """
    Example stakeholder utility functions.
    These are illustrative; in real use, stakeholders would define their own.
    """
    return [
        # 教員側から見た「働きやすさ」スコア
        StakeholderUtility(
            name="TeacherPerspective",
            weights={
                "burnout_index": -0.7,
                "workload_index": -0.5,
                "student_learning_efficiency": 0.3,
                "leadership_trust_battery": 0.4,
                "recruitment_difficulty": -0.3,
            },
        ),
        # 経営層がよく見がちな「見かけ上の効率＆コスト」スコア
        StakeholderUtility(
            name="ManagementKPIPerspective",
            weights={
                "efficiency_index_recognized": 0.6,
                "external_spend": -0.3,
                "competitor_gap_index": -0.4,
                "student_exit_rate": -0.4,
            },
        ),
        # 生徒・保護者側の学習体験スコア
        StakeholderUtility(
            name="StudentParentPerspective",
            weights={
                "student_learning_efficiency": 0.6,
                "ai_accessibility_index": 0.4,
                "ai_service_quality_index": 0.4,
                "burnout_index": -0.3,
                "student_exit_rate": -0.5,
            },
        ),
    ]


def print_stakeholder_scores(school: SchoolEcosystem, utilities: list[StakeholderUtility]) -> None:
    print("\n=== Stakeholder Utility Scores ===")
    for u in utilities:
        print(f"{u.name:25s}: {u.score(school):.3f}")


# -------------------------
# Hidden message (obfuscated a little)
# -------------------------

def _print_hidden_message_if_any_future_hope(school: SchoolEcosystem) -> None:
    """
    Prints a small hidden message if at least one student is tagged as future hope.

    The text is lightly obfuscated so that it does not pop out when
    just skimming the source code.
    """
    if not any(a.role == "student" and a.is_future_hope for a in school.actors):
        return

    encoded_words = [
        "siht", "si", "a", "lanoitcif", "loohcs", "noitalumis.",
        "ti", "si", "ton", "tuoba", "eno", "oreh", "rehcaet.",
        "fi", "uoy", "era", "gninnur", "siht", "edoc", "dna", "gnidaer", "eht", "tuptuo,",
        "uoy", "era", "ydaerla", "gnikniht", "tuoba", "smetsys", "dna", "eht", "erutuf.",
        "taht", "teiuq", "tibah", "si", "eno", "llams", "noisrev", "fo", "'erutuf", "epoh'.",
    ]

    msg = " ".join(w[::-1] for w in encoded_words)
    print("\n=== Hidden message ===")
    print(msg)


# -------------------------
# Simulation entry point
# -------------------------

def simulate(years: int = 5, seed: Optional[int] = 42) -> None:
    school, world = build_demo_scenario(random_seed=seed)
    utilities = build_default_utilities()

    print(school.summary())
    print_world_comparison(school, world)
    print_stakeholder_scores(school, utilities)

    for _ in range(years):
        school.simulate_year()

    print("\n")
    print(school.summary())
    print_world_comparison(school, world)
    print_reintegration_report(school, world)
    print_stakeholder_scores(school, utilities)
    _print_hidden_message_if_any_future_hope(school)


if __name__ == "__main__":
    simulate()
