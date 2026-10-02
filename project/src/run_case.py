import sys; sys.path.insert(0, "src")
from engine import evaluate, fork, load_graph, candidate_items

CASE = dict(
    is_food_purpose=True, is_edible=True, is_animal_origin=True, is_cell_cultivated=True,
    is_medical_purpose=False, is_intravenous_nutrition=False, is_enzyme_preparation=False,
    has_proteolytic_enzymes=False,      # трансглутаминаза = связующее, не протеолитический фермент
    is_dairy_egg_honey=False,
    is_meat=None,                        # ЮРИДИЧЕСКИЙ ВОПРОС: считается ли клеточная масса «мясом»
    processing_state="formed_with_additives",  # не входит в перечень состояний гр. 02 и не «приготовлен» явно -> None
    meat_share_pct=85,                   # доля клеточной массы (из описания); учитывается, только если is_meat=True
    is_2101_2105_product=False, is_listed_in_0410=False, is_listed_in_2106=False,
    named_elsewhere_other=False,         # допущение: иных позиций, где продукт поименован, нет
)
G = load_graph()
res = evaluate(CASE)
L = ["# Отчёт: Formed Cell-cultivated Chicken (прототип, уровень групп)\n",
     "Входные признаки: " + ", ".join(f"`{k}={v}`" for k, v in CASE.items()) + "\n",
     "## 1. Вердикт по группам\n", "| Группа | Статус | Кандидатов (10-знач. кодов) |", "|---|---|---|"]
names = {"blocked": "исключена", "conditional": "зависит от трактовки", "allowed": "допустима"}
for g, o in res.items():
    L.append(f"| {g} | {names[o['status']]} | {len(candidate_items(G, g))} |")
L.append("\n## 2. Трасса правил\n")
for g, o in res.items():
    L.append(f"**Группа {g}: {names[o['status']]}**")
    for rid, src, msg in o["trace"] or [("-", "-", "правила не сработали")]:
        L.append(f"- `{rid}` ({src}): {msg}")
    L.append("")
L.append("## 3. Развилка по открытым юридическим вопросам\n")
L.append("Вопрос A: признаётся ли клеточная масса «мясом» (`is_meat`). Вопрос B: соответствует ли продукт состояниям гр. 02, а не «приготовленному» (`state_matches_group02`).\n")
L.append("| A: мясо? | B: состояние как в гр. 02? | Допустимые группы |"); L.append("|---|---|---|")
for a, groups in fork(CASE, ["is_meat", "state_matches_group02"]):
    L.append(f"| {'да' if a['is_meat'] else 'нет'} | {'да' if a['state_matches_group02'] else 'нет'} | {', '.join(groups) or '-'} |")
L.append("\nПри A = «нет» остаются 04 (поз. 0410) и 21 (поз. 2106): обе остаточные («нигде более не поименованные»). "
         "В приложенных текстах критерия выбора между ними нет, нужны ОПИ 3 и экспертная оценка.")
open("reports/case_cell_chicken.md", "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))
