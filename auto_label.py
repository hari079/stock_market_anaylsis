#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
auto_label.py - Real-World Headline Labeller
Labels real-world crawled headlines based on their search query source 
and text heuristics. Performs under-sampling on the majority NEUTRAL class 
to produce a balanced, 100% real-world dataset.
"""

import os
import re
import pandas as pd

# Keywords for classifying general feeds if they fall into behavioral classes
FOMO_KEYWORDS = ["fomo", "pile in", "piling in", "don't miss", "dont miss", "buying frenzy", "mania", "frenzy"]
HERD_KEYWORDS = ["herd", "exodus", "investors flee", "fleeing", "mass exit", "dumping", "follow the crowd", "sheep-like"]
LOSS_KEYWORDS = ["loss aversion", "drawdown", "refuse to sell", "holding onto", "hold tight", "holding bag", "unwilling to sell"]
COG_KEYWORDS = ["cognitive dissonance", "shrugs off", "dismisses bad news", "defies", "despite", "ignores warning", "shrug off"]
PANIC_KEYWORDS = ["panic", "bloodbath", "capitulate", "rout", "plunge", "crash", "sell-off", "selloff", "mass panic"]

# Sentiment/action words that should NEVER be allowed in the NEUTRAL class to avoid label leakage
NEUTRAL_EXCLUDE_KEYWORDS = [
    "surge", "rally", "plunge", "crash", "fear", "panic", "fomo", "herd", 
    "exodus", "flee", "bloodbath", "capitulate", "shrug", "defy", "despite", 
    "refuse", "hold", "fears", "soar", "spike", "drop", "jump", "sell-off", 
    "selloff", "mania", "frenzy", "rout", "bagholder", "dissonance", 
    "aversion", "drawdown", "bubble", "fleeing", "shock", "warning", "crisis",
    "war", "conflict", "strike", "strikes", "attack", "attacks", "threat", 
    "threats", "threatens", "tension", "tensions", "escalate", "escalates", 
    "escalation", "uncertainty", "halt", "halts", "vault", "vaults", 
    "rise", "rises", "rising", "fall", "falls", "falling", "slide", 
    "slides", "sliding", "rebound", "rebounds", "rebounding", "bounce", 
    "bounces", "bouncing", "boost", "boosts", "boosting", "climb", 
    "climbs", "climbing", "gain", "gains", "gaining", "loss", "losses", 
    "losing", "grew", "grow", "growth", "growing", "higher", "lower", 
    "peak", "peaks", "peaking", "bottom", "bottoms", "bottoming", 
    "highs", "lows", "all-time", "all time"
]

def classify_general_headline(headline):
    """
    Classifies a general headline using text heuristics.
    Excludes headlines containing active sentiment/emotional features to keep NEUTRAL purely factual.
    """
    h_lower = headline.lower()
    
    if any(k in h_lower for k in LOSS_KEYWORDS):
        return "LOSS_AVERSION"
    if any(k in h_lower for k in COG_KEYWORDS):
        return "COGNITIVE_DISSONANCE"
    if any(k in h_lower for k in FOMO_KEYWORDS):
        return "FOMO"
    if any(k in h_lower for k in HERD_KEYWORDS):
        return "HERD"
    if any(k in h_lower for k in PANIC_KEYWORDS):
        return "PANIC"
        
    # Filter out emotional or behavioral content from the neutral class
    if any(k in h_lower for k in NEUTRAL_EXCLUDE_KEYWORDS):
        return "EXCLUDE"
        
    return "NEUTRAL"

def main():
    raw_path = "data/raw_headlines.csv"
    labelled_path = "data/labelled_headlines.csv"
    
    if not os.path.exists(raw_path):
        print(f"ERROR: '{raw_path}' not found! Run 01_scrape.py first.")
        return
        
    df = pd.read_csv(raw_path, encoding="utf-8")
    print(f"Loaded {len(df)} raw scraped headlines.")
    
    # Label each headline
    labels = []
    for idx, row in df.iterrows():
        headline = row["headline"]
        q_source = row["query_source"]
        
        # If it came from a targeted behavioral search query, we trust the source label
        if q_source in ["FOMO", "HERD", "LOSS_AVERSION", "COGNITIVE_DISSONANCE", "PANIC"]:
            labels.append(q_source)
        else:
            # General feeds are parsed with keyword heuristics
            labels.append(classify_general_headline(headline))
            
    df["label"] = labels
    # Remove excluded headlines (contaminated neutrals)
    df = df[df["label"] != "EXCLUDE"].reset_index(drop=True)
    
    print("\nInitial Crawled Label Distribution:")
    counts = df["label"].value_counts()
    for label, count in counts.items():
        print(f"  {label:<25}: {count} headlines")
        
    # To prevent bias, under-sample the NEUTRAL class to 150 headlines.
    # Keep all other real-world categories as they are.
    df_neutral = df[df["label"] == "NEUTRAL"]
    df_non_neutral = df[df["label"] != "NEUTRAL"]
    
    target_neutral = 150
    if len(df_neutral) > target_neutral:
        df_neutral_sampled = df_neutral.sample(n=target_neutral, random_state=42)
        df_final = pd.concat([df_neutral_sampled, df_non_neutral], ignore_index=True)
        print(f"\nUnder-sampled NEUTRAL class to {target_neutral} headlines.")
    else:
        df_final = df
        print("\nKeeping all NEUTRAL headlines.")
        
    # Shuffle the final dataset
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("\n--- Final Balanced 100% Real-World Dataset ---")
    final_counts = df_final["label"].value_counts()
    for label, count in final_counts.items():
        print(f"  {label:<25}: {count} headlines")
    print(f"  Total Dataset Size: {final_counts.sum()}")
    print("----------------------------------------------")
    
    # Save to labelled_headlines.csv
    df_final.to_csv(labelled_path, index=False, encoding="utf-8")
    print(f"Saved balanced, 100% real-world dataset to '{labelled_path}'.")

if __name__ == "__main__":
    main()
