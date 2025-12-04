# School Ecosystem Simulator

## What This Script Does
- Models a fictional “protected school　ecosystem interacting with a harsher external world that is shaped by AI/DX trends.
- Simulates infrastructure decay, burnout, productivity, efficiency, and stakeholder utilities with explicit randomness so results are non-deterministic.
- Tracks legacy staff, higher-adaptability teachers, and 100 generated students to see who burns out, leaves, or becomes “future hope after a multiyear run.
- Prints summaries before and after the run, compares staff against external requirements, reports student futures, and emits a lightly obfuscated hidden message if any students reach future-hope status.

Run it with Python 3.10+:

```bash
python main.py               # or: py main.py on Windows
python - <<'PY'
from main import simulate
simulate(years=8, seed=7)    # programmatic entry point
PY
```

## Adjusting the Initial Parameters
The demo scenario is assembled in `build_demo_scenario()` and `simulate()` (see `main.py`). Tweak the following areas to explore different worlds:

1. **Simulation horizon & randomness**
   - Change the arguments in `simulate(years=5, seed=42)` to run longer or start from a different RNG seed.
   - Inside `SchoolEcosystem`, the `randomness` field (default `0.05`) controls how noisy yearly transitions are.

2. **External pressure**
   - Edit `ExternalWorld(selection_pressure=0.8, ai_shift_speed=0.9)` to represent harsher or kinder outside markets. Higher values raise the adaptability threshold staff must clear to thrive after leaving.

3. **Macro constraints**
   - The `EnvironmentConstraints` dataclass (`budget_pressure`, `regulation_rigidity`, `demographic_pressure`) is created right before the `SchoolEcosystem`. Raising these numbers simulates tighter budgets, tougher regulations, or shrinking student pools and will influence several downstream ticks.

4. **School starting stats**
   - `SchoolEcosystem(...)` is instantiated with dozens of baseline indices (infrastructure health, suppression level, portal maturity, AI accessibility, etc.). Override the defaults directly in the constructor call—or reassign attributes after creation—to encode a healthier or more fragile organization.
   - Example snippet:
     ```python
     school = SchoolEcosystem(
         name="ProtectedSchool",
         env=env,
         infrastructure_health=0.6,
         suppression_level=0.5,
         student_learning_efficiency=0.55,
     )
     ```

5. **Dynamics coefficients**
   - Pass a customized `DynamicsCoefficients(...)` when creating `SchoolEcosystem` if you want burnout to react more strongly (or weakly) to fragmentation, workload, etc. That lets you keep the actor roster the same but explore alternate “physics for the ecosystem.

6. **Actors**
   - The roster at the bottom of `build_demo_scenario()` seeds legacy admins, three high-adapt teachers, and 100 procedurally generated students. Adjust `adaptability`, `change_attitude`, or even add new roles to see how different mixes change the outcome.
   - The student loop currently samples adaptability from a truncated Gaussian (`random.gauss(0.5, 0.15)` and clamps it to `[0.1, 0.9]`). Modify the mean, variance, or clamp to simulate more fragile or more resilient student bodies.

7. **Stakeholder utilities**
   - `build_default_utilities()` defines three example viewpoints (teachers, management KPI lens, and student/parent experience). Edit the `weights` dicts or add new `StakeholderUtility` objects to see how different value systems evaluate the same simulated state.

## Suggested Workflow
1. Modify parameters as described above.
2. Run `python main.py` to simulate five years with the new setup.
3. Inspect the “before/after Esummaries, world survival table, reintegration report, stakeholder utility scores, and (if triggered) the hidden message to understand how your tweaks influenced the ecosystem.
4. Iterate on the parameters or extend the dataclasses if you need richer scenarios (e.g., add new indices, actors, or outputs).

Because every rate and threshold lives in plain Python dataclasses, the simulator is intentionally easy to fork for workshops, blog posts, or thought experiments about organizational debt and adaptation pressure.
