#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
04_predict.py - Behavioural Finance NLP Predictor
Loads the trained TF-IDF + Logistic Regression model and provides an interactive
command-line tool for single-headline predictions and semicolon-separated batch predictions.
"""

import os
import sys
import pickle
import pandas as pd

# Mappings for meanings and academic theories
THEORY_MAP = {
    "FOMO": {
        "meaning": "Fear of Missing Out — retail FOMO, rushing to buy assets to avoid missing gains",
        "theory": "Narrative Economics (Shiller, 2019)"
    },
    "HERD": {
        "meaning": "Herd Behaviour — mass crowd-following, sheep-like exits, or copycat buying",
        "theory": "Financial Instability Hypothesis (Minsky, 1986)"
    },
    "PANIC": {
        "meaning": "Panic Selling — irrational fear-driven mass selloff and asset dumping",
        "theory": "Prospect Theory (Kahneman & Tversky, 1979)"
    },
    "LOSS_AVERSION": {
        "meaning": "Loss Aversion — holding losing bags, refusing to sell, waiting for break-even",
        "theory": "Prospect Theory (Kahneman & Tversky, 1979)"
    },
    "COGNITIVE_DISSONANCE": {
        "meaning": "Cognitive Dissonance — market shrugs off shock/bad news, continuing to rally",
        "theory": "Efficient Market Hypothesis Critique (Shiller, 2000)"
    },
    "NEUTRAL": {
        "meaning": "Neutral — factual market reporting, no strong emotional or behavioural signal",
        "theory": "No strong behavioural signal detected"
    }
}

def print_box(headline, label, confidence):
    """
    Prints the beautiful ASCII prediction box requested by the user.
    """
    meaning = THEORY_MAP[label]["meaning"]
    theory = THEORY_MAP[label]["theory"]
    
    print("════════════════════════════════════════════")
    print(f"  Headline   : {headline}")
    print(f"  Label      : {label}")
    print(f"  Confidence : {confidence:.1f}%")
    print(f"  Meaning    : {meaning}")
    print(f"  Theory     : {theory}")
    print("════════════════════════════════════════════")

def main():
    model_path = "model.pkl"
    if not os.path.exists(model_path):
        print(f"ERROR: '{model_path}' not found! Run 03_train_model.py first.")
        sys.exit(1)
        
    print("Loading model pipeline...")
    with open(model_path, "rb") as f:
        model = pickle.load(f)
        
    print("\n" + "=" * 60)
    print("      INTERACTIVE BEHAVIOURAL FINANCE NLP PREDICTOR")
    print("=" * 60)
    print("  Instructions:")
    print("  - Type any headline to predict its behavioural finance label.")
    print("  - Type 'batch' to enter multiple headlines separated by semicolons.")
    print("  - Type 'quit' or 'exit' to end.")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\nEnter headline (or command): ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["quit", "exit"]:
                print("Exiting predictor. Goodbye!")
                break
                
            if user_input.lower() == "batch":
                batch_input = input("Enter multiple headlines separated by semicolons:\n> ").strip()
                if not batch_input:
                    continue
                    
                # Split and clean headlines
                headlines = [h.strip() for h in batch_input.split(";") if h.strip()]
                if not headlines:
                    print("No headlines parsed.")
                    continue
                    
                # Predict
                preds = model.predict(headlines)
                probs = model.predict_proba(headlines)
                
                # Format results table
                results = []
                for h, pred, prob in zip(headlines, preds, probs):
                    max_prob = prob.max() * 100
                    theory = THEORY_MAP[pred]["theory"]
                    results.append({
                        "Headline": h[:60] + "..." if len(h) > 60 else h,
                        "Predicted Label": pred,
                        "Confidence": f"{max_prob:.1f}%",
                        "Theory": theory
                    })
                    
                df_results = pd.DataFrame(results)
                print("\nBatch Predictions:")
                print(df_results.to_string(index=False))
                print("-" * 60)
                
            else:
                # Single headline prediction
                pred = model.predict([user_input])[0]
                prob = model.predict_proba([user_input])[0]
                max_prob = prob.max() * 100
                
                print_box(user_input, pred, max_prob)
                
        except KeyboardInterrupt:
            print("\nExiting predictor. Goodbye!")
            break
        except Exception as e:
            print(f"Error during prediction: {e}")

if __name__ == "__main__":
    main()
