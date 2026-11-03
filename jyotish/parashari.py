"""Parashari layer: graha drishti, functional nature by lagna, and core yogas."""
from __future__ import annotations

from .chart import Chart, SIGN_LORDS, SIGNS

# Full special aspects, counted inclusively from the planet's own house.
# Every graha aspects the 7th; Mars, Jupiter and Saturn add their special aspects.
# Rahu/Ketu get only the 7th here; many teachers add 5th and 9th (change NODE_ASPECTS).
SPECIAL = {"Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10]}
NODE_ASPECTS = [7]
KENDRA, TRIKONA, DUSTHANA, UPACHAYA_BAD = {1, 4, 7, 10}, {1, 5, 9}, {6, 8, 12}, {3, 6, 11}
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Moolatrikona: sign index and degree range.
MOOLATRIKONA = {"Sun": (4, 0, 20), "Moon": (1, 3, 30), "Mars": (0, 0, 12), "Mercury": (5, 15, 20),
                "Jupiter": (8, 0, 10), "Venus": (6, 0, 15), "Saturn": (10, 0, 20)}
MAHAPURUSHA = {"Mars": "Ruchaka", "Mercury": "Bhadra", "Jupiter": "Hamsa", "Venus": "Malavya",
               "Saturn": "Sasa"}


def aspect_houses(planet: str, house: int) -> list[int]:
    offsets = NODE_ASPECTS if planet in ("Rahu", "Ketu") else SPECIAL.get(planet, [7])
    return sorted((house + o - 2) % 12 + 1 for o in offsets)


def _p(chart: Chart) -> dict:
    return {p.name: p for p in chart.planets}


def _lord_of(chart: Chart, house: int) -> str:
    return SIGN_LORDS[(chart.lagna.sign_index + house - 1) % 12]


def aspects(chart: Chart) -> list[dict]:
    """Which houses (and the planets in them) each graha aspects."""
    out = []
    for p in chart.planets:
        for h in aspect_houses(p.name, p.house):
            targets = [q.name for q in chart.planets if q.house == h and q.name != p.name]
            out.append({"planet": p.name, "house": h, "planets": targets})
    return out


def aspects_between(chart: Chart, a: str, b: str) -> bool:
    P = _p(chart)
    return P[b].house in aspect_houses(a, P[a].house)


def is_moolatrikona(planet: str, lon: float) -> bool:
    mt = MOOLATRIKONA.get(planet)
    return bool(mt) and int(lon // 30) == mt[0] and mt[1] <= lon % 30 < mt[2]


def functional_nature(chart: Chart) -> dict[str, str]:
    """Functional benefic/malefic for this lagna, by house lordship (Parashari principles)."""
    out = {}
    for name in SEVEN:
        owned = {h for h in range(1, 13) if _lord_of(chart, h) == name}
        kendra = owned & {4, 7, 10}
        trikona = owned & TRIKONA
        bad = owned & {3, 6, 11}
        eighth = 8 in owned and 1 not in owned and name not in ("Sun", "Moon")
        if kendra and (owned & {5, 9}):
            nature = "yogakaraka"
        elif trikona and not bad and not eighth:
            nature = "functional benefic"
        elif (bad or eighth) and not trikona:
            nature = "functional malefic"
        elif trikona and (bad or eighth):
            nature = "mixed"
        elif kendra and name in NATURAL_BENEFICS:
            nature = "neutral (kendradhipati dosha)"
        else:
            nature = "neutral"
        out[name] = nature
    return out


def yogas(chart: Chart) -> list[dict]:
    P = _p(chart)
    moon_h = P["Moon"].house
    found = []

    def add(name, why, planets):
        found.append({"name": name, "description": why, "planets": planets})

    def from_moon(h):
        return (h - moon_h) % 12 + 1

    # Pancha Mahapurusha
    for pl, yname in MAHAPURUSHA.items():
        p = P[pl]
        if p.house in KENDRA and p.dignity in ("own sign", "exalted", "moolatrikona"):
            add(f"{yname} yoga", f"{pl} {p.dignity} in house {p.house} (a kendra)", [pl])

    # Gajakesari
    if from_moon(P["Jupiter"].house) in KENDRA:
        add("Gajakesari yoga", f"Jupiter in house {from_moon(P['Jupiter'].house)} from the Moon", ["Jupiter", "Moon"])
    if P["Sun"].sign == P["Mercury"].sign:
        add("Budhaditya yoga", f"Sun and Mercury together in {P['Sun'].sign}", ["Sun", "Mercury"])
    if P["Moon"].sign == P["Mars"].sign:
        add("Chandra-Mangala yoga", f"Moon and Mars together in {P['Moon'].sign}", ["Moon", "Mars"])

    # Parivartana (sign exchange)
    seen = set()
    for a in SEVEN:
        b = SIGN_LORDS[P[a].sign_index]
        if b != a and b in SEVEN and SIGN_LORDS[P[b].sign_index] == a and (b, a) not in seen:
            seen.add((a, b))
            add("Parivartana yoga", f"{a} and {b} exchange signs ({P[a].sign} / {P[b].sign}), "
                f"linking houses {P[a].house} and {P[b].house}", [a, b])

    # Raja yoga: a kendra lord and a trikona lord related by conjunction, mutual aspect or exchange.
    lords = {h: _lord_of(chart, h) for h in range(1, 13)}
    pairs = set()
    for k in (1, 4, 7, 10):
        for t in (1, 5, 9):
            a, b = lords[k], lords[t]
            if a == b or k == t:
                continue
            key = tuple(sorted((a, b)))
            if key in pairs:
                continue
            how = None
            if P[a].sign == P[b].sign:
                how = f"together in house {P[a].house}"
            elif aspects_between(chart, a, b) and aspects_between(chart, b, a):
                how = "in mutual aspect"
            elif SIGN_LORDS[P[a].sign_index] == b and SIGN_LORDS[P[b].sign_index] == a:
                how = "exchanging signs"
            if how:
                pairs.add(key)
                add("Raja yoga", f"{a} (lord of {k}) and {b} (lord of {t}) {how}", [a, b])
    for name, nature in functional_nature(chart).items():
        if nature == "yogakaraka":
            add("Yogakaraka", f"{name} owns both a kendra and a trikona for {chart.lagna.sign} lagna "
                f"(placed in house {P[name].house})", [name])

    # Dhana yoga: lords of 2/11 linked with lords of 5/9 by conjunction.
    for w in (2, 11):
        for t in (5, 9):
            a, b = lords[w], lords[t]
            if a != b and P[a].sign == P[b].sign:
                add("Dhana yoga", f"{a} (lord of {w}) with {b} (lord of {t}) in house {P[a].house}", [a, b])

    # Vipareeta Raja yoga: dusthana lord in a dusthana.
    for h, yname in ((6, "Harsha"), (8, "Sarala"), (12, "Vimala")):
        l = lords[h]
        if P[l].house in DUSTHANA and not ({h for h in range(1, 13) if lords[h] == l} & {1}):
            add(f"Vipareeta Raja yoga ({yname})", f"{l}, lord of {h}, sits in house {P[l].house}", [l])

    # Neecha Bhanga (simplified): lord of the debilitation sign, or of the exaltation sign,
    # in a kendra from lagna or Moon.
    for pl in SEVEN:
        p = P[pl]
        if p.dignity != "debilitated":
            continue
        exalt_sign = (p.sign_index + 6) % 12
        for helper in {SIGN_LORDS[p.sign_index], SIGN_LORDS[exalt_sign]}:
            hp = P[helper]
            if hp.house in KENDRA or from_moon(hp.house) in KENDRA:
                add("Neecha Bhanga", f"{pl} debilitated in {p.sign}, but {helper} "
                    f"(lord of {SIGNS[p.sign_index] if helper == SIGN_LORDS[p.sign_index] else SIGNS[exalt_sign]}) "
                    f"is in a kendra from the lagna or Moon", [pl, helper])
                break

    # Kemadruma: no graha (other than Sun and the nodes) in the 2nd or 12th from the Moon.
    neighbours = [q for q in SEVEN if q not in ("Sun", "Moon") and from_moon(P[q].house) in (2, 12)]
    if not neighbours:
        add("Kemadruma yoga", "No planet in the 2nd or 12th from the Moon (check cancellations)", ["Moon"])
    return found


def parashari_factors(chart: Chart) -> set[str]:
    tags = set()
    P = _p(chart)
    for a in aspects(chart):
        n = a["planet"].lower()
        tags.add(f"{n} aspects house {a['house']}")
        if a["house"] == 1:
            tags.add(f"{n} aspects lagna")
        for t in a["planets"]:
            tags.add(f"{n} aspects {t.lower()}")
    names = [p.name for p in chart.planets]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if P[a].sign == P[b].sign:
                tags |= {f"{a.lower()} conjunct {b.lower()}", f"{b.lower()} conjunct {a.lower()}",
                         f"{a.lower()} with {b.lower()}", f"{b.lower()} with {a.lower()}"}
    for pl, nature in functional_nature(chart).items():
        tags.add(f"{pl.lower()} {nature.split(' (')[0]}")
    for y in yogas(chart):
        tags.add(y["name"].lower())
        tags.add(y["name"].lower().split(" (")[0])
    return tags


def parashari_summary(chart: Chart) -> str:
    lines = ["Graha drishti (houses aspected):"]
    by = {}
    for a in aspects(chart):
        by.setdefault(a["planet"], []).append(
            f"{a['house']}" + (f" ({', '.join(a['planets'])})" if a["planets"] else ""))
    lines += [f"- {k} aspects {', '.join(v)}" for k, v in by.items()]
    lines.append(f"Functional nature for {chart.lagna.sign} lagna: " + "; ".join(
        f"{k} {v}" for k, v in functional_nature(chart).items()))
    ys = yogas(chart)
    lines.append("Yogas detected (verify strength and cancellations):" if ys else "Yogas detected: none of the core yogas checked.")
    lines += [f"- {y['name']}: {y['description']}" for y in ys]
    return "\n".join(lines)
