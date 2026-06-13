#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
03_train_model.py - Behavioural Finance Classifier Trainer
Loads labelled headlines, trains a TF-IDF + Logistic Regression pipeline,
prints a detailed classification report, and saves the confusion matrix and 
predictive keyword plots.
"""

import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

def train_model():
    print("=" * 60)
    print("      TRAINING BEHAVIOURAL FINANCE CLASSIFIER")
    print("=" * 60)
    
    labelled_path = "data/labelled_headlines.csv"
    if not os.path.exists(labelled_path):
        print(f"ERROR: '{labelled_path}' not found! Run 01_scrape.py and augment_data.py first.")
        return
        
    df = pd.read_csv(labelled_path, encoding="utf-8")
    
    # Drop rows where label is empty or NaN
    df = df.dropna(subset=["label"])
    df = df[df["label"].str.strip() != ""]
    
    # Print class distribution before training
    print("\n--- Label Distribution Before Training ---")
    dist = df["label"].value_counts()
    for label, count in dist.items():
        print(f"  {label:<25}: {count} headlines ({count/len(df)*100:.1f}%)")
    print("-" * 42)
    print(f"  Total samples: {len(df)}")
    print("=" * 60)
    
    # Split features and labels
    X = df["headline"]
    y = df["label"]
    
    # Split 80% train, 20% test with stratification to preserve class balance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    print(f"Train set size: {len(X_train)} headlines")
    print(f"Test set size : {len(X_test)} headlines\n")
    
    # Build single pipeline: TF-IDF Vectorizer + Logistic Regression Classifier
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2), 
            max_features=5000, 
            stop_words='english',
            sublinear_tf=True
        )),
        ('classifier', LogisticRegression(
            C=10.0,
            max_iter=1000, 
            random_state=42
        ))
    ])
    
    # Train pipeline
    print("Training Logistic Regression pipeline...")
    pipeline.fit(X_train, y_train)
    print("Training complete.\n")
    
    # Predict on test set
    y_pred = pipeline.predict(X_test)
    
    # Evaluate model
    accuracy = accuracy_score(y_test, y_pred)
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    report_text = classification_report(y_test, y_pred)
    
    print("=" * 60)
    print(f"Overall Accuracy: {accuracy * 100:.2f}%")
    print("=" * 60)
    print("Classification Report:")
    print(report_text)
    print("=" * 60)

    # Save metrics JSON
    import json
    metrics_data = {
        "accuracy": accuracy,
        "classification_report_text": report_text,
        "class_metrics": report_dict,
        "dataset_size": len(df)
    }
    os.makedirs("data", exist_ok=True)
    with open("data/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=4)
    print("Saved metrics to 'data/metrics.json'.")
    
    # -------------------------------------------------------------
    # Image 1 — Confusion Matrix (confusion_matrix.png)
    # -------------------------------------------------------------
    print("Generating and saving Confusion Matrix plot...")
    plt.figure(figsize=(8, 6), dpi=150)
    
    unique_labels = sorted(list(set(y)))
    cm = confusion_matrix(y_test, y_pred, labels=unique_labels)
    
    sns.heatmap(
        cm, 
        annot=True, 
        fmt="d", 
        cmap="Blues", 
        xticklabels=unique_labels, 
        yticklabels=unique_labels,
        cbar=True,
        square=True
    )
    
    plt.title("Confusion Matrix — Behavioural Finance Headline Classifier", fontsize=12, fontweight='bold', pad=15)
    plt.xlabel("Predicted Label", fontsize=10, labelpad=10)
    plt.ylabel("Actual Label", fontsize=10, labelpad=10)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig("confusion_matrix.png", dpi=150)
    plt.close()
    print("Confusion Matrix saved to 'confusion_matrix.png'.")
    
    # -------------------------------------------------------------
    # Image 2 — Top Keywords Per Class (top_keywords.png)
    # -------------------------------------------------------------
    print("Generating and saving Top Keywords Per Class plot...")
    vectorizer = pipeline.named_steps['tfidf']
    classifier = pipeline.named_steps['classifier']
    
    feature_names = vectorizer.get_feature_names_out()
    coefs = classifier.coef_
    classes = classifier.classes_
    
    # Set up matplotlib grid (2 rows, 3 columns)
    fig, axes = plt.subplots(2, 3, figsize=(18, 10), dpi=150)
    axes = axes.flatten()
    
    # Harmonious colors for the 6 subplots
    subplot_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
    
    for idx, class_label in enumerate(classes):
        class_coefs = coefs[idx]
        
        # Get the indices of the top 10 coefficients for this class
        top_10_indices = class_coefs.argsort()[-10:]
        
        top_features = [feature_names[i] for i in top_10_indices]
        top_weights = [class_coefs[i] for i in top_10_indices]
        
        # Plot horizontal bar chart
        ax = axes[idx]
        ax.barh(top_features, top_weights, color=subplot_colors[idx % len(subplot_colors)], edgecolor='black', alpha=0.85)
        
        ax.set_title(f"Class: {class_label}", fontsize=12, fontweight='bold')
        ax.set_xlabel("Predictive Weight (Coefficient)", fontsize=9)
        ax.tick_params(axis='both', which='major', labelsize=9)
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        
    plt.suptitle("Top Predictive Keywords per Behavioural Class", fontsize=18, fontweight='bold', y=0.98)
    plt.tight_layout()
    # Adjust spacing to fit suptitle
    plt.subplots_adjust(top=0.90)
    plt.savefig("top_keywords.png", dpi=150)
    plt.close()
    print("Top Keywords plot saved to 'top_keywords.png'.")
    
    # Save the pipeline
    with open("model.pkl", "wb") as f:
        pickle.dump(pipeline, f)
    print("Trained model pipeline successfully serialized and saved to 'model.pkl'.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    train_model()
