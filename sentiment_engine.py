"""Rule-based sentiment analysis engine ported from AspectSentinel's script.js."""
import re

POSITIVE_WORDS = {
    "amazing": 2.5, "awesome": 2.5, "best": 2.5, "beautiful": 1.7,
    "excellent": 2.7, "fantastic": 2.7, "good": 1.5, "great": 2,
    "happy": 1.8, "love": 2.5, "loved": 2.5, "perfect": 2.7,
    "pleased": 1.8, "recommend": 1.8, "satisfied": 1.8, "nice": 1.4,
    "pretty": 1.5, "comfortable": 1.5, "smooth": 1.3, "soft": 1.2,
    "quick": 1.2, "easy": 0.8, "reliable": 1.7, "sturdy": 1.5,
    "useful": 1.2, "works": 0.35, "working": 0.35, "luckily": 0.65,
    "perfectly": 1.5,
}

NEGATIVE_WORDS = {
    "awful": -2.7, "bad": -1.8, "broken": -2.7, "damaged": -2.4,
    "disappointing": -2.2, "disappointed": -2.2, "defective": -2.7,
    "hate": -2.5, "horrible": -2.7, "late": -1.4, "missing": -2,
    "poor": -2, "problem": -1.5, "problems": -1.5, "return": -1.1,
    "returned": -1.1, "stopped": -2.1, "terrible": -2.7, "tight": -1.6,
    "uncomfortable": -1.8, "useless": -2.5, "waste": -2.5, "worst": -2.7,
    "wrong": -1.8, "slow": -1.5, "ugly": -1.6, "difficult": -1.2,
    "expensive": -0.8, "weird": -1.5, "leak": -2.5, "leaks": -2.5,
    "leaking": -2.5, "leaked": -2.5, "leakage": -2.5, "draining": -1.8,
    "overheats": -2, "overheating": -2, "crashed": -2.2, "crashing": -2.2,
    "freezing": -1.8, "disconnecting": -1.8, "thin": -0.4, "faded": -1.7,
}

NEGATIONS = {"not", "no", "never", "without", "hardly"}
INTENSIFIERS = {"very", "really", "extremely", "absolutely", "so"}
CONTRAST_WORDS = {"but", "however", "although", "though", "yet"}
SPECIAL_PHRASES = [
    (r"\b(?:exceeded|exceeds|exceeding) (?:my |our )?expectations?\b|\bbetter than (?:i |we )?expected\b|\bmore than (?:i |we )?expected\b|\babove (?:my |our )?expectations?\b|\btoo good than expected\b", 2.5),
    (r"\bnot as expected\b|\bbelow (?:my |our )?expectations?\b|\bshort of (?:my |our )?expectations?\b", -2),
    (r"\btoo (?:thin|small|big|short|long|tight|loose|heavy|light|slow|noisy|loud|hard|soft)\b", -2),
    (r"\bnot like (?:the )?(?:one )?(?:shown|pictured|advertised|online|on the website)\b|\bnot (?:as|what) shown\b|\bnot the same as (?:the )?(?:picture|pictures|website|advertised)\b", -2.5),
    (r"\b(?:actual )?colou?r (?:is )?lighter than (?:the )?(?:picture|pictures|shown|expected)\b", -2.4),
    (r"\b(?:looks|is|was) (?:really |very |so )?(?:pretty|beautiful|gorgeous|lovely)\b", 2),
    (r"\b(?:fits?|fit) perfectly\b|\bmatches? (?:the )?(?:photos|pictures|description)\b|\bexactly as (?:shown|described|expected)\b", 1.8),
    (r"\b(?:does not|doesn't|did not|didn't|is not|isn't|was not|wasn't) work(?:ing)?\b|\bnot working\b|\bstopped working\b", -2.8),
    (r"\bworking slow(?:ly)?\b|\bslow(?:ly)? (?:computer|laptop|phone|device|performance)\b", -2.5),
    (r"\bbattery (?:is )?(?:draining|drains|dies) (?:too )?(?:fast|quickly)\b|\b(?:fast|quick) battery drain(?:ing)?\b", -3),
    (r"\b(?:lipstick|makeup|product|item|container|bottle)s? (?:is |are |was |were )?(?:leaking|leaked)\b|\b(?:leaking|leaked|leakage) (?:from|through) (?:the )?(?:packaging|package|box|container)\b", -3),
    (r"\b(?:on time|as described|as shown|as expected|met (?:my |our )?expectations?)\b", 0),
]


def normalize(text: str) -> str:
    """Lowercase text and expand common English contractions."""
    text = text.lower()
    for contraction, replacement in [("n't", " not"), ("'re", " are"), ("'m", " am"),
                                     ("'ve", " have"), ("'ll", " will"), ("'d", " would"),
                                     ("'s", " is")]:
        text = text.replace(contraction, replacement)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text)).strip()


def split_into_sentences(text: str) -> list[str]:
    """Split a review into sentence/clause-sized pieces for separate scoring."""
    pieces = re.findall(r"[^.!?\n]+[.!?]?", text)
    clauses = []
    for piece in pieces:
        clauses.extend(re.split(r",\s*|(?=\b(?:but|also|however|although|though|yet)\b)", piece, flags=re.I))
    result = []
    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue
        if re.fullmatch(r"(?:but|also|however|although|though|yet)[.!?]*", clause, flags=re.I) and result:
            result[-1] += " " + clause
        else:
            result.append(clause)
    return result


def score_sentence(sentence: str) -> dict:
    """Score a sentence using word lists, phrases, negation and emphasis rules."""
    clean = normalize(sentence)
    score = 0.0
    for pattern, value in SPECIAL_PHRASES:
        if re.search(pattern, clean, flags=re.I):
            score += value

    words = clean.split()
    for index, word in enumerate(words):
        value = POSITIVE_WORDS.get(word, NEGATIVE_WORDS.get(word, 0))
        if not value:
            continue
        if index > 0 and words[index - 1] in INTENSIFIERS:
            value *= 1.4
        if any(token in NEGATIONS for token in words[max(0, index - 3):index]):
            value = abs(value) * 0.5 if value < 0 else -value
        has_contrast_before = any(token in CONTRAST_WORDS for token in words[:index])
        score += value * (1.35 if has_contrast_before else 0.7)

    sentiment = "positive" if score >= 0.7 else "negative" if score <= -0.7 else "neutral"
    return {"sentiment": sentiment, "score": round(score, 2)}


def analyze_review(text: str) -> dict:
    """Return clause predictions, sentiment counts and overall sentiment."""
    sentences = split_into_sentences(text)
    predictions = [score_sentence(sentence) for sentence in sentences]
    counts = {label: sum(p["sentiment"] == label for p in predictions)
              for label in ("positive", "negative", "neutral")}
    if not predictions:
        overall = "neutral"
    else:
        high = max(counts.values())
        leaders = [label for label, count in counts.items() if count == high]
        overall = leaders[0] if len(leaders) == 1 else "mixed"
    return {"sentences": sentences, "predictions": predictions, "counts": counts, "overall": overall}
