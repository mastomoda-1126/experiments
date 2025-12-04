````markdown
# School Ecosystem Simulator

A small **fictional systems-toy** that models a “protected” school ecosystem interacting with a stricter external world shaped by AI / DX / macro changes.

> ⚠️ **Important upfront notes**
>
> - All schools, people, and roles in this simulator are **fictional**.
> - All numbers (coefficients, thresholds, probabilities) are **illustrative levers**, not empirical truth.
> - This is **not** a decision-support tool for real HR or policy. It is a **thought experiment** about structure, pressure, and different stakeholder perspectives.

---

## 1. What This Script Does

At a high level, the simulator:

- Models a **protected school ecosystem** that can shelter “legacy OS” actors longer than the outside world would.
- Models an **external world** with:
  - selection pressure (`selection_pressure`)
  - speed of AI paradigm shift (`ai_shift_speed`)
- Simulates year-by-year changes in:
  - infrastructure health
  - DX roadmap clarity
  - burnout
  - productivity
  - “true” vs “recognized” efficiency
  - trust and transparency
  - student learning efficiency and exit rate
  - innovation potential and local LLM infra
- Explicitly injects **randomness** so results are **non-deterministic** even with similar parameters.
- Tracks:
  - legacy admins / teachers
  - several high-adaptability teachers
  - 100 procedurally generated students
- Observes over multiple years:
  - Who burns out?
  - Who leaves the system?
  - Who manages to “reboot” outside vs becoming a casualty?
  - Which students probabilistically become “future hope” under different environments?

At the end of a run it:

- Prints **before/after summaries** of the school state.
- Compares staff against external survival thresholds.
- Prints **reintegration outcomes** for staff who left.
- Computes **probabilistic future hope** for each student.
- Prints **stakeholder utility scores** from several example viewpoints.
- Emits a small, lightly obfuscated **hidden message** if at least one student is tagged as “future hope”.

---

## 2. How To Run It

Requirements: **Python 3.10+**

### Basic usage (CLI)

```bash
python main.py       # or: py main.py on Windows
````

This will:

1. Build a demo scenario (fictional actors + default parameters).
2. Print the initial state.
3. Simulate 5 years (default).
4. Print the final state, staff comparison, reintegration report, stakeholder scores, and possibly the hidden message.

### Programmatic usage

You can call the simulation from another Python script or from the REPL:

```bash
python - <<'PY'
from main import simulate

# Example: 8-year horizon, different RNG seed
simulate(years=8, seed=7)
PY
```

Parameters:

* `years`: how many school years to simulate.
* `seed`: optional random seed for reproducibility.
  Change this to see different random realizations under the same structural parameters.

---

## 3. Conceptual Model (What the Classes Represent)

This section explains the main dataclasses so you can read or modify the code with intent.

### 3.1 Actor

```python
@dataclass
class Actor:
    name: str
    role: Literal["teacher", "admin", "student"]
    os_version: str
    adaptability: float  # 0.0–1.0
    protected: bool = True
    ...
```

Each `Actor` represents one person in the ecosystem:

* `role`: teacher, admin, or student.
* `os_version`: a label like `"LegacyOS-1995"` or `"HighAdaptOS-2025"`; this is **just a tag**, not real software.
* `adaptability`: how flexible this actor is under change.
* Additional fields track:

  * burnout status
  * whether they have left the system
  * whether they rebooted successfully outside or became a casualty
  * opportunity cost and what choice they made (`stay_inside` / `leave_outside`)
  * for students: probability and label of “future hope”.

### 3.2 ExternalWorld

```python
@dataclass
class ExternalWorld:
    selection_pressure: float = 0.8
    ai_shift_speed: float = 0.9
```

Represents external constraints:

* `required_threshold()` computes how high an actor’s **effective adaptability** must be to survive outside.
* `evaluate_actor(actor)` checks if a staff member is **likely** to survive outside (deterministic baseline).
* `reintegration_outcome(actor)` adds random noise and burnout penalties to decide:

  * `"rebooted"` vs `"casualty"` for actors who left.

### 3.3 EnvironmentConstraints

```python
@dataclass
class EnvironmentConstraints:
    budget_pressure: float = 0.5
    regulation_rigidity: float = 0.5
    demographic_pressure: float = 0.5
```

Encodes macro-level constraints (budget, regulations, demographics) that influence how fast or slow certain improvements can happen.

### 3.4 SchoolEcosystem

```python
@dataclass
class SchoolEcosystem:
    name: str
    env: EnvironmentConstraints
    dynamics: DynamicsCoefficients = field(default_factory=DynamicsCoefficients)
    actors: List[Actor] = field(default_factory=list)
    ...
```

This holds the **state of the school** and the **dynamics** that evolve it year by year.

It tracks many indices, for example:

* `infrastructure_health`
* `dx_clarity` (DX roadmap clarity)
* `burnout_index`
* `student_exit_rate`
* `portal_maturity`, `database_foundation`
* `process_fragmentation_index`, `task_personalization_index`
* `external_system_dependency`, `external_spend`
* `educational_asset_index`, `central_repository_level`
* `innovation_potential_index`, `local_llm_infra_level`
* `ai_service_quality_index`, `ai_accessibility_index`
* `productivity_index`
* `efficiency_index_true` vs `efficiency_index_recognized`
* `suppression_level` (0–1)
* `leadership_trust_battery`, `info_transparency`
* `pm_capability`, `grand_design_clarity`

The yearly update is done by:

```python
def simulate_year(self) -> None:
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
```

Each `_tick_...` function encodes one part of the “physics” of the ecosystem.

### 3.5 DynamicsCoefficients (the “physics parameters”)

```python
@dataclass
class DynamicsCoefficients:
    infra_to_burnout: float = 0.1
    dxclarity_to_burnout: float = 0.1
    ...
```

These are the **weights** that connect state variables (e.g., bad infrastructure) to outcomes (e.g., burnout).
They are **not empirically calibrated** and should be treated as **hypotheses / sliders**:

* Increase a coefficient → that factor has more influence.
* Decrease a coefficient → that factor matters less.

You can create your own `DynamicsCoefficients` to explore alternate “worldviews” without touching the structure.

### 3.6 StakeholderUtility (the “value layer”)

```python
@dataclass
class StakeholderUtility:
    name: str
    weights: dict[str, float]
```

This is a simple linear utility function over `SchoolEcosystem` attributes:

* It does **not** change the simulation itself.
* It only changes **how a given state is scored** from a particular viewpoint
  (e.g., teachers, management, students/parents).

The default utilities are defined in `build_default_utilities()`.

### 3.7 Student “future hope” probability

```python
def student_future_hope_probability(school, world, actor) -> float:
    ...
```

For each student, this function:

* Looks at the student’s **effective adaptability** vs external requirement.
* Computes an **environment score** from:

  * suppression level
  * DX clarity
  * student learning efficiency
  * AI accessibility
* Combines them with a **logistic function** to get a probability in `[0, 1]`.

Design intent:

* Even in negative environments, high-adaptability students have a **small but non-zero** chance to become “future hope”.
* In positive environments, probabilities can reach **several tens of percent** for high-adaptability students.
* Randomness is used when deciding whether each individual becomes “future hope” so there is no deterministic “destiny”.

---

## 4. Adjusting the Initial Parameters

The demo scenario is assembled in `build_demo_scenario()` and used by `simulate()` (see `main.py`).
You can change **any** of these knobs to describe different fictional worlds.

> 💡 **Guiding idea:**
> These parameters are **your assumptions** about how the world works.
> Editing them is part of the experiment.

### 4.1 Simulation horizon & randomness

* In `simulate(years=5, seed=42)`:

  * Increase `years` to watch long-term drifts (e.g., 10–20 years).
  * Change `seed` to get different random samples under the same structure.
* Inside `SchoolEcosystem`, the `randomness` field (default `0.05`) controls how noisy transitions are:

  * `randomness = 0.0`: fully deterministic, given the same start state.
  * Higher values: more random variation around the trend.

### 4.2 External pressure

Defined in:

```python
world = ExternalWorld(selection_pressure=0.8, ai_shift_speed=0.9)
```

* Increase `selection_pressure` or `ai_shift_speed` to simulate **harsher outside markets**:

  * Staff need higher effective adaptability to reboot successfully.
* Decrease them to simulate **gentler environments** where more staff can survive outside.

### 4.3 Macro constraints (budget / regulation / demographics)

Right before the `SchoolEcosystem` is created:

```python
env = EnvironmentConstraints(
    budget_pressure=0.6,
    regulation_rigidity=0.5,
    demographic_pressure=0.4,
)
```

* `budget_pressure`: high → less room for improvement even if structure is good.
* `regulation_rigidity`: high → reforms and innovation are slower.
* `demographic_pressure`: high → shrinking student pool and more difficulty recruiting.

These values feed into several `_tick_...` functions and will shape:

* Innovation potential growth
* Educational assets and repositories
* Recruitment difficulty
* Student exit dynamics

### 4.4 School starting stats

The `SchoolEcosystem` constructor has many default fields. In the demo:

```python
school = SchoolEcosystem(
    name="ProtectedSchool",
    env=env,
)
```

You can override any index here to change the starting point:

```python
school = SchoolEcosystem(
    name="ProtectedSchool",
    env=env,
    infrastructure_health=0.6,
    suppression_level=0.5,
    student_learning_efficiency=0.55,
    portal_maturity=0.2,
    database_foundation=0.2,
)
```

Typical levers:

* `suppression_level`
* `portal_maturity` / `database_foundation`
* `process_fragmentation_index`
* `leadership_trust_battery` / `info_transparency`
* `local_llm_infra_level` / `ai_accessibility_index`

These starting values strongly influence how the early years behave (and sometimes whether positive feedback loops can even start).

### 4.5 Dynamics coefficients (“physics” weights)

To change **how strongly** each factor influences burnout, productivity, and efficiency, pass a custom `DynamicsCoefficients`:

```python
custom_dyn = DynamicsCoefficients(
    infra_to_burnout=0.15,               # make infra issues hurt more
    workload_to_burnout=0.02,            # treat workload as less central
    llm_to_productivity=0.03,            # be more conservative about LLM gains
    base_eff_infra_weight=0.5,           # infra matters more to true efficiency
)

school = SchoolEcosystem(
    name="ProtectedSchool",
    env=env,
    dynamics=custom_dyn,
)
```

Use this to encode **different hypotheses**:

* A world where **trust** matters more than infra.
* A world where **AI helps a lot** vs a world where it helps only a little.
* A world where **fragmentation** is the main burnout driver, etc.

### 4.6 Actors (staff & students)

At the end of `build_demo_scenario()`:

* A small set of admins / teachers is created:

  * legacy DX chief
  * legacy teachers
  * several high-adapt teachers (generic “test particles”)
* Then 100 students are added:

```python
for i in range(100):
    adapt = random.gauss(0.5, 0.15)
    adapt = max(0.1, min(0.9, adapt))
    ...
```

You can:

* Change the **number** of students.
* Change the adaptability distribution:

  * mean (`0.5`) → more adaptive or more fragile cohorts.
  * standard deviation (`0.15`) → more homogeneous vs more diverse.
  * clamp range (`[0.1, 0.9]`) → minimum and maximum adaptability.
* Change `change_attitude` probabilities (support / neutral / resist).
* Add or remove teachers / admins with different:

  * `os_version`
  * `adaptability`
  * `change_attitude`
  * `protected` flag

These changes will affect:

* How many “change seeds” exist (`_tick_change_dynamics`).
* Who burns out and who leaves under pressure.
* How external survival checks play out.

### 4.7 Stakeholder utilities (value perspectives)

`build_default_utilities()` defines three example lenses:

* `TeacherPerspective`
* `ManagementKPIPerspective`
* `StudentParentPerspective`

Each is a simple weight dictionary over school attributes, e.g.:

```python
StakeholderUtility(
    name="TeacherPerspective",
    weights={
        "burnout_index": -0.7,
        "workload_index": -0.5,
        "student_learning_efficiency": 0.3,
        "leadership_trust_battery": 0.4,
        "recruitment_difficulty": -0.3,
    },
)
```

You can:

* Change weights to reflect different priorities.
* Add new perspectives (e.g., “RegulatorView”, “AlumniView”).
* Have students design their own weights and compare how **the same state** looks under different value systems.

Remember: **utility scores do not affect the simulation**. They only affect **how you interpret** the result.

---

## 5. Suggested Workflow (For Exploration or Workshops)

1. **Run the default scenario once**

   ```bash
   python main.py
   ```

   * Skim the initial and final summaries.
   * Look at staff survival vs external world.
   * Look at future hope counts and stakeholder scores.

2. **Pick a hypothesis to test**

   Example ideas:

   * “What if suppression is low but infrastructure starts very weak?”
   * “What if AI infra is great, but trust is low and PM is weak?”
   * “What if budget pressure is extremely high, but leadership is strong?”

3. **Modify parameters**

   * Edit `build_demo_scenario()`:

     * change `SchoolEcosystem` starting indices
     * adjust `EnvironmentConstraints`
     * tweak `ExternalWorld`
     * swap in a custom `DynamicsCoefficients`
   * Optionally, adjust actors (number and distribution of students, staff mix).

4. **Re-run and compare**

   * Run `python main.py` (or call `simulate(...)` with your own years/seed).
   * Compare:

     * `burnout_index`, `student_exit_rate`
     * `efficiency_index_true` vs `efficiency_index_recognized`
     * number of “future hope” students
     * stakeholder scores

5. **Iterate**

   * Repeat with different parameter sets.
   * Capture interesting configurations (e.g., as separate functions like `build_optimistic_scenario()`, `build_pessimistic_scenario()`).
   * If used in a class or workshop, let different groups take different parameter sets and present their outcomes.

---

## 6. Interpretation & Safety Notes

To avoid misunderstandings:

* This code is **not a moral judgement machine**.
* It does **not** say who “should” leave or stay in any real organization.
* It does **not** predict the fate of any particular real student or teacher.

Instead, it is:

* A **toy model** to think about:

  * how structure (infra, DX clarity, PM, trust, suppression)
  * and external constraints (budget, regulations, selection pressure)
  * interact with people’s adaptability and choices.
* A way to explore how **different stakeholders** can look at the **same situation** and score it very differently.

If you use this simulator in teaching:

* Emphasize that **changing parameters is part of the learning**.
* Encourage participants to:

  * challenge the default coefficients,
  * propose alternative dynamics,
  * design their own stakeholder utilities,
  * and discuss which assumptions feel realistic or not.

---

## 7. Extending the Simulator

Because the core is plain Python with dataclasses, it is easy to extend:

* Add new indices to `SchoolEcosystem` (e.g., “mentoring_index”, “community_support_index”).
* Add new `_tick_...` functions that couple them into the dynamics.
* Split code into multiple modules (`models.py`, `dynamics.py`, `reporting.py`) if the file gets large.
* Replace print-based reporting with:

  * JSON output,
  * plotting,
  * or a small web UI to adjust parameters interactively.

You are encouraged to **fork and customize** this simulator for:

* workshops,
* blog posts,
* lectures about organizational debt and adaptation pressure,
* or purely personal thought experiments.

The important part is not the exact numbers, but **the conversations and questions** that emerge when you start to move those numbers around.

```
```
