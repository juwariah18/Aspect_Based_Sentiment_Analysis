import re
import sys
from collections import Counter
from functools import lru_cache

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


MODEL_NAME = "nlptown/bert-base-multilingual-uncased-sentiment"
SAMPLE_REVIEW = (
    "The delivery was quick, the product was packed properly and everything was "
    "exactly as shown in the picture. The toy was working when I opened it, but "
    "it stopped working the next day. Waste of money. I received the product "
    "two days late and the box was damaged. Luckily the item was working."
)
EMOJIS = {
    "positive": "😊",
    "negative": "😞",
    "neutral": "😐",
    "mixed": "😐",
}


@lru_cache(maxsize=1)
def load_sentiment_model():
    """Load the pretrained product-review sentiment model once."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def split_into_clauses(review):
    """Split a review into short sentence and contrast clauses."""
    sentences = re.split(r"(?<=[.!?\n])\s+", review.strip())
    clauses = []
    for sentence in sentences:
        parts = re.split(
            r",\s*|;\s*|(?=\b(?:but|however|although|yet)\b)",
            sentence,
            flags=re.IGNORECASE,
        )
        clauses.extend(part.strip() for part in parts if part.strip())
    return clauses


def analyze_clause(clause, tokenizer, model):
    """Classify a clause and return its sentiment and confidence."""
    model_text = clause
    if re.match(r"^luckily\b", clause, flags=re.IGNORECASE):
        remainder = re.sub(r"^luckily\b", "", clause, flags=re.IGNORECASE).strip()
        model_text = f"I was lucky that {remainder}"

    inputs = tokenizer(
        model_text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
    )
    with torch.inference_mode():
        logits = model(**inputs).logits[0]
        star_probabilities = torch.softmax(logits, dim=-1)

    # The model predicts probabilities for ratings from one to five stars.
    sentiment_probabilities = {
        "negative": star_probabilities[0] + star_probabilities[1],
        "neutral": star_probabilities[2],
        "positive": star_probabilities[3] + star_probabilities[4],
    }
    strongest_sentiment = max(
        sentiment_probabilities, key=sentiment_probabilities.get
    )
    confidence = round(
        sentiment_probabilities[strongest_sentiment].item() * 100
    )
    # Treat a weak model preference as neutral instead of forcing a polarity.
    sentiment = (
        "neutral"
        if confidence < 55
        else strongest_sentiment
    )
    return sentiment, confidence


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    tokenizer, model = load_sentiment_model()
    review = input(
        "Enter a review (or press Enter to use the sample): "
    ).strip() or SAMPLE_REVIEW

    clauses = split_into_clauses(review)
    results = [
        analyze_clause(clause, tokenizer, model)
        for clause in clauses
    ]
    counts = Counter(sentiment for sentiment, _ in results)
    highest_count = max(counts.values(), default=0)
    leaders = [
        sentiment
        for sentiment in ("positive", "negative", "neutral")
        if counts[sentiment] == highest_count
    ]
    overall = leaders[0] if len(leaders) == 1 else "mixed"

    print("\nSentiment Analysis")
    print(f"Overall: {EMOJIS[overall]} {overall.title()}")
    print(f"😊 Positive: {counts['positive']}")
    print(f"😞 Negative: {counts['negative']}")
    print(f"😐 Neutral: {counts['neutral']}")
    print("\n🧩 Sentence Analysis")

    for number, (clause, (sentiment, confidence)) in enumerate(
        zip(clauses, results), start=1
    ):
        print(f"\nSentence {number}")
        print(clause)
        print(f"{EMOJIS[sentiment]} {sentiment.upper()} ({confidence}%)")


if __name__ == "__main__":
    main()
