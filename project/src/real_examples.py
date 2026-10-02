"""
Набор C (v1, реальные данные): решения о классификации, тексты которых удалось
найти в открытом доступе (зеркала: garant.ru, tks.ru, tws.by, alta.ru).
Это НЕЗАВИСИМАЯ проверка движка: эти решения не использовались при написании правил.
"""
import sys, csv, json; sys.path.insert(0, "src")
from engine import evaluate

B = dict(is_food_purpose=True, is_edible=True, is_animal_origin=False, is_medical_purpose=False,
         is_intravenous_nutrition=False, is_enzyme_preparation=False, has_proteolytic_enzymes=False,
         is_dairy_egg_honey=False, is_2101_2105_product=False, is_listed_in_0410=False, is_listed_in_2106=False,
         named_elsewhere_other=False, is_meat=False, processing_state="other_prepared", meat_share_pct=0)

REAL = [
 dict(id="R01", decision="Решение Коллегии ЕЭК № 57 от 16.04.2019",
      url="https://www.garant.ru/products/ipo/prime/doc/72128840/",
      description="Мясной полуфабрикат «котлета из говядины»: измельчённое, формованное и замороженное "
                  "обваленное мясо КРС, без соли или с солью <1,2 мас.%, БЕЗ термической обработки.",
      opi_in_decision="ОПИ 1 и 6", expected_code="0202 30",
      features=dict(B, is_animal_origin=True, is_meat=True, processing_state="frozen", meat_share_pct=100)),
 dict(id="R02", decision="Решение Коллегии ЕЭК № 165 от 08.12.2020",
      url="https://www.tks.ru/news/law/2020/12/09/0012",
      description="Мясной сыровяленый продукт: окорок свиной туши, посол солью и др. ингредиентами (сахара, "
                  "нитраты/нитриты, аскорбат натрия), сушка и созревание (ферментация) до готовности к "
                  "непосредственному употреблению; соль ≥1,2 мас.%.",
      opi_in_decision="ОПИ 1", expected_code="0210",
      features=dict(B, is_animal_origin=True, is_meat=True, processing_state="dried", meat_share_pct=100)),
 dict(id="R03", decision="Решение Коллегии ЕЭК № 44 от 28.03.2023, п.3",
      url="https://www.alta.ru/tamdoc/23kr0044/",
      description="Поливитаминный комплекс: смесь витаминов + вкусо-ароматические, питательные и др. вещества "
                  "(кроме для в/в введения), для сбалансированного дополнения питания взрослых, дозы витаминов "
                  "не выше верхнего допустимого уровня потребления.",
      opi_in_decision="ОПИ 1", expected_code="2106",
      features=dict(B, is_medical_purpose=False)),
]

if __name__ == "__main__":
    rows = []
    for r in REAL:
        res = evaluate(r["features"])
        allowed = sorted(g for g, o in res.items() if o["status"] == "allowed")
        cond = sorted(g for g, o in res.items() if o["status"] == "conditional")
        exp_g = r["expected_code"][:2]
        match = exp_g in allowed
        rows.append([r["id"], r["decision"], r["url"], r["description"], r["opi_in_decision"],
                     r["expected_code"], ",".join(allowed), ",".join(cond),
                     "СОВПАДАЕТ" if match else "РАСХОЖДЕНИЕ", json.dumps(r["features"], ensure_ascii=False)])
        print(r["id"], r["decision"], "| ожидаемая группа:", exp_g, "| движок допустил:", allowed,
              "|", "OK" if match else "MISMATCH")
    with open("data/processed/examples_real_v1.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id","decision","url","description","opi_in_decision","expected_code",
                    "engine_allowed_groups","engine_conditional_groups","check","features_json"])
        w.writerows(rows)
