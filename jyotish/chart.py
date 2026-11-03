"""Sidereal (Lahiri) birth chart computation using the Swiss Ephemeris."""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta

import swisseph as swe

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus",
              "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
              "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
              "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
              "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
              "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
              "Revati"]
DASHA_ORDER = [("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
               ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)]
DASHA_YEARS = dict(DASHA_ORDER)
YEAR_DAYS = 365.25

PLANETS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
           "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
           "Rahu": swe.MEAN_NODE}

# Sign index (0 = Aries) of exaltation, debilitation and own signs.
EXALT = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11,
         "Saturn": 6, "Rahu": 1, "Ketu": 7}
OWN = {"Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5], "Jupiter": [8, 11],
       "Venus": [1, 6], "Saturn": [9, 10], "Rahu": [], "Ketu": []}


def dignity(planet: str, sign: int) -> str:
    if EXALT.get(planet) == sign:
        return "exalted"
    if (EXALT.get(planet, -99) + 6) % 12 == sign:
        return "debilitated"
    if sign in OWN.get(planet, []):
        return "own sign"
    return ""


@dataclass
class Placement:
    name: str
    longitude: float          # sidereal, 0-360
    sign: str
    sign_index: int
    degree_in_sign: float
    house: int                # whole-sign house from Lagna
    nakshatra: str
    pada: int
    nakshatra_lord: str
    retrograde: bool = False
    dignity: str = ""
    navamsa_sign: str = ""
    lord_of_houses: list[int] = field(default_factory=list)


@dataclass
class Chart:
    name: str
    birth_local: str
    utc_offset: float
    latitude: float
    longitude: float
    ayanamsa: float
    lagna: Placement
    planets: list[Placement]
    dashas: list[dict]

    def to_dict(self) -> dict:
        return asdict(self)


def _nakshatra(lon: float) -> tuple[str, int, str]:
    span = 360 / 27
    idx = int(lon // span)
    pada = int((lon % span) // (span / 4)) + 1
    return NAKSHATRAS[idx], pada, DASHA_ORDER[idx % 9][0]


def _navamsa_sign(lon: float) -> int:
    return int(lon // (30 / 9)) % 12


def _placement(name: str, lon: float, lagna_sign: int, retro=False) -> Placement:
    sign = int(lon // 30)
    nak, pada, nak_lord = _nakshatra(lon)
    return Placement(
        name=name, longitude=round(lon, 4), sign=SIGNS[sign], sign_index=sign,
        degree_in_sign=round(lon % 30, 2), house=(sign - lagna_sign) % 12 + 1,
        nakshatra=nak, pada=pada, nakshatra_lord=nak_lord, retrograde=retro,
        dignity=dignity(name, sign), navamsa_sign=SIGNS[_navamsa_sign(lon)],
        lord_of_houses=sorted(((s - lagna_sign) % 12 + 1) for s in range(12)
                              if SIGN_LORDS[s] == name),
    )


def vimshottari(moon_lon: float, birth_utc: datetime, years_ahead: int = 120) -> list[dict]:
    span = 360 / 27
    idx = int(moon_lon // span)
    start_i = idx % 9
    lord, years = DASHA_ORDER[start_i]
    elapsed_frac = (moon_lon % span) / span
    # Dasha start is before birth by the elapsed portion.
    start = birth_utc - timedelta(days=elapsed_frac * years * YEAR_DAYS)
    out, t = [], start
    for k in range(9):
        md_lord, md_years = DASHA_ORDER[(start_i + k) % 9]
        md_end = t + timedelta(days=md_years * YEAR_DAYS)
        antars, at = [], t
        for j in range(9):
            ad_lord, ad_years = DASHA_ORDER[(start_i + k + j) % 9]
            ad_len = md_years * ad_years / 120
            ad_end = at + timedelta(days=ad_len * YEAR_DAYS)
            antars.append({"lord": ad_lord, "start": at.date().isoformat(),
                           "end": ad_end.date().isoformat()})
            at = ad_end
        out.append({"lord": md_lord, "start": t.date().isoformat(),
                    "end": md_end.date().isoformat(), "antardashas": antars})
        t = md_end
    return out


def compute_chart(name: str, date: str, time: str, utc_offset: float,
                  latitude: float, longitude: float) -> Chart:
    """date 'YYYY-MM-DD', time 'HH:MM' local, utc_offset in hours (IST = 5.5)."""
    local = datetime.fromisoformat(f"{date}T{time}")
    utc = local - timedelta(hours=utc_offset)
    jd = swe.julday(utc.year, utc.month, utc.day,
                    utc.hour + utc.minute / 60 + utc.second / 3600)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    ayan = swe.get_ayanamsa_ut(jd)

    _, ascmc = swe.houses_ex(jd, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    asc = ascmc[0]
    lagna_sign = int(asc // 30)
    lagna = _placement("Lagna", asc, lagna_sign)
    lagna.dignity = ""

    planets = []
    for pname, pid in PLANETS.items():
        pos, _ = swe.calc_ut(jd, pid, flags)
        lon, speed = pos[0] % 360, pos[3]
        planets.append(_placement(pname, lon, lagna_sign, retro=speed < 0 or pname == "Rahu"))
        if pname == "Rahu":
            planets.append(_placement("Ketu", (lon + 180) % 360, lagna_sign, retro=True))

    moon = next(p for p in planets if p.name == "Moon")
    return Chart(name=name, birth_local=local.isoformat(), utc_offset=utc_offset,
                 latitude=latitude, longitude=longitude, ayanamsa=round(ayan, 4),
                 lagna=lagna, planets=planets, dashas=vimshottari(moon.longitude, utc))


def current_dasha(chart: Chart, on: str | None = None) -> tuple[str, str]:
    on = on or datetime.utcnow().date().isoformat()
    for md in chart.dashas:
        if md["start"] <= on < md["end"]:
            for ad in md["antardashas"]:
                if ad["start"] <= on < ad["end"]:
                    return md["lord"], ad["lord"]
            return md["lord"], ""
    return "", ""


def chart_factors(chart: Chart) -> list[str]:
    """Searchable tags describing the chart, used to find relevant taught rules."""
    tags = {f"lagna:{chart.lagna.sign.lower()}", f"{chart.lagna.sign.lower()} lagna"}
    for p in chart.planets:
        n = p.name.lower()
        tags |= {f"{n} in house {p.house}", f"{n} in {p.sign.lower()}",
                 f"{n} in {p.nakshatra.lower()}"}
        if p.dignity:
            tags.add(f"{n} {p.dignity}")
        if p.retrograde and p.name not in ("Rahu", "Ketu"):
            tags.add(f"{n} retrograde")
        for h in p.lord_of_houses:
            tags.add(f"lord of house {h} in house {p.house}")
    md, ad = current_dasha(chart)
    if md:
        tags |= {f"{md.lower()} mahadasha", f"{md.lower()}-{ad.lower()} dasha"}
    return sorted(tags)


def chart_summary(chart: Chart) -> str:
    lines = [f"Native: {chart.name}, born {chart.birth_local} (UTC{chart.utc_offset:+g}), "
             f"lat {chart.latitude}, lon {chart.longitude}. Lahiri ayanamsa {chart.ayanamsa}.",
             f"Lagna: {chart.lagna.sign} {chart.lagna.degree_in_sign}° "
             f"({chart.lagna.nakshatra} pada {chart.lagna.pada}), Navamsa lagna {chart.lagna.navamsa_sign}.",
             "Planets (whole-sign houses):"]
    for p in chart.planets:
        extra = ", ".join(x for x in [p.dignity, "retrograde" if p.retrograde and p.name not in ("Rahu", "Ketu") else ""] if x)
        lord = f"; lord of {', '.join(map(str, p.lord_of_houses))}" if p.lord_of_houses else ""
        lines.append(f"- {p.name}: {p.sign} {p.degree_in_sign}°, house {p.house}, "
                     f"{p.nakshatra} pada {p.pada} (star lord {p.nakshatra_lord}), "
                     f"D9 {p.navamsa_sign}{lord}{'; ' + extra if extra else ''}")
    md, ad = current_dasha(chart)
    lines.append(f"Current Vimshottari dasha: {md} mahadasha / {ad} antardasha.")
    lines.append("Mahadasha sequence: " + "; ".join(
        f"{d['lord']} {d['start'][:4]}-{d['end'][:4]}" for d in chart.dashas))
    return "\n".join(lines)
