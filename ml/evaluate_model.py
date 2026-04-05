from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import classification_report


def main():
    base_dir = Path(__file__).resolve().parent
    dataset_path = base_dir / "datasets" / "labeled" / "training_data.csv"
    model_path = base_dir / "models" / "disaster_classifier.pkl"

    if not dataset_path.exists() or not model_path.exists():
        raise FileNotFoundError("Model or dataset missing. Run train_model.py first.")

    data = pd.read_csv(dataset_path)
    model = joblib.load(model_path)

    predictions = model.predict(data["text"])
    report = classification_report(data["label"], predictions)

    print(report)


if __name__ == "__main__":
    main()
