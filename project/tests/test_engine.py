import sys; sys.path.insert(0, "src")
from engine import evaluate, fork

def allowed(f): return sorted(g for g, o in evaluate(f).items() if o["status"] == "allowed")

BASE = dict(is_dairy_egg_honey=False, named_elsewhere_other=False, is_enzyme_preparation=False,
            is_medical_purpose=False, is_intravenous_nutrition=False,
            is_2101_2105_product=False, is_listed_in_0410=False, is_listed_in_2106=False)

CASES = {
 "замороженная тушка курицы":        (dict(BASE, is_food_purpose=True, is_edible=True, is_animal_origin=True, is_meat=True,
                                          processing_state="frozen", meat_share_pct=100), ["02"]),
 "варёные куриные котлеты, 60% мяса": (dict(BASE, is_food_purpose=True, is_edible=True, is_animal_origin=True, is_meat=True,
                                          processing_state="cooked", meat_share_pct=60), ["16"]),
 "готовое блюдо, 10% мяса":          (dict(BASE, is_food_purpose=True, is_edible=True, is_animal_origin=False, is_meat=True,
                                          processing_state="cooked", meat_share_pct=10), ["21"]),
 "вакцина":                          (dict(BASE, is_food_purpose=False, is_edible=False, is_animal_origin=False, is_meat=False,
                                          is_medical_purpose=True, processing_state="other_prepared", meat_share_pct=0), ["30"]),
 "БАД с витаминами без лечебных заявлений": (dict(BASE, is_food_purpose=True, is_edible=True, is_animal_origin=False, is_meat=False,
                                          processing_state="other_prepared", meat_share_pct=0), ["21"]),
 "сыр":                              (dict(BASE, is_food_purpose=True, is_edible=True, is_animal_origin=True, is_meat=False,
                                          is_dairy_egg_honey=True, processing_state="other_prepared", meat_share_pct=0), ["04"]),
}
if __name__ == "__main__":
    bad = 0
    for name, (f, exp) in CASES.items():
        got = allowed(f); ok = got == exp; bad += not ok
        print(("OK  " if ok else "FAIL"), name, "| ожидали", exp, "| получили", got)
    print("Провалено:", bad)
