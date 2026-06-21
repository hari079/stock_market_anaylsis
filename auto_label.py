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

# Centralized keywords loading
import json
import re

KEYWORDS_PATH = "data/keywords.json"
if os.path.exists(KEYWORDS_PATH):
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        KEYWORDS = json.load(f)
else:
    KEYWORDS = {}

FOMO_KEYWORDS = KEYWORDS.get("FOMO", [])
HERD_KEYWORDS = KEYWORDS.get("HERD", [])
LOSS_KEYWORDS = KEYWORDS.get("LOSS_AVERSION", [])
COG_KEYWORDS = KEYWORDS.get("COGNITIVE_DISSONANCE", [])
PANIC_KEYWORDS = KEYWORDS.get("PANIC", [])
NEUTRAL_EXCLUDE_KEYWORDS = KEYWORDS.get("NEUTRAL_EXCLUDE", [])

def contains_hedging(t):
    t_lower = t.lower()
    # Remove institutional references
    t_clean = re.sub(r'\bhedge(?:s|d)?\s+funds?\b', '', t_lower)
    t_clean = re.sub(r'\bhedge[-s]*funds?\b', '', t_clean)
    t_clean = re.sub(r'\bhedgeye\b', '', t_clean)
    
    # Now check for hedging terms
    for kw in ['hedging', 'hedged', 'hedging strategies', 'hedging strategy', 'hedging positions', 'hedging position']:
        if kw in t_clean:
            return True
    if 'hedge against' in t_clean:
        return True
    
    # Standalone 'hedge' as a word
    if re.search(r'\bhedge(s|d)?\b', t_clean):
        return True
        
    return False

def classify_general_headline(headline):
    """
    Classifies a general headline using text heuristics.
    Excludes headlines containing active sentiment/emotional features to keep NEUTRAL purely factual.
    """
    h_lower = headline.lower()
    
    if contains_hedging(headline):
        return "LOSS_AVERSION"
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
