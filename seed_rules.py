"""Starter Parashari rules so analysis has something to work with.

These are paraphrased general principles from the Parashari tradition (BPHS and standard
teaching), written as a starting point. Edit, delete or override them with what your
teacher and books say: your own rules and corrections always take priority.

Run: python seed_rules.py   (safe to run twice; it skips rules already present)
"""
from jyotish.knowledge import KnowledgeBase

SRC = "Parashari principle (paraphrased, verify against BPHS)"

STARTER = [
    # --- fundamentals: houses and lords ---------------------------------------
    ("lord of house 1 in house 1", "Strong sense of self, good vitality, self-made; the native shapes their own life.", "personality"),
    ("lord of house 1 in house 10", "Self-driven career, recognition through one's own effort; status matters to the native.", "career"),
    ("lord of house 1 in house 6", "Native fights obstacles and competition directly; can do well in service, health or legal work, but must guard health.", "health"),
    ("lord of house 1 in house 8", "Life marked by transformations and sudden changes; interest in research or the hidden; watch longevity factors and health.", "health"),
    ("lord of house 1 in house 12", "Expenditure, foreign residence or a spiritual inclination; the native may feel unseen at home.", "foreign"),
    ("lord of house 9 in house 10", "Dharma-Karmadhipati: fortune supports career; meaningful work and good mentors.", "career"),
    ("lord of house 10 in house 9", "Dharma-Karmadhipati: career aligned with purpose, fortune through work, mentors help career.", "career"),
    ("lord of house 5 in house 9", "Trikona lords linked: merit from past lives, good fortune through children, education and wisdom.", "fortune"),
    ("lord of house 7 in house 1", "Partner plays a central role in life; native is relationship-oriented, may marry someone known or nearby.", "marriage"),
    ("lord of house 7 in house 7", "Strong house of marriage and partnership; spouse of good character; business partnerships favoured.", "marriage"),
    ("lord of house 2 in house 11", "Dhana combination: income and savings link up; wealth through gains and networks.", "wealth"),
    ("lord of house 11 in house 2", "Gains turn into accumulated wealth; family resources grow.", "wealth"),
    ("lord of house 4 in house 4", "Comfort at home, property, vehicles and a supportive mother; emotional stability.", "home"),
    ("lord of house 6 in house 12", "Vipareeta (Vimala type): enemies and debts dissolve; savings habits; can be good if supported.", "yoga"),
    ("lord of house 8 in house 6", "Vipareeta (Sarala type): resilience; obstacles defeat themselves.", "yoga"),
    ("lord of house 12 in house 8", "Vipareeta (Vimala/Sarala link): losses turn to gains through crises; good for research and the occult.", "yoga"),
    # --- placements -------------------------------------------------------------
    ("Jupiter in house 1", "Wisdom, optimism and protection; ethical, respected; Jupiter's aspects on 5, 7 and 9 bless children, marriage and fortune.", "personality"),
    ("Saturn in house 7", "Marriage tends to come later; mature or older partner; relationships carry duty and endurance. Saturn also gains directional strength (dig bala) here.", "marriage"),
    ("Mars in house 7", "Kuja dosha house: passion and friction in partnership; match with a similar Mars placement is traditionally advised.", "marriage"),
    ("Mars in house 8", "Kuja dosha house: sudden events, need to guard against accidents and conflicts with in-laws.", "marriage"),
    ("Saturn in house 10", "Slow, steady rise in career through discipline; authority comes late but lasts.", "career"),
    ("Sun in house 10", "Directional strength (dig bala) for the Sun: authority, government links, visible career.", "career"),
    ("Moon in house 4", "Directional strength for the Moon: emotional contentment, attachment to home and mother.", "home"),
    ("Rahu in house 10", "Ambition and unconventional career rise; fame or notoriety; foreign links in work.", "career"),
    ("Ketu in house 12", "Strong pull towards moksha and spiritual practice; detachment from material loss.", "spirituality"),
    ("Venus in house 12", "Venus is happy in the 12th: comforts, pleasures of bed, a generous lifestyle.", "comfort"),
    # --- dignity and states -----------------------------------------------------
    ("Moon debilitated", "Emotional sensitivity and a fluctuating mind; needs steady routines; check Neecha Bhanga.", "mind"),
    ("Sun debilitated", "Ego and confidence tested, strained relations with authority or father; check Neecha Bhanga.", "self"),
    ("Jupiter exalted", "Strong wisdom, grace and protection; blessings on the houses Jupiter rules and aspects.", "strength"),
    ("Saturn exalted", "Fairness, endurance and organisational skill; long-lasting results in the houses Saturn rules.", "strength"),
    ("Mars own sign", "Strong drive, courage and initiative; energy well channelled into the houses Mars rules.", "strength"),
    ("Jupiter retrograde", "Wisdom turned inward; unconventional beliefs or teachers; results of Jupiter come with review and delay.", "state"),
    # --- aspects ----------------------------------------------------------------
    ("Jupiter aspects lagna", "Protection to body and character; good judgement, ethical conduct.", "personality"),
    ("Jupiter aspects moon", "Calms and supports the mind; a key protective influence, also forms part of Gajakesari-like strength.", "mind"),
    ("Saturn aspects moon", "Heavy or serious mind, tendency to worry; maturity and endurance through emotional discipline.", "mind"),
    ("Saturn aspects house 7", "Delay or seriousness in marriage; long-lasting commitment once made.", "marriage"),
    ("Mars aspects house 7", "Heat and assertiveness in partnerships; can bring arguments if afflicted.", "marriage"),
    # --- yogas ------------------------------------------------------------------
    ("gajakesari yoga", "Respect, intelligence, lasting reputation; strength depends on the dignity and house of Jupiter and Moon.", "yoga"),
    ("raja yoga", "Rise in status and authority, especially in the dashas of the planets forming it.", "yoga"),
    ("dhana yoga", "Wealth-giving combination; activates in the dashas of the lords involved.", "yoga"),
    ("yogakaraka", "The yogakaraka planet gives very good results in its dasha, especially when well placed.", "yoga"),
    ("parivartana yoga", "Exchange binds two houses: their affairs merge. Between good houses it is auspicious; with 6/8/12 it is mixed.", "yoga"),
    ("kemadruma yoga", "Loneliness or poverty of support in the mind; cancelled if planets are in kendras from lagna or Moon.", "yoga"),
    ("neecha bhanga", "Debilitation cancelled: early struggle that turns into strong later rise.", "yoga"),
    ("budhaditya yoga", "Sharp intellect and communication; weaker if Mercury is combust (very close to the Sun).", "yoga"),
    ("hamsa yoga", "Pancha Mahapurusha of Jupiter: virtuous, learned, respected.", "yoga"),
    ("malavya yoga", "Pancha Mahapurusha of Venus: charm, comforts, artistic gifts, prosperous marriage.", "yoga"),
    ("ruchaka yoga", "Pancha Mahapurusha of Mars: courage, leadership, success in competition, police or military.", "yoga"),
    ("bhadra yoga", "Pancha Mahapurusha of Mercury: intellect, eloquence, success in business and learning.", "yoga"),
    ("sasa yoga", "Pancha Mahapurusha of Saturn: authority over many, discipline, power that builds slowly.", "yoga"),
    # --- functional nature and dashas -------------------------------------------
    ("saturn functional malefic", "For this lagna Saturn's dasha brings the hardships of the houses it rules, softened if well placed.", "functional"),
    ("jupiter functional malefic", "Jupiter's natural goodness is reduced for this lagna; its dasha brings results of difficult houses it rules.", "functional"),
    ("rahu mahadasha", "18-year period of ambition, worldly expansion, foreign links and unconventional paths; judge by Rahu's house and dispositor.", "timing"),
    ("saturn mahadasha", "19 years of effort, responsibility and structure; results follow Saturn's lordship and dignity for this lagna.", "timing"),
    ("jupiter mahadasha", "16 years of growth, learning and children/teachers; good if Jupiter is a functional benefic.", "timing"),
]

if __name__ == "__main__":
    kb = KnowledgeBase()
    have = {(r["condition"].lower(), r["interpretation"].lower()) for r in kb.rules()}
    added = 0
    for c, i, t in STARTER:
        if (c.lower(), i.lower()) not in have:
            kb.add_rule(c, i, t, SRC)
            added += 1
    print(f"Added {added} starter Parashari rules ({len(STARTER) - added} already present).")
