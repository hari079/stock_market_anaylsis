import json
import pandas as pd

# Load metrics
with open("data/metrics.json", "r") as f:
    data = json.load(f)

print("=" * 60)
print(f"Overall Accuracy: {round(data['accuracy']*100, 2)}%")
print(f"Dataset Size: {data['dataset_size']} headlines")
print("=" * 60)
print("\nPer-Class Metrics:")
skip = {"accuracy", "macro avg", "weighted avg"}
for k, v in data["class_metrics"].items():
    if k not in skip:
        print(f"  {k:<25}: Precision={round(v['precision']*100,1)}%  Recall={round(v['recall']*100,1)}%  F1={round(v['f1-score']*100,1)}%  Support={int(v['support'])}")

print("\nMacro Avg:")
ma = data["class_metrics"]["macro avg"]
print(f"  Precision={round(ma['precision']*100,1)}%  Recall={round(ma['recall']*100,1)}%  F1={round(ma['f1-score']*100,1)}%")

# Dataset distribution
df = pd.read_csv("data/labelled_headlines.csv")
print("\n" + "=" * 60)
print("Label Distribution:")
dist = df["label"].value_counts()
for label, count in dist.items():
    print(f"  {label:<25}: {count} ({round(count/len(df)*100,1)}%)")
print(f"  Total: {len(df)}")
