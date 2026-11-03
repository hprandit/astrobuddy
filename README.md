# Jyotish Learning Assistant (Parashari)

A small platform that learns Vedic astrology with you and learns to give chart analysis.

1. **Chart engine**: sidereal zodiac, Lahiri ayanamsa (Swiss Ephemeris), whole-sign houses,
   nakshatra and pada, D9 Navamsa, dignity, house lordship, Vimshottari mahadasha/antardasha.
2. **Knowledge base you teach**: IF/THEN rules with topic and source (SQLite, `data/jyotish.db`).
3. **Analysis**: Claude reads the chart, the rules that match it, and your past corrections.
   It cites rules as `[R12]`, marks anything not taught as *(general knowledge)*, and ends
   with questions for you, so each session gives you something new to teach.
4. **Corrections**: every correction is saved and fed into future analyses; you can also turn
   it straight into a rule. `/api/export` gives all taught material as JSON, which becomes the
   dataset for fine-tuning a custom model later.

## Run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # without it, Analyze shows the prompt instead
python seed_rules.py                     # optional starter rules
uvicorn app:app --reload                 # open http://localhost:8000
```

`JYOTISH_MODEL` picks the Claude model (default `claude-opus-5-5`).

## Birth place

Type a city and pick it from the list: latitude, longitude and timezone fill in, and the UTC offset
is worked out for the birth date itself (including historical changes such as India's +6:30 war
time in 1942-45). Lookup is offline (GeoNames, towns of 5,000+ people). For a smaller village,
type the coordinates and UTC offset by hand.

## Parashari layer

`jyotish/parashari.py` adds what a Parashari reading starts from:

- **Graha drishti**: every graha aspects the 7th; Mars also the 4th and 8th, Jupiter the 5th and
  9th, Saturn the 3rd and 10th. Rahu and Ketu get the 7th only; if your teacher gives them the
  5th and 9th too, set `NODE_ASPECTS = [5, 7, 9]`.
- **Functional nature by lagna**: yogakaraka, functional benefic/malefic, kendradhipati dosha.
  Sun and Moon are not blemished by 8th lordship.
- **Dignity** now includes moolatrikona.
- **Yogas**: Pancha Mahapurusha, Gajakesari, Budhaditya, Chandra-Mangala, Parivartana,
  Raja yoga (kendra and trikona lords conjunct, in mutual aspect or exchanging), Yogakaraka,
  Dhana, Vipareeta Raja (Harsha/Sarala/Vimala), Neecha Bhanga (simplified) and Kemadruma.
  These are detected mechanically and Claude is told to judge their strength.

`python seed_rules.py` loads about 55 starter rules, paraphrased general Parashari principles.
They are a scaffold to correct, not scripture: edit or delete any that differ from your books.

## Writing rules that match well

Conditions are matched against the chart's factor phrases (shown on the Chart tab), e.g.
`Saturn in house 7`, `Venus in Pisces`, `Moon in Rohini`, `Jupiter exalted`,
`Mars retrograde`, `lord of house 10 in house 9`, `Rahu mahadasha`, `libra lagna`,
`Jupiter aspects moon`, `Saturn aspects house 7`, `Moon conjunct Mars`, `Saturn yogakaraka`,
`Saturn functional malefic`, `Gajakesari yoga`, `Raja yoga`, `Venus moolatrikona`.
"7th house" is understood as "house 7".

## Not yet included

Other divisional charts beyond D9, Shadbala and Ashtakavarga, full yoga cancellation rules, transits, multi-user accounts, hosting.
