#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
02_label_helper.py - Interactive Labelling Helper Tool
Displays a reference guide for behavioural finance categories, loads raw headlines,
and allows interactive terminal labelling with auto-saving.
"""

import os
import sys
import pandas as pd

# Define mapping from keyboard input to label names
LABEL_MAP = {
    "1": "FOMO",
    "2": "HERD",
    "3": "PANIC",
    "4": "LOSS_AVERSION",
    "5": "COGNITIVE_DISSONANCE",
    "6": "NEUTRAL"
}

# The theories and descriptions printed on startup
GUIDE = """
================================================================================
                    BEHAVIOURAL FINANCE LABELLING GUIDE
================================================================================
1 = FOMO (Fear Of Missing Out)
    - Investors rushing in, "pile in", "don't miss", fear of missing gains.
    - Example: "Gold surges as investors pile in amid Iran fears"

2 = HERD (Herd Behaviour)
    - Mass movement following the crowd, "exodus", "everyone selling", "investors flee".
    - Example: "Retail investors dump gold ETFs in mass exodus"

3 = PANIC (Panic Selling / Sudden Fear)
    - Sharp crash language, "plunge", "rout", "bloodbath", "capitulate", sudden selling.
    - Example: "Bitcoin plunges 15% as panic selling grips crypto market"

4 = LOSS_AVERSION (Reluctance to Realise Losses)
    - Holding losing positions, refusing to sell, "down X% but holding", selling winners early.
    - Example: "Investors hold gold despite 12% drawdown hoping for recovery"

5 = COGNITIVE_DISSONANCE (Ignoring Contradictory Evidence)
    - Markets ignoring bad news, contradictory behaviour, "shrugs off", "dismisses", "despite shock".
    - Example: "Stocks shrug off oil shock, rally continues despite IEA warning"

6 = NEUTRAL (Factual / Informational)
    - Factual price reporting, normal market updates, no emotional or behavioural language.
    - Example: "Oil settles at $81.40 per barrel on Tuesday"

s = Skip headline
q = Quit and save progress
================================================================================
"""

def print_summary(df):
    """
    Prints the summary of labels assigned so far.
    """
    print("\n--- Current Label Distribution Summary ---")
    if "label" not in df.columns or df["label"].isna().all() or (df["label"] == "").all():
        print("  No labels assigned yet.")
        return
        
    counts = df[df["label"].notna() & (df["label"] != "")]["label"].value_counts()
    for label_code, label_name in LABEL_MAP.items():
        count = counts.get(label_name, 0)
        print(f"  {label_name:<25}: {count} headlines")
        
    total_labelled = counts.sum()
    total_total = len(df)
    print(f"  Progress: {total_labelled} / {total_total} labelled ({total_labelled/total_total*100:.1f}%)")
    print("-" * 42)

def main():
    print(GUIDE)
    
    raw_path = "data/raw_headlines.csv"
    labelled_path = "data/labelled_headlines.csv"
    
    if not os.path.exists(raw_path):
        print(f"ERROR: '{raw_path}' not found! Run 01_scrape.py first.")
        sys.exit(1)
        
    # Load raw headlines
    df_raw = pd.read_csv(raw_path, encoding="utf-8")
    
    # If labelled file already exists, load it to preserve progress
    if os.path.exists(labelled_path):
        print(f"Loading existing progress from '{labelled_path}'...")
        df = pd.read_csv(labelled_path, encoding="utf-8")
        # Ensure label column exists
        if "label" not in df.columns:
            df["label"] = ""
        # Align with raw headlines (in case scrape was run again and has new articles)
        # We merge based on headline, keeping existing labels
        df = pd.merge(df_raw, df[["headline", "label"]], on="headline", how="left", suffixes=("_raw", ""))
        if "label_raw" in df.columns:
            df = df.drop(columns=["label_raw"])
        df["label"] = df["label"].fillna("")
    else:
        df = df_raw.copy()
        if "label" not in df.columns:
            df["label"] = ""
        # Ensure empty string for missing labels instead of NaN
        df["label"] = df["label"].fillna("")
        
    print_summary(df)
    
    # Find indices of headlines that still need a label
    unlabelled_indices = df[df["label"] == ""].index.tolist()
    
    if not unlabelled_indices:
        print("\nAll headlines are already labelled! Nothing to do.")
        sys.exit(0)
        
    print(f"Found {len(unlabelled_indices)} unlabelled headlines. Starting interactive session...\n")
    
    for i, idx in enumerate(unlabelled_indices):
        row = df.loc[idx]
        headline = row["headline"]
        source = row["source"]
        date = row["date"]
        
        print(f"\n[{i+1}/{len(unlabelled_indices)}] Source: {source} ({date})")
        print(f"Headline: \"{headline}\"")
        
        while True:
            choice = input("Assign Label [1-6, s=skip, q=quit]: ").strip().lower()
            
            if choice == 'q':
                print("\nSaving progress and quitting...")
                df.to_csv(labelled_path, index=False, encoding="utf-8")
                print(f"Progress saved to '{labelled_path}'.")
                print_summary(df)
                sys.exit(0)
                
            elif choice == 's':
                print("Skipped.")
                break
                
            elif choice in LABEL_MAP:
                selected_label = LABEL_MAP[choice]
                df.at[idx, "label"] = selected_label
                print(f"Labelled as -> {selected_label}")
                
                # Auto-save after every single label as requested
                df.to_csv(labelled_path, index=False, encoding="utf-8")
                break
            else:
                print("Invalid input. Please choose 1, 2, 3, 4, 5, 6, s, or q.")
                
    # If loop completes
    df.to_csv(labelled_path, index=False, encoding="utf-8")
    print(f"\nAll headlines processed. Final labelled dataset saved to '{labelled_path}'.")
    print_summary(df)

if __name__ == "__main__":
    main()
