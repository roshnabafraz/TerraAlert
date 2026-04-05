import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report


def main():
    base_dir = Path(__file__).resolve().parent
    dataset_path = base_dir / "datasets" / "labeled" / "training_data.csv"
    model_path = base_dir / "models" / "disaster_classifier.pkl"
    metrics_path = base_dir / "models" / "metrics.json"

    if not dataset_path.exists():
        raise FileNotFoundError(f"Training data not found: {dataset_path}")

    data = pd.read_csv(dataset_path)
    if "text" not in data.columns or "label" not in data.columns:
        raise ValueError("Training data must include 'text' and 'label' columns")

    X_train, X_test, y_train, y_test = train_test_split(
        data["text"], data["label"], test_size=0.2, random_state=42, stratify=data["label"]
    )

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    report = classification_report(y_test, predictions, output_dict=True)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)

    with open(metrics_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print(f"Model saved to {model_path}")
    print(f"Metrics saved to {metrics_path}")


if __name__ == "__main__":
    main()
