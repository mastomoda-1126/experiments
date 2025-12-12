# School Ecosystem Simulator

A small **fictional systems-toy** that models a “protected” school ecosystem and a stricter external world shaped by AI / DX / macro changes. It is meant for **thought experiments and discussion**, not for prediction.
日本語：AI・DX・マクロ環境の変化が強い外部世界と、そこからある程度守られた架空の学校エコシステムをシミュレートする**思考実験用の小さなモデル**です。予測や意思決定ツールではありません。

⚠️ **Important upfront notes**

- All schools, people, and roles in this simulator are **fictional**.
  日本語：登場する学校・人物・役職はすべてフィクションです。
- All numbers (coefficients, thresholds, probabilities) are **illustrative levers**, not empirical truth.
  日本語：係数・しきい値・確率などの数値は「仮のつまみ」であり、経験的な真実ではありません。
- This is **not** a decision-support tool for real HR, policy, or clinical decisions.
  日本語：現実の人事・制度設計・臨床判断などの意思決定ツールとして使うことは想定していません。
- The update rules are **loosely informed by recent research** (e.g. on job demands–resources, school climate, technostress, AI in education), but only at the level of *directions* (signs), not effect sizes.
  日本語：更新ルールは近年の研究（仕事要求‐資源モデル、学校風土、テクノストレス、教育分野のAIなど）の「符号（方向）」のみをゆるく反映しており、効果量は反映していません。
- AI / LLM tools in this script are intentionally simplified:
  日本語：AI/LLM の効果は意図的に控えめで、以下の条件を満たした場合にだけ少し効くようにしています。
  - They relieve some workload and improve learning efficiency **only after** certain structural pre-conditions (infrastructure, repositories, clarity, trust) are met.
    日本語：インフラ・教材リポジトリ・方針の明確さ・信頼が整った後にのみ業務負荷を軽減し、学習効率を改善します。
  - Real-world AI deployments can also *increase* workload and stress; those “AI gone wrong” scenarios are largely **out of scope** for this toy model.
    日本語：現実のAI導入では負荷やストレスが増すケースもありますが、本モデルでは大きく扱っていません。

In short: this code is a **sandbox for exploring assumptions** about structure, pressure, and different stakeholder perspectives — not a model of any specific real institution.
日本語：これは、構造・圧力・利害関係者の視点の違いを試すための**仮想サンドボックス**であり、実在の組織を表すものではありません。

---

## Version

- Current version: **1.0.1** (defined in `main.py::__version__`)
- When bumping the version, update both `main.py` and this README section to keep them aligned.

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
  - a cohort of procedurally generated students
- Observes over multiple years:
  - Who burns out?
  - Who leaves the system?
  - Who manages to “reboot” outside vs becoming a casualty?
  - Which students probabilistically become “future hope” under different environments?

At the end of a run it:

- Prints **before/after summaries** of the school state.
- Compares staff against external survival thresholds.
- Prints **reintegration outcomes** for staff who left.
- Computes **probabilistic future hope** for each student (using a small logistic model based on adaptability and environment; this is *illustrative*, not predictive).
- Prints **stakeholder utility scores** from several example viewpoints.
- Emits a small, lightly obfuscated **hidden message** if at least one student is tagged as “future hope”.
- Writes a **year-by-year history** (burnout, complexity, expected future-hope count, etc.) used for downstream reporting.
- Generates a **dashboard PNG** plus a timestamped PDF under `output/`, with simple charts and an automatically generated “Org health advice” panel.

The intent is to give you a **playground for assumptions**: you tweak parameters and structures, then watch how the fictional ecosystem responds, knowing that the numbers are illustrative rather than empirically calibrated.


---

## 2. How To Run It

Requirements:

- **Python 3.10+**
- `matplotlib` (install with `pip install matplotlib` or `pip install -r requirements.txt`)

### Basic usage (CLI)

```bash
python main.py       # or: py main.py on Windows
````

This will:

1. Build a demo scenario (fictional actors + default parameters).
2. Print the initial state.
3. Simulate 10 years by default (override with `simulate(years=...)` or edit `simulate`).
4. Print the final state, staff comparison, reintegration report, stakeholder scores, and possibly the hidden message.
5. Save `outputs/simulation_history_page1.png` and a timestamped PDF in `outputs/` with the same trend charts plus the auto-generated org-health advice block.

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

To keep scenario definitions readable, two helper dataclasses wrap these parameters:

* `ActorSpec` – deterministic staff/admin entries instantiated via `_add_actor_specs`.
* `StudentDemographic` – cohort definitions (count, adaptability distribution, attitude probabilities) used by `_populate_student_demographics` to create 100 diverse students.

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

* `trend_damping` (default `0.65`) blends each year's delta back toward the previous value. Increase it toward `1.0` for snappier swings, decrease toward ~`0.4` for very slow-moving institutions.

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

`build_demo_scenario()` now separates deterministic adults and demographic-driven students:

1. **Staff/Admins (20 total)** – encoded as `core_actor_specs` (list of `ActorSpec`). This covers legacy leadership, hybrid ops, wellness roles, multiple high-adapt teachers, outreach coaches, etc. `_add_actor_specs()` simply iterates that list and instantiates each entry, so editing the staff cast is as easy as changing the table.
2. **Students (100 total)** – defined through `student_demographics`, a list of nine `StudentDemographic` cohorts (UrbanScholar, RuralGeneral, STEMCoder, CreativeArtist, TransferStudent, CaregiverWorker, Athlete, Activist, InternationalBridge). Each cohort declares its count, OS tag, adaptability mean/std (clamped to `[0.1, 0.95]`), protection flag, and support/neutral/resist probabilities. `_populate_student_demographics()` handles naming and sampling accordingly.

To customize:

* Modify entries in `core_actor_specs` to add/remove specific adults or tweak their adaptability/protection.
* Adjust cohort sizes or distributions inside `student_demographics` to reflect different fictional demographics or total student counts.
* Introduce new cohorts (e.g., `EveningAdultLearner`, `ExchangeScholar`) by appending to the demographic list.

These edits continue to influence:

* How many “change seeds” exist (`_tick_change_dynamics`).
* Burnout/exit patterns among adults.
* Student future-hope probabilities, since adaptability and environment interplay in `student_future_hope_probability()`.

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

## 5. Visual dashboard (PNG + PDF)

Every simulation run writes the following artifacts to `outputs/`:

- `simulation_history_page1.png`
- `simulation_history_YYYYMMDD_HHMMSS.pdf` (timestamped so you can keep multiple runs without overwriting)

Each dashboard has seven panels:

1. **Initial parameters** – the starting metrics so you can compare later runs.
2. **Org health advice** – automatically generated guidance (e.g., “Lower suppression”, “Simplify workflows”) derived from the latest snapshot.
3. **Infrastructure vs Complexity** – trendlines for infra health vs system complexity.
4. **Burnout & Workload** – burnout index vs workload index.
5. **Student outcomes** – student exit rate vs learning efficiency.
6. **Productivity & Efficiency** – true productivity vs true/recognized efficiency.
7. **Future hope output** – expected count of future-hope students computed from the probability model.

Use the PDF when you need to flip through multiple runs, and the PNG for quick sharing in reports or slides.

---

## 6. Suggested Workflow (For Exploration or Workshops)

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

## 7. Interpretation & Safety Notes

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

## 8. Extending the Simulator

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

---

## 9. Evidence-informed design notes (very short)

This simulator is *not* empirically calibrated, but the sign and rough structure of many links are aligned with current research on schools, teachers, and students.

Very briefly:

- **Job demands, burnout, and retention**

  Large meta-analyses of teacher well-being framed by the Job Demands–Resources (JD-R) model show that high workload, role conflict, and other job demands are robustly associated with stress and burnout, while resources such as autonomy, collegial support, and psychological capital predict better well-being and occupational commitment and lower turnover intentions (e.g., Li et al., 2025). Burnout and work engagement emerge as the strongest correlates of overall well-being.  

  → In the simulator, indices like `workload_index`, `burnout_index` and `recruitment_difficulty` loosely reflect this JD-R logic.

- **Leadership, trust, and school climate**

  Qualitative and quantitative studies consistently find that opaque, authoritarian leadership practices harm teacher well-being and retention, while transparent, supportive, and participatory leadership strengthens trust and keeps teachers in the profession (e.g., Flores & Shuls, 2024; Li, 2024; Education Support, 2025). Work on inclusive school climate also shows that positive climate and teaching efficacy can buffer burnout.  

  → This is echoed in how `leadership_trust_battery`, `info_transparency`, and `suppression_level` feed into `burnout_index`, `systemic_opportunity_cost`, and change-dynamics in the model.

- **Digital complexity, technostress, and “DX gone wrong”**

  Systematic reviews and empirical studies on **technostress** report that juggling multiple ICT systems, constant connectivity, and frequent tool changes can increase stress, health complaints, work–family conflict, and intentions to quit among teachers (e.g., Yang et al., 2025; Rey-Merchán et al., 2022; Wang et al., 2023, 2025). Poorly integrated digital ecosystems can therefore degrade both well-being and effectiveness.  

  → The simulator expresses this as rising `external_system_dependency`, `system_complexity`, `process_fragmentation_index`, and `learning_cost_index` pushing up `workload_index` and `burnout_index` while dragging down `productivity_index`.

- **AI / LLM tools: double-edged relief**

  Recent reviews on AI in teaching and teacher professional development suggest that AI-based tools can offload routine tasks, support personalised feedback, and improve some learning metrics when well designed and supported, but also introduce new demands, ethical concerns, and dependency risks (e.g., Tan et al., 2024; Eltahir, 2024; Klimova, 2025; Younas, 2025).  

  → In this toy model, higher `local_llm_infra_level` and `ai_accessibility_index` slightly relieve burnout and improve productivity and student learning efficiency, but only after some structural pre-conditions (infra, repositories, clarity) are met. This is deliberately cautious rather than “AI solves everything”.

- **Teacher burnout and student outcomes / "future hope"**

  A systematic review by Madigan & Kim (2021) and more recent work indicate that teacher burnout is associated with lower student achievement and less adaptive motivation, and that teacher stress and burnout covary with classroom climate indicators. At the same time, even in difficult environments, some students still achieve strong outcomes.  

  → The `student_future_hope_probability(...)` function follows this spirit: harsh environments and high burnout push probabilities down, but individual adaptability still leaves a small non-zero chance for “future hope” students even in negative scenarios, and higher chances under healthier structures.

> **TL;DR**: numbers in this code are *dials*, not truth.  
> But the directions of influence are chosen so that pushing the dials roughly agrees with what recent research tends to find about schools, teachers, and students.


# Japanese ver.

**バージョン**: 現在のバージョンは **1.0.1** です（`main.py` の `__version__` と同じ値）。バージョンを上げる際は `main.py` と README の両方を同時に更新してください。

````markdown
# School Ecosystem Simulator（スクール・エコシステム・シミュレータ）

AI・DX・マクロ環境の変化にさらされる「外部世界」と、そこからある程度保護された**架空の学校エコシステム**の相互作用をモデル化した、小さな**システム系のおもちゃ（systems-toy）**です。

> ⚠️ **最初に重要な注意**
>
> - このシミュレータに登場する学校・人物・役職は、すべて**フィクション**です。
> - 係数・しきい値・確率などの数値は、**経験的な真実ではなく「仮のつまみ」**です。
> - 現実の人事・制度設計などの**意思決定ツールとして使うことは想定していません**。  
>   これは、組織構造・圧力・利害関係者の視点の違いについて考えるための**思考実験**用モデルです。

---

## 1. このスクリプトがやること

このシミュレータは、ざっくり言うと次のようなことを行います。

- **保護された学校エコシステム**をモデル化  
  - 「レガシーOS」を持つアクター（教員・管理職）が、外部世界より長く生き残れる環境
- それと対になる**外部世界**をモデル化  
  - `selection_pressure`：選択圧（厳しさ）
  - `ai_shift_speed`：AIパラダイムシフトの速度
- 年ごとの変化として、以下のような指標をシミュレート  
  - インフラ健全性
  - DXロードマップの明確さ
  - バーンアウト
  - 生産性
  - 「真の効率」 vs 「認識されている効率（KPI）」
  - 信頼・情報透明性
  - 学習効率・生徒離脱率
  - イノベーションポテンシャルとローカルLLM基盤
- **乱数によるノイズ**を明示的に入れ、結果が**非決定的**になるように設計
- 追跡するアクター：
  - レガシーな管理職・教員
  - 高適応な教員数名
  - 100人の生成された生徒
- 複数年のシミュレーションを通して観察すること：
  - 誰がバーンアウトするか？
  - 誰がシステムから出ていくか？
  - 出た人は外で「再起」できるのか、それともキャリア的に「犠牲」になってしまうのか？
  - 環境と適応力の組み合わせの中で、どの生徒が確率的に「future hope」になるのか？

シミュレーション終了時には、次のものを出力します。

- 学校状態の**開始前 / 終了後サマリー**
- スタッフが外部世界の要求をどの程度満たせるかの比較
- システムを離れたスタッフの**再統合（re-integration）レポート**
- 各生徒の**future hope の確率とラベル付け**
- 複数の**ステークホルダー視点**から見たユーティリティスコア
- 少なくとも1人の生徒が future hope になった場合、小さな**隠しメッセージ**（軽く難読化済み）を出力
- 年次ごとの**履歴データ**（バーンアウト、複雑性、future hope 期待値など）を保存
- `outputs/` に**ダッシュボード PNG**とタイムスタンプ付き PDF を出力（トレンド＋組織アドバイス付き）

---

## 2. 実行方法

要件：

- **Python 3.10 以上**
- `matplotlib`（`pip install matplotlib` または `pip install -r requirements.txt` などで導入）

### 基本的な使い方（コマンドライン）

```bash
python main.py       # Windows なら: py main.py
````

このコマンドで行われること：

1. デモ用シナリオの構築（架空のアクター＋デフォルトパラメータ）
2. 初期状態サマリーの出力
3. デフォルトで**10年間**のシミュレーション（`simulate(years=...)` で変更可能）
4. 最終状態サマリー、外部世界との比較、再統合レポート、ステークホルダスコア、および条件を満たせば隠しメッセージの出力
5. `outputs/` に `simulation_history_page1.png` とタイムスタンプ付き PDF（例：`simulation_history_YYYYMMDD_HHMMSS.pdf`）を保存

以前の実行結果を見直したい場合は、`outputs/` フォルダ内の PNG / PDF を開いてください。PDF は毎回タイムスタンプ付きで生成されるため、閲覧中に上書きされる心配はありません。

### プログラムから呼び出す場合

別スクリプトや REPL から直接呼び出すこともできます。

```bash
python - <<'PY'
from main import simulate

# 例：8年シミュレーション、乱数シードを変更
simulate(years=8, seed=7)
PY
```

引数：

* `years`: シミュレートする「学校年度」の数
* `seed`: 再現性を保つための乱数シード（任意）
  同じ seed と同じ構造パラメータなら、同じ結果が出ます。

---

## 3. 概念モデル（各クラスが意味しているもの）

コードを読みやすく・変更しやすくするために、主要な dataclass の意味を整理します。

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

`Actor` はエコシステム内の**1人の人物**を表します。

* `role`: `"teacher"`, `"admin"`, `"student"` のいずれか
* `os_version`: `"LegacyOS-1995"`, `"HighAdaptOS-2025"` のようなラベル（**比喩的なタグ**であり、実在ソフトではありません）
* `adaptability`: 変化への適応力（0.0〜1.0）
* その他のフィールドで管理するもの：

  * バーンアウト状態
  * システムから離脱したかどうか
  * 外部で「再起」できたか、それとも「犠牲」になったか
  * 機会費用（opportunity_cost）と、そのときの選択（`stay_inside` / `leave_outside`）
  * 生徒の場合：future hope 確率とラベル

シナリオ定義を読みやすく保つため、次の補助 dataclass を併用しています：

* `ActorSpec` – `_add_actor_specs` を通じて個別ポジションを生成する人材テーブルです。
* `StudentDemographic` – `_populate_student_demographics` で定義個数の生徒を指定分布に応じて自動生成するためのコーホートです。

### 3.2 ExternalWorld

```python
@dataclass
class ExternalWorld:
    selection_pressure: float = 0.8
    ai_shift_speed: float = 0.9
```

**外部世界の厳しさ**を表すクラスです。

* `required_threshold()`
  → 外部世界で生き残るために必要な「実効適応力」を計算
* `evaluate_actor(actor)`
  → 教職員が外で生き残れそうかどうかの**ベースライン判定（決定論的）**
* `reintegration_outcome(actor)`
  → バーンアウトペナルティと乱数ノイズを加えたうえで、

  * `"rebooted"`（再起）
  * `"casualty"`（システム由来の犠牲）
    を確率的に決定

### 3.3 EnvironmentConstraints

```python
@dataclass
class EnvironmentConstraints:
    budget_pressure: float = 0.5
    regulation_rigidity: float = 0.5
    demographic_pressure: float = 0.5
```

学校の外側にある**マクロ制約**を表します。

* `budget_pressure`: 予算圧力（高いほど改善に使える余力が少ない）
* `regulation_rigidity`: 規制の硬さ（高いほど制度変更が難しい）
* `demographic_pressure`: 人口動態圧力（高いほど生徒数減少・採用難など）

これらは複数の `_tick_...` 内で参照され、たとえば：

* イノベーションポテンシャルの蓄積速度
* 教材資産・リポジトリの構築速度
* 採用難易度
* 生徒離脱のダイナミクス

などに影響します。

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

**学校組織そのもの**を表すクラスで、状態とダイナミクスを一括して持ちます。

主なインデックス例：

* `infrastructure_health`（インフラ健全性）
* `dx_clarity`（DXロードマップの明確さ）
* `burnout_index`（教職員バーンアウト指数）
* `student_exit_rate`（生徒離脱率推定）
* `portal_maturity` / `database_foundation`（ポータル・DBの成熟度）
* `process_fragmentation_index`（業務の分断度）
* `task_personalization_index`（タスク属人性）
* `external_system_dependency` / `external_spend`（外部システム依存と支出）
* `educational_asset_index` / `central_repository_level`（教材資産・中央リポジトリ）
* `innovation_potential_index` / `local_llm_infra_level`
* `ai_service_quality_index` / `ai_accessibility_index`
* `productivity_index`
* `efficiency_index_true` vs `efficiency_index_recognized`
* `suppression_level`（変化抑圧レベル）
* `leadership_trust_battery` / `info_transparency`
* `pm_capability` / `grand_design_clarity`

年ごとの更新は次のように行われます。

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

各 `_tick_...` 関数は、「その1年で何がどう変化するか」という**局所的なルール（物理法則）**を表しています。

### 3.5 DynamicsCoefficients（「物理パラメータ」）

```python
@dataclass
class DynamicsCoefficients:
    infra_to_burnout: float = 0.1
    dxclarity_to_burnout: float = 0.1
    ...
```

これらは、状態変数（例：インフラ不良）がアウトカム（例：バーンアウト）に与える影響の**重み**です。

* 経験的に校正された値ではなく、**仮説ベースのスライダー**として扱ってください。
* 係数を大きくすると → その要因がアウトカムに強く効く世界観
* 小さくすると → その要因があまり重要でない世界観

`DynamicsCoefficients` を差し替えることで、構造を変えずに

* 「インフラ重視の世界」
* 「信頼重視の世界」
* 「AI による生産性向上効果を控えめにみる世界」

など、**異なる世界観**を試すことができます。

### 3.6 StakeholderUtility（「価値レイヤー」）

```python
@dataclass
class StakeholderUtility:
    name: str
    weights: dict[str, float]
```

`SchoolEcosystem` 上の属性に重み付けをして、1つのスカラー値（スコア）に変換するための簡単な線形ユーティリティ関数です。

* シミュレーションそのものには**一切影響しません**。
* ある状態を、ある視点（教員・経営層・生徒/保護者など）からどう評価するか、という**見方の違い**を表現します。

デフォルトのユーティリティは `build_default_utilities()` に定義されています。

### 3.7 生徒の「future hope」確率

```python
def student_future_hope_probability(school, world, actor) -> float:
    ...
```

各生徒について、この関数は次を行います。

* 生徒自身の**実効適応力**と外部世界の要求水準との差（`delta`）を評価
* 学校環境から算出した **env_score** を使用：

  * 抑圧レベル
  * DX clarity
  * 生徒学習効率
  * AI へのアクセス性
* それらを**ロジスティック関数**に通して、`0〜1` の確率に変換

設計意図：

* 環境が悪くても、高い適応力を持つ生徒には **ゼロではない小さな確率**で future hope の可能性を残す。
* 環境が良く、適応力も高い場合は、確率が**数十パーセント程度**まで上がり得る。
* 実際にどの個人が future hope になるかは、確率に基づく乱数で決まるため、**運命論的な決めつけは避けられています**。

---

## 4. 初期パラメータの調整方法

デモシナリオは `build_demo_scenario()` で組み立てられ、`simulate()` から使われます（`main.py` を参照）。
ここで紹介するパラメータは、**どれも自由に変更して構いません**。

> 💡 **考え方**
> これらのパラメータは「世界がこう動くはずだ」という**あなた自身の前提**です。
> それを書き換えてみること自体が、このシミュレータの狙いの一部です。

### 4.1 シミュレーション期間とランダム性

* `simulate(years=5, seed=42)` の引数：

  * `years` を増やすと → 長期的なドリフト（10年, 20年など）が見える
  * `seed` を変えると → 同じ構造の下で**別のランダムな歴史**を観察できる
* `SchoolEcosystem` 内の `randomness` フィールド（デフォルト `0.05`）：

  * `randomness = 0.0` にすると → 完全決定論（同じ初期状態なら毎回同じ結果）
  * 値を上げると → トレンドに対するランダムな揺らぎが増える

* `trend_damping`（デフォルト `0.65`）：

  * 毎年の変化量を前年度値に向けてブレンドする係数。
  * `1.0` に近づけると急激に変化し、`0.4` 付近まで下げると非常に緩やかな推移になる。

### 4.2 外部圧力（ExternalWorld）

```python
world = ExternalWorld(selection_pressure=0.8, ai_shift_speed=0.9)
```

* `selection_pressure` / `ai_shift_speed` を上げる
  → **外の世界が厳しくなる**。再起に必要な実効適応力が高くなる。
* 下げる
  → **外が優しい世界**。外に出た教員が再起しやすくなる。

### 4.3 マクロ制約（予算 / 規制 / 人口動態）

`SchoolEcosystem` 作成直前で定義されています。

```python
env = EnvironmentConstraints(
    budget_pressure=0.6,
    regulation_rigidity=0.5,
    demographic_pressure=0.4,
)
```

* `budget_pressure`：高いほど「予算的に余裕がない世界」
* `regulation_rigidity`：高いほど「改革しづらい世界」
* `demographic_pressure`：高いほど「生徒数減少や採用難が強い世界」

これらは直接・間接に：

* イノベーションポテンシャルの伸び
* 教材資産やリポジトリの構築
* 採用難易度
* 生徒離脱率

などに影響します。

### 4.4 学校の初期状態

`SchoolEcosystem` には多くのフィールドがデフォルト値付きで定義されています。デモでは：

```python
school = SchoolEcosystem(
    name="ProtectedSchool",
    env=env,
)
```

という最低限の指定だけをしています。

任意の指標を上書きして、スタート地点を変えることができます。

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

よく効くレバーの例：

* `suppression_level`（抑圧レベル）
* `portal_maturity` / `database_foundation`（ポータル・DB）
* `process_fragmentation_index`（業務分断）
* `leadership_trust_battery` / `info_transparency`（信頼と透明性）
* `local_llm_infra_level` / `ai_accessibility_index`（AI基盤とアクセス性）

これらは初期数年の挙動や、そもそも**好循環が起こり得るかどうか**に強く影響します。

### 4.5 DynamicsCoefficients（「物理」の強さを変える）

各要因がバーンアウト・生産性・効率にどれだけ効くかを変えたい場合は、カスタム `DynamicsCoefficients` を渡します。

```python
custom_dyn = DynamicsCoefficients(
    infra_to_burnout=0.15,               # インフラの悪さの影響を強める
    workload_to_burnout=0.02,            # 業務量の影響をやや弱める
    llm_to_productivity=0.03,            # LLM効果を控えめに見る
    base_eff_infra_weight=0.5,           # 真の効率に対するインフラの重みを増やす
)

school = SchoolEcosystem(
    name="ProtectedSchool",
    env=env,
    dynamics=custom_dyn,
)
```

これにより、構造自体は変えずに「世界のルール」だけ変えることができます。

### 4.6 アクター（教職員・生徒）

`build_demo_scenario()` では、次の 2 テーブルで初期アクターを管理しています。

1. **教員・管理職 20 名**  E `ActorSpec` のリスト `core_actor_specs` に定義。レガシー系リーダー、ハイブリッド運営、ウェルネス担当、高適応教員、地域連携コーチなどを含みます。`_add_actor_specs()` がこの表をそのまま `Actor` に変換するため、キャストの調整はテーブル編集だけで済みます。
2. **生徒 100 名**  E `StudentDemographic` のリスト `student_demographics` で 9 コーホート（UrbanScholar / RuralGeneral / STEMCoder / CreativeArtist / TransferStudent / CaregiverWorker / Athlete / Activist / InternationalBridge）を定義。各コーホートが人数・OS・適応度平均/標準偏差（`[0.1, 0.95]` に clamp）・保護有無・態度確率を持ち、`_populate_student_demographics()` が命名と確率サンプリングを行います。

カスタマイズの例：

* `core_actor_specs` の行を編集して、特定ポジションを追加・削除したり適応度/保護設定を変える。
* `student_demographics` 内の人数や分布を変え、別のフィクション上の人口配分を表現する。
* 新しいコーホート（例：`EveningAdultLearner`, `ExchangeScholar` など）を追加して構成比を調整する。

これらの変更は引き続き、

* 「変化の種」量（`_tick_change_dynamics`）
* 教員側のバーンアウト／離脱パターン
* `student_future_hope_probability()` による future hope 確率

などに影響します。

### 4.7 ステークホルダーのユーティリティ（価値観）

`build_default_utilities()` では、3つの例示的な視点が定義されています。

* `TeacherPerspective`（教員視点）
* `ManagementKPIPerspective`（経営層/KPI視点）
* `StudentParentPerspective`（生徒・保護者視点）

例：

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

できること：

* 重みを変えて、現場の優先順位を反映させる
* 新しい視点（例：`RegulatorView`, `AlumniView` など）を追加する
* 学生に自分の `weights` を考えさせ、「同じ状態が視点によってどう見え方が変わるか」を比較させる

繰り返しになりますが、**ユーティリティスコアはシミュレーション結果を変えません**。
あくまで「同じ世界をどう評価するか」のためのレイヤーです。

---

## 5. 可視化ダッシュボード（PNG / PDF）

各シミュレーション実行後、`outputs/` に以下のファイルが生成されます。

- `simulation_history_page1.png`
- `simulation_history_YYYYMMDD_HHMMSS.pdf`（タイムスタンプ付きで過去のランを保存可能）

ダッシュボードには7つのパネルが含まれます。

1. **Initial parameters** – 比較用に初期状態の指標を一覧化
2. **Org health advice** – 最新スナップショットをもとに自動生成される改善アドバイス
3. **Infrastructure vs Complexity** – インフラ健全性とシステム複雑性の推移
4. **Burnout & Workload** – バーンアウト指数と業務負荷の推移
5. **Student outcomes** – 生徒離脱率と学習効率の推移
6. **Productivity & Efficiency** – 実際の生産性と真/認識効率の推移
7. **Future hope output** – future hope 期待人数（確率モデルに基づく）の推移

複数回の実行を比較したい場合は PDF をめくり、レポートやスライドに貼る際は PNG を利用してください。

---

## 6. おすすめの利用フロー（探索・ワークショップ向け）

1. **まずはデフォルトシナリオを一度回す**

   ```bash
   python main.py
   ```

   * 初期サマリーと最終サマリーをざっと眺める
   * スタッフが外部世界で生き残れるかの表を確認
   * future hope の人数や、各ステークホルダスコアを見る

2. **「何を変えたらどうなりそうか」という仮説を1つ決める**

   例：

   * 「抑圧は低いが、インフラがとても弱い世界」
   * 「AI基盤は強いが、PMが弱く信頼も低い世界」
   * 「予算圧力が極端に高いが、リーダーシップが強い世界」

3. **該当パラメータを編集する**

   * `build_demo_scenario()` 内で：

     * `SchoolEcosystem` の初期インデックスを変更
     * `EnvironmentConstraints` を調整
     * `ExternalWorld` を変更
     * 必要なら `DynamicsCoefficients` をカスタム版に差し替え
   * 必要に応じてアクター構成（特に生徒分布と高適応教員）を変える

4. **再実行し、前後を比較する**

   * `python main.py` または `simulate(...)` を再度実行
   * 次のような指標を比較：

     * `burnout_index`, `student_exit_rate`
     * `efficiency_index_true` vs `efficiency_index_recognized`
     * future hope 生徒数
     * 各ステークホルダーのスコア

5. **面白いシナリオをパターンとして保存する**

   * `build_optimistic_scenario()`
   * `build_pessimistic_scenario()`
   * `build_high_trust_low_budget_scenario()`
     のように、関数名で世界観を分けてしまうと、授業やワークショップで比較しやすくなります。

---

## 7. 解釈・安全面での注意

誤解を避けるためのポイントです。

* このコードは**道徳的判定器ではありません**。
* 現実の誰かを指して「この人は残るべき／出るべき」と判断するためのものではありません。
* 実在の学校や組織の将来を**予測するツール**でもありません。

このシミュレータは、あくまで：

* 構造（インフラ・DXの明確さ・PM・信頼・抑圧）と、
* 外的制約（予算・規制・選択圧）が、
* 個々人の適応力と選択にどう絡み合い得るか

を考えるための**比喩的モデル**です。

授業やワークショップで使う場合は、次の点を強調するとよいでしょう。

* **パラメータを書き換えること自体が学習の一部**であること
* 参加者に：

  * デフォルト係数へのツッコミ
  * 代替となるダイナミクス案の提案
  * 自分なりのステークホルダー・ユーティリティの設計
    をさせ、「自分は世界のどこに重きを置いているのか」を言語化させること

---

## 8. シミュレータの拡張アイデア

コアはプレーンな Python + dataclass だけで構成されているので、拡張は容易です。

* `SchoolEcosystem` に新しい指標を追加
  例：`mentoring_index`, `community_support_index` など
* 新しい `_tick_...` 関数を追加し、その指標をダイナミクスに組み込む
* ファイルが長くなってきたら、以下のように分割：

  * `models.py`（Actor, SchoolEcosystem, ExternalWorld, EnvironmentConstraints）
  * `dynamics.py`（各 `_tick_...`）
  * `reporting.py`（summary・print系）
* print ベースの出力を：

  * JSON 出力
  * グラフ描画
  * パラメータをGUIでいじれる簡易Web UI
    などに差し替えると、より対話的な教材にもなります。

このシミュレータは、次のような用途への**フォーク前提**で設計されています。

* 授業・ワークショップ
* ブログ記事・技術ノート
* 組織の技術的負債や適応圧について考えるためのミニツール
* あるいは純粋な個人的思考実験

ここで重要なのは、**数値そのものの正しさ**ではなく、
それらの数値を動かしながら議論するときに生まれる**問いや対話**です。

---

### 9.1 エビデンスとのゆるやかな整合性（日本語メモ）

このシミュレータは、実データから係数を推定した「予測モデル」ではなく、研究でよく出てくる傾向をざっくり反映した **思考実験モデル** です。

- 教員の仕事要求・バーンアウト・離職  
  メタ分析では、長時間労働や業務負担などの「仕事要求」はストレスやバーンアウトを高め、自律性やサポートなどの「仕事資源」はウェルビーイングと職業コミットメントを高めると報告されています（Li ら, 2025 など）。本モデルの `workload_index` や `burnout_index` の関係はこの方向性をなぞったものです。

- リーダーシップ・信頼・学校風土  
  不透明で権威主義的なマネジメントはウェルビーイングと定着を悪化させ、透明性が高く支援的なリーダーシップは信頼と定着を高めるという研究が多く報告されています（Flores & Shuls, 2024; Li, 2024; Education Support, 2025 など）。`suppression_level` や `leadership_trust_battery` の扱いはこの辺りを抽象化しています。

- DX／ICT とテクノストレス  
  複数の ICT ツールの同時利用や常時オンライン状態が、教員のテクノストレス・健康問題・ワークライフバランス悪化と関連することが示されています（Yang ら, 2025; Rey-Merchán ら, 2022; Wang ら, 2023, 2025 など）。`external_system_dependency` や `system_complexity` が上がると負担とバーンアウトが増える設計は、これをモデル化したものです。

- AI / LLM ツール  
  AI はうまく設計すればルーティン業務の軽減や個別化学習の支援になりうる一方で、新たなスキル要求や倫理的懸念も伴う二面性を持つとされています（Tan ら, 2024; Younas, 2025 など）。本モデルでは、インフラと設計が整った場合にのみ `local_llm_infra_level` などがプラスに効くようにしており、「魔法の杖」扱いはしていません。

- 教員バーンアウトと生徒アウトカム  
  系統的レビューでは、教員バーンアウトが学力や動機づけの質の低下と関連する一方で、どんな環境でも一部の生徒は高い成果を上げることも指摘されています（Madigan & Kim, 2021 など）。このアイデアが `student_future_hope_probability` に反映されており、悪い環境でも「小さながら 0 ではない future hope」、良い環境では「それなりの比率の future hope」が出るようになっています。

数値自体は「仮のつまみ」であり、**どのつまみをどれくらい動かしたときに何が起きるかを議論するための道具**として設計されています。
ワークショップで比較しやすくなります。

---
