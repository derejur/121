"""Стартовый набор C: примеры, прямо названные в приложенных Пояснениях (source_type=explanatory).
ВАЖНО: правила движка выписаны из тех же текстов, поэтому проверка на этом наборе = тест согласованности, а не оценка точности."""
import sys, csv, json; sys.path.insert(0, "src")
from engine import evaluate

B = dict(is_food_purpose=True, is_edible=True, is_animal_origin=False, is_medical_purpose=False,
         is_intravenous_nutrition=False, is_enzyme_preparation=False, has_proteolytic_enzymes=False,
         is_dairy_egg_honey=False, is_2101_2105_product=False, is_listed_in_0410=False, is_listed_in_2106=False,
         named_elsewhere_other=False, is_meat=False, processing_state="other_prepared", meat_share_pct=0)
def M(state, share=100, **k): return dict(B, is_animal_origin=True, is_meat=True, processing_state=state, meat_share_pct=share, **k)
def MED(**k): return dict(B, is_food_purpose=False, is_edible=False, is_medical_purpose=True, **k)

# id, описание, источник (Пояснения), ожидаемые группы (пусто = вне 02/04/16/21/30), ожидаемая позиция, признаки
S = [
 ("S01","Говяжья туша свежая","Пояснения к 0201",["02"],"0201",M("fresh")),
 ("S02","Замороженная свинина","Пояснения к 0203",["02"],"0203",M("frozen")),
 ("S03","Замороженное мясо кролика","Пояснения к 0208",["02"],"0208",M("frozen")),
 ("S04","Копчёная грудинка (бекон)","Пояснения к 0210",["02"],"0210",M("smoked")),
 ("S05","Замороженные говяжьи языки","Пояснения к 0206",["02"],"0206",M("frozen")),
 ("S06","Свежее мясо, обработанное папаином","Общие положения к гр. 02",["02"],"0201-0210",M("fresh", has_proteolytic_enzymes=True)),
 ("S07","Сырой фарш без других ингредиентов","Пояснения к 1601, искл. (б)",["02"],"0201-0210",M("chilled")),
 ("S08","Мясо, отваренное или жареное","Пояснения к 1602 (1)",["16"],"1602",M("cooked")),
 ("S09","Колбаса салями","Пояснения к 1601 (1)",["16"],"1601",M("other_prepared")),
 ("S10","Мясо в панировке","Пояснения к 1602 (3)",["16"],"1602",M("other_prepared")),
 ("S11","Готовое блюдо, 30% мяса","Пояснения к 1602 (5)",["16"],"1602",dict(B, is_meat=True, meat_share_pct=30, processing_state="cooked")),
 ("S12","Мясной экстракт","Пояснения к 1603",["16"],"1603",M("other_prepared")),
 ("S13","Гомогенизированное детское пюре из мяса","Прим. к субпозициям 1 к гр. 16",["16"],"1602 10",M("other_prepared")),
 ("S14","Гомогенизированное детское пюре мясо+овощи, до 250 г","Прим. 3 к гр. 21",["21"],"2104 20",dict(B, is_meat=True, meat_share_pct=40, processing_state="other_prepared", is_2101_2105_product=True)),
 ("S15","Готовый суп с мясом","Пояснения к 2104",["21"],"2104 10",dict(B, is_meat=True, meat_share_pct=25, processing_state="cooked", is_2101_2105_product=True)),
 ("S16","Соевый соус","Пояснения к 2103",["21"],"2103 10",dict(B, is_2101_2105_product=True)),
 ("S17","Томатный кетчуп","Пояснения к 2103",["21"],"2103 20",dict(B, is_2101_2105_product=True)),
 ("S18","Растворимый кофе","Пояснения к 2101",["21"],"2101",dict(B, is_2101_2105_product=True)),
 ("S19","Пекарные дрожжи","Пояснения к 2102",["21"],"2102",dict(B, is_2101_2105_product=True)),
 ("S20","Неживые одноклеточные микроорганизмы (биомасса)","Пояснения к 2102 (Б)",["21"],"2102 20",dict(B, is_2101_2105_product=True)),
 ("S21","Мороженое на молочной основе","Пояснения к 2105",["21"],"2105",dict(B, is_animal_origin=True, is_2101_2105_product=True)),
 ("S22","Текстурированный соевый белок","Пояснения к 2106 (6)",["21"],"2106 10",dict(B)),
 ("S23","Автолизированные дрожжи","Пояснения к 2106 (11)",["21"],"2106",dict(B)),
 ("S24","Витаминная пищевая добавка без заявлений о лечении","Пояснения к 2106 (16), 3003",["21"],"2106",dict(B)),
 ("S25","Травяной чай/настой без лечебной дозы","Пояснения к 2106 (14)",["21"],"2106",dict(B)),
 ("S26","Яичный продукт с пряностями","Пояснения к 0408, искл. (б)",["21"],"2106",dict(B, is_animal_origin=True, is_listed_in_2106=True)),
 ("S27","Вакцина для людей","Пояснения к 3002 (Г)",["30"],"3002 20",MED()),
 ("S28","Иммунная сыворотка","Пояснения к 3002 (В)",["30"],"3002 12",MED()),
 ("S29","Моноклональные антитела","Пояснения к 3002 (В)(2)",["30"],"3002 13-15",MED()),
 ("S30","Таблетки, расфасованные в дозах","Пояснения к 3004",["30"],"3004",MED()),
 ("S31","Реагенты для определения группы крови","Пояснения к 3006 (5)",["30"],"3006 20",MED()),
 ("S32","Молоко","Пояснения к 0401",["04"],"0401",dict(B, is_animal_origin=True, is_dairy_egg_honey=True)),
 ("S33","Йогурт","Пояснения к 0403",["04"],"0403 10",dict(B, is_animal_origin=True, is_dairy_egg_honey=True)),
 ("S34","Сливочное масло","Пояснения к 0405",["04"],"0405 10",dict(B, is_animal_origin=True, is_dairy_egg_honey=True)),
 ("S35","Сыр","Пояснения к 0406",["04"],"0406",dict(B, is_animal_origin=True, is_dairy_egg_honey=True)),
 ("S36","Яйца в скорлупе","Пояснения к 0407",["04"],"0407",dict(B, is_animal_origin=True, is_dairy_egg_honey=True)),
 ("S37","Натуральный мёд","Пояснения к 0409",["04"],"0409",dict(B, is_animal_origin=True, is_dairy_egg_honey=True)),
 ("S38","Черепашьи яйца","Пояснения к 0410 (1)",["04"],"0410",dict(B, is_animal_origin=True, is_listed_in_0410=True)),
 ("S39","Съедобные гнёзда салангана","Пояснения к 0410 (2)",["04"],"0410",dict(B, is_animal_origin=True, is_listed_in_0410=True)),
 ("S40","Ферментный препарат для тендеризации мяса","Пояснения к 2106, искл. (3507)",[],"3507",dict(B, is_enzyme_preparation=True)),
 ("S41","Продукт из сыворотки, более 95% лактозы","Прим. 4(а) к гр. 04 (1702)",[],"1702",dict(B, is_animal_origin=True, named_elsewhere_other=True)),
]

if __name__ == "__main__":
    ok = 0; rows = []
    for sid, desc, src, exp, head, f in S:
        got = sorted(g for g, o in evaluate(f).items() if o["status"] == "allowed")
        good = got == sorted(exp); ok += good
        rows.append([sid, desc, src, "explanatory", ",".join(exp) or "вне 02/04/16/21/30", head, ",".join(got) or "-", "OK" if good else "РАСХОЖДЕНИЕ", json.dumps(f, ensure_ascii=False)])
        if not good: print("РАСХОЖДЕНИЕ", sid, desc, "| ожидали", exp, "| получили", got)
    print(f"Согласованность: {ok}/{len(S)}")
    with open("data/processed/examples_seed.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh); w.writerow(["id","description","source_ref","source_type","expected_groups","expected_heading","engine_groups","check","features_json"]); w.writerows(rows)
