"""
Движок правил ТН ВЭД (прототип, уровень 2-значных групп: 02, 04, 16, 21, 30).
Трёхзначная логика: True / False / None (None = «в описании товара не сказано»
или «нужна юридическая трактовка»). Никаких вероятностей: только вывод по правилам
с трассой (какое правило сработало, откуда оно взято).
"""
import itertools
import pandas as pd
import networkx as nx

# ---------- трёхзначная логика ----------
def NOT(a):  return None if a is None else (not a)
def AND(*a):
    if any(x is False for x in a): return False
    if any(x is None for x in a):  return None
    return True
def OR(*a):
    if any(x is True for x in a):  return True
    if any(x is None for x in a):  return None
    return False
def GT(x, t): return None if x is None else x > t

STATES_G02 = {"fresh", "chilled", "frozen", "salted", "dried", "smoked"}
STATES_PREPARED = {"cooked", "canned", "other_prepared"}

# ---------- производные признаки ----------
def derive(f):
    d = dict(f)
    st = d.get("processing_state")
    if st in STATES_G02:        d["state_matches_group02"] = True
    elif st in STATES_PREPARED: d["state_matches_group02"] = False
    else:                       d["state_matches_group02"] = d.get("state_matches_group02")  # None или явная развилка
    d["is_prepared"] = NOT(d["state_matches_group02"])
    share = d.get("meat_share_pct")
    # доля «мяса» имеет смысл, только если компонент признан мясом
    d["meat_gt20"] = AND(d.get("is_meat"), GT(share, 20)) if d.get("is_meat") is not False else False
    d["named_elsewhere"] = OR(
        AND(d.get("is_meat"), d["state_matches_group02"]),   # 0201-0210
        AND(d["is_prepared"], d["meat_gt20"], NOT(d.get("is_2101_2105_product"))),  # 1601/1602
        d.get("is_dairy_egg_honey"),                         # 0401-0409
        d.get("is_2101_2105_product"),                       # 2101-2105
        d.get("is_listed_in_0410"),                          # перечень пояснений к 0410
        d.get("named_elsewhere_other"))                      # прочее: вводит эксперт
    d["named_for_0410"] = OR(d["named_elsewhere"], d.get("is_listed_in_2106"))
    return d

# ---------- правила ----------
# effect: "block"  -> если pred True, группа исключается
#         "require"-> если pred False, группа исключается
#         "note"   -> справочно, на вывод не влияет
RULES = [
 # группа 30
 dict(id="N30_1a", group="30", effect="block", src="Прим. 1(а) к гр. 30",
      text="Гр. 30 не включает пищевые продукты или напитки (кроме питательных препаратов для внутривенного введения)",
      pred=lambda x: AND(x.get("is_food_purpose"), NOT(x.get("is_intravenous_nutrition")))),
 dict(id="S30_scope", group="30", effect="require", src="Наименование гр. 30 / Пояснения к 3001-3006",
      text="Гр. 30 = фармацевтическая продукция: нужно лечебное, профилактическое или диагностическое назначение",
      pred=lambda x: OR(x.get("is_medical_purpose"), x.get("is_intravenous_nutrition"))),
 # группа 02
 dict(id="N02_1a", group="02", effect="block", src="Прим. 1(а) к гр. 02",
      text="Непригодные для употребления в пищу продукты не входят в гр. 02",
      pred=lambda x: NOT(x.get("is_edible"))),
 dict(id="S02_title", group="02", effect="require", src="Наименование гр. 02",
      text="Гр. 02 = мясо и пищевые мясные субпродукты: компонент должен быть «мясом»",
      pred=lambda x: x.get("is_meat")),
 dict(id="E02_states", group="02", effect="require", src="Общие положения к гр. 02",
      text="В гр. 02 мясо только в состояниях: свежее, охлаждённое, замороженное, солёное/в рассоле/сушёное/копчёное; не приготовленное",
      pred=lambda x: x["state_matches_group02"]),
 dict(id="E02_enzymes", group="02", effect="note", src="Общие положения к гр. 02",
      text="Обработка протеолитическими ферментами и измельчение мясо из гр. 02 НЕ выводят",
      pred=lambda x: x.get("has_proteolytic_enzymes")),
 # группа 16
 dict(id="N16_1", group="16", effect="block", src="Прим. 1 к гр. 16",
      text="Мясо, приготовленное способами гр. 02, в гр. 16 не включается",
      pred=lambda x: AND(x.get("is_meat"), x["state_matches_group02"])),
 dict(id="N16_2b", group="16", effect="block", src="Прим. 2 к гр. 16",
      text="Продукты с начинкой 1902 и готовые продукты 2103/2104 в гр. 16 не включаются",
      pred=lambda x: x.get("is_2101_2105_product")),
 dict(id="N16_2", group="16", effect="require", src="Прим. 2 к гр. 16",
      text="Готовые продукты входят в гр. 16, если содержат более 20 мас.% мяса и т.п.",
      pred=lambda x: x["meat_gt20"]),
 # группа 21
 dict(id="N21_1d", group="21", effect="block", src="Прим. 1(д) к гр. 21",
      text="Готовые пищевые продукты с более чем 20 мас.% мяса относятся к гр. 16",
      pred=lambda x: AND(x["is_prepared"], x["meat_gt20"], NOT(x.get("is_2101_2105_product")))),
 dict(id="N21_1g", group="21", effect="block", src="Прим. 1(ж) к гр. 21",
      text="Ферментные препараты (3507) не входят в гр. 21",
      pred=lambda x: x.get("is_enzyme_preparation")),
 dict(id="N21_1e", group="21", effect="block", src="Прим. 1(е) к гр. 21",
      text="Лекарственные средства (3003/3004) не входят в гр. 21",
      pred=lambda x: x.get("is_medical_purpose")),
 dict(id="E2106_food", group="21", effect="require", src="Наименование поз. 2106",
      text="2106: пищевой продукт",
      pred=lambda x: x.get("is_food_purpose")),
 dict(id="E2106_cond", group="21", effect="block", src="Пояснения к поз. 2106",
      text="2106 только если продукт не поименован и не включён ни в какую другую позицию",
      pred=lambda x: AND(x["named_elsewhere"], NOT(x.get("is_2101_2105_product")))),
 # группа 04 (для прототипа: молочные/яйца/мёд, либо остаточная поз. 0410)
 dict(id="S04_scope", group="04", effect="require", src="Наименование гр. 04; Пояснения к 0410",
      text="Гр. 04: молочные продукты, яйца, мёд ИЛИ съедобный продукт животного происхождения, нигде более не поименованный (0410)",
      pred=lambda x: OR(x.get("is_dairy_egg_honey"), x.get("is_listed_in_0410"),
                        AND(x.get("is_food_purpose"), x.get("is_animal_origin"), NOT(x["named_for_0410"])))),
]

def evaluate(features):
    x = derive(features)
    out = {}
    for g in ["02", "04", "16", "21", "30"]:
        status, trace = "allowed", []
        for r in [r for r in RULES if r["group"] == g]:
            v = r["pred"](x)
            if r["effect"] == "block":      hit, unk = v is True, v is None
            elif r["effect"] == "require":  hit, unk = v is False, v is None
            else:                           hit, unk = False, False
            if r["effect"] == "note":
                if v is True: trace.append((r["id"], r["src"], "справочно: " + r["text"]))
                continue
            if hit:
                status = "blocked"; trace.append((r["id"], r["src"], "БЛОК: " + r["text"]))
            elif unk:
                if status != "blocked": status = "conditional"
                trace.append((r["id"], r["src"], "НЕ ЯСНО: " + r["text"]))
        out[g] = dict(status=status, trace=trace)
    # блок сильнее «не ясно»: пересчёт
    for g, o in out.items():
        if any(t[2].startswith("БЛОК") for t in o["trace"]): o["status"] = "blocked"
    return out

def fork(features, unknowns):
    """Перебор трактовок неопределённых булевых признаков."""
    rows = []
    for combo in itertools.product([True, False], repeat=len(unknowns)):
        f = dict(features); f.update(dict(zip(unknowns, combo)))
        res = evaluate(f)
        rows.append((dict(zip(unknowns, combo)),
                     [g for g, o in res.items() if o["status"] == "allowed"]))
    return rows

def load_graph(nodes_csv="data/processed/tnved_nodes.csv", edges_csv="data/processed/tnved_edges.csv"):
    n = pd.read_csv(nodes_csv, dtype=str).fillna("")
    e = pd.read_csv(edges_csv, dtype=str)
    G = nx.DiGraph()
    for r in n.itertuples(): G.add_node(r.code, level=r.level, name=r.name)
    G.add_edges_from(zip(e.parent, e.child))
    return G

def candidate_items(G, group):
    return [c for c in nx.descendants(G, group) if G.nodes[c]["level"] == "item"]
