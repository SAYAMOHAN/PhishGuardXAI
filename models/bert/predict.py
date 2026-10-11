
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_DIR = Path(__file__).resolve().parent / "saved_model"

tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
model.eval()


def predict_bert(url: str) -> float:
    """Return the model's probability that a URL is phishing (class 1)."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")

    inputs = tokenizer(
        url.strip(),
        return_tensors="pt",
        truncation=True,
        max_length=96,
    )

    with torch.inference_mode():
        logits = model(**inputs).logits
        probability = torch.softmax(logits, dim=1)[0, 1].item()

    return float(probability)


if __name__ == "__main__":
    examples = [
        "https://www.wikipedia.org/",
        "http://paypal.com.security-check.example/login",
    ]

    for url in examples:
        probability = predict_bert(url)
        print(f"URL: {url}")
        print(f"Phishing probability: {probability:.4f}")
        print(f"Predicted class: {'phishing' if probability >= 0.5 else 'legitimate'}")
        print()
