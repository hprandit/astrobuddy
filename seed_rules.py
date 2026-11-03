"""A few starter rules so analysis has something to work with. Replace with your own."""
from jyotish.knowledge import KnowledgeBase

STARTER = [
    ("Saturn in house 7", "Marriage tends to come later; partner mature, responsible or older; relationships carry duty.", "marriage", "classical (Parashari)"),
    ("Jupiter in house 1", "Wisdom, optimism and protection; respected, ethical nature; good for health and guidance.", "personality", "classical (Parashari)"),
    ("Moon debilitated", "Emotional sensitivity and fluctuating mind; needs steady routines; check Neecha Bhanga.", "mind", "classical (Parashari)"),
    ("Mars own sign", "Strong drive, courage and initiative; energy well channelled into the houses Mars rules.", "strength", "classical (Parashari)"),
    ("lord of house 10 in house 9", "Dharma-Karmadhipati link: career aligned with purpose, fortune through work, mentors help career.", "career", "classical (Parashari)"),
    ("Rahu mahadasha", "18-year period of ambition, worldly expansion, foreign links and unconventional paths; judge by Rahu's house and dispositor.", "timing", "classical (Parashari)"),
]

if __name__ == "__main__":
    kb = KnowledgeBase()
    for c, i, t, s in STARTER:
        kb.add_rule(c, i, t, s)
    print(f"Added {len(STARTER)} starter rules.")
