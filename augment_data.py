#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
augment_data.py - Behavioural Finance Dataset Augmentor
Generates high-fidelity academic-aligned behavioural finance headlines
using template expansion, merges them with crawled raw headlines, 
applies heuristics, removes duplicates, and balances the final dataset.
"""

import os
import random
import pandas as pd
from auto_label import classify_general_headline

# Set seed for reproducibility
random.seed(42)

ASSETS = [
    "Bitcoin", "Gold", "Oil", "Tesla", "Nvidia", "Apple", "Ethereum", 
    "Tech stocks", "S&P 500", "US Dollar", "Crude Oil", "Meme coins", 
    "Treasury yields", "Real estate", "Silver", "Crypto markets", "AI stocks",
    "Nasdaq", "Bank stocks", "Natural Gas"
]

PERCENTAGES = ["10", "12", "15", "20", "25", "30", "40", "50"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PRICES = ["$80", "$1,200", "$60,000", "$150", "$2,000", "$450", "$95", "$3,500"]

TEMPLATES = {
    "FOMO": [
        "Retail buyers pile into {asset} as prices skyrocket",
        "Don't miss out on the next {asset} rally, experts warn",
        "FOMO grips investors as {asset} surges to new record highs",
        "Buying frenzy pushes {asset} to unsustainable levels",
        "Retail mania driving {asset} parabolic as latecomers jump in",
        "Fearing they will miss the boat, retail investors flock to {asset}",
        "Is {asset} the next big thing? Retail buyers are rushing to buy",
        "Frenzy in {asset} options market as traders bet on massive rally",
        "Investors chase the {asset} rally despite warnings of a bubble",
        "Piling into {asset}: The retail crowd refuses to stay on the sidelines",
        "Fear of missing out drives massive retail inflow into {asset}",
        "Retail traders trigger short squeeze in {asset} as FOMO peaks",
        "Speculators buy {asset} at all-time highs fearing further gains",
        "Public interest in {asset} spikes as retail buyers chase momentum",
        "Late-stage FOMO drives massive surge in {asset} trading activity"
    ],
    "HERD": [
        "Retail investors dump {asset} in massive flocking exit",
        "Herd mentality takes over as crowd dumps {asset} holdings",
        "Exodus from {asset} continues as investors follow the crowd",
        "Everyone is selling {asset}, causing retail panic herd",
        "Investors flee {asset} as market crowd moves to cash",
        "Mass retail dumping of {asset} triggers copycat selling",
        "Follow the leader: Retail crowd copies institutional exit from {asset}",
        "Flocking to exit: Why everyone is selling their {asset} today",
        "Sheep-like panic triggers massive retail exit from {asset}",
        "Retail crowd scrambles to dump {asset} as sell-off intensifies",
        "Panic selling spreads to retail investors flocking out of {asset}",
        "Crowd dynamics take over as investors simultaneously dump {asset}",
        "Exodus from {asset} funds gathers steam amid widespread pessimism",
        "Investors herd into cash, selling off {asset} positions in unison",
        "Follow-the-crowd behavior causes sharp retail drawdown in {asset}"
    ],
    "PANIC": [
        "Bloodbath in {asset} market as prices plunge {percent}%",
        "Panic selling grips {asset} as market crashes suddenly",
        "Capitulation: Investors dump {asset} in absolute market rout",
        "Severe {asset} sell-off triggers circuit breakers, prices crash",
        "{asset} plunges into free fall as panic grips Wall Street",
        "Traders capitulate as {asset} suffers its worst day in years",
        "Absolute carnage in {asset} as selloff wipes out billions",
        "Market panic triggers emergency liquidations in {asset}",
        "{asset} market crashes as investors capitulate in panic",
        "Plunging {asset} prices spark widespread fear and forced selling",
        "{asset} prices collapse by {percent}% in sudden panic-driven rout",
        "Widespread panic triggers margin calls and liquidation of {asset}",
        "Frightened investors dump {asset} in chaotic market capitulation",
        "Crash warning: {asset} enters free fall as stop-losses trigger",
        "Sell-off accelerates in {asset} as fear index hits record high"
    ],
    "LOSS_AVERSION": [
        "Investors hold onto {asset} despite severe {percent}% drawdown hoping for recovery",
        "Refusing to sell: Retail bagholders cling to {asset} despite losses",
        "Loss aversion keeps investors trapped in losing {asset} positions",
        "Holding losing bags: Why retail won't lock in {asset} losses",
        "Stubborn investors refuse to cut losses on declining {asset}",
        "{asset} down {percent}%, but investors hold tight hoping to break even",
        "Psychology of the bagholder: Refusing to sell {asset} at a loss",
        "Loss aversion rules: Traders double down on losing {asset} trades",
        "Unwilling to sell: Retail investors hold {asset} through deep drawdown",
        "Hoping for a rebound: Investors refuse to exit their losing {asset} bets",
        "Loss aversion prevents investors from cutting ties with falling {asset}",
        "Retail traders hold {asset} bags, refusing to realize paper losses",
        "Stubborn retail holding keeps {asset} positions active despite deep red",
        "Reluctance to take losses leads to stagnation in retail {asset} portfolios",
        "Holding {asset} all the way down: The psychological cost of loss aversion"
    ],
    "COGNITIVE_DISSONANCE": [
        "{asset} shrugs off bad news, continuing its rally despite macro shock",
        "Ignoring warnings: {asset} defies negative inflation report",
        "{asset} rally continues despite clear indicators of economic slowdown",
        "Cognitive dissonance: Markets ignore {asset} regulatory crackdowns",
        "{asset} prices rise despite disappointing corporate earnings report",
        "Defying gravity: {asset} shrugs off geopolitical tension and rises",
        "Investors dismiss warnings of {asset} correction, pushing prices higher",
        "Why the market is ignoring bad news and buying {asset} anyway",
        "{asset} defies negative analyst forecasts with surprise rally",
        "Ignoring the red flags: Retail buyers bid up {asset} despite risks",
        "{asset} price surges even as regulatory warning signals emerge",
        "Market shrugs off {asset} supply issues as speculation continues",
        "Cognitive dissonance grows as investors buy {asset} despite crash threats",
        "Bullish momentum in {asset} persists despite rising interest rates",
        "{asset} markets remain blind to risk, extending rally on bad news"
    ],
    "NEUTRAL": [
        "{asset} settles at {price} on {day} afternoon trade",
        "Factual update: {asset} trading volume holds steady",
        "Federal Reserve announces latest interest rate decision",
        "{asset} price remains unchanged ahead of earnings report",
        "Analysts release quarterly revenue forecast for {asset}",
        "Central bank reports modest economic growth in Q1",
        "Trading volume for {asset} matches three-month average",
        "{asset} price fluctuates within narrow range during morning session",
        "New regulatory guidelines issued for {asset} market participants",
        "Company executive outlines long-term strategy for {asset} growth",
        "{asset} markets close for the weekend after quiet trading day",
        "Department of Labor releases latest employment data on {day}",
        "{asset} index undergoes annual rebalancing with minimal impact",
        "Factual report: {asset} imports rise slightly in quarterly summary",
        "Treasury department issues scheduled auction results for {asset}",
        "Scheduled regulatory review of {asset} completed without action",
        "Economists publish revised baseline outlook for {asset} markets",
        "Standard contract updates finalized for {asset} futures traders",
        "{asset} commercial distribution rates remain at seasonal averages",
        "Retail stores report steady supply of {asset} products",
        "Industry conference discusses technical developments in {asset}",
        "New study evaluates historical performance trends of {asset}",
        "Annual meeting of {asset} trade association scheduled for Q3",
        "{asset} processing plants operate within normal parameters",
        "Statistical summary: {asset} export volumes unchanged this month",
        "Local governments issue guidelines on {asset} resource management",
        "Academic research paper reviews long-term utility of {asset}"
    ]
}

def generate_augmented_headlines():
    augmented_records = []
    
    for label, templates_list in TEMPLATES.items():
        # Cross-multiply templates and assets to generate rich data
        for template in templates_list:
            for asset in ASSETS:
                headline = template.format(
                    asset=asset,
                    percent=random.choice(PERCENTAGES),
                    day=random.choice(DAYS),
                    price=random.choice(PRICES)
                )
                augmented_records.append({
                    "source": "Academic Augmentation",
                    "headline": headline,
                    "date": "2026-06-13",
                    "query_source": "AUGMENTED",
                    "label": label
                })
                
    # Create DataFrame
    df_aug = pd.DataFrame(augmented_records)
    print(f"Generated {len(df_aug)} augmented headlines via template expansion.")
    return df_aug

def merge_and_balance_datasets():
    print("=" * 60)
    print("      BEHAVIOURAL FINANCE DATASET AUGMENTATION")
    print("=" * 60)
    
    raw_path = "data/raw_headlines.csv"
    labelled_path = "data/labelled_headlines.csv"
    
    # 1. Load raw scraped data if available
    df_scraped_labelled = pd.DataFrame()
    if os.path.exists(raw_path):
        df_raw = pd.read_csv(raw_path, encoding="utf-8")
        print(f"Loaded {len(df_raw)} raw scraped headlines.")
        
        # Apply labels based on query source or heuristics
        labels = []
        for idx, row in df_raw.iterrows():
            q_source = row["query_source"]
            headline = row["headline"]
            
            if q_source in ["FOMO", "HERD", "LOSS_AVERSION", "COGNITIVE_DISSONANCE", "PANIC"]:
                labels.append(q_source)
            else:
                # Exclude general RSS feeds to prevent NEUTRAL class contamination
                labels.append("EXCLUDE")
                
        df_raw["label"] = labels
        # Filter out contaminated neutral headlines
        df_raw = df_raw[df_raw["label"] != "EXCLUDE"].reset_index(drop=True)
        df_scraped_labelled = df_raw
    else:
        print("WARNING: 'data/raw_headlines.csv' not found. Will rely solely on augmented template data.")

    # 2. Generate augmented academic data
    df_augmented = generate_augmented_headlines()
    
    # 3. Combine datasets
    df_combined = pd.concat([df_scraped_labelled, df_augmented], ignore_index=True)
    
    # 4. Clean duplicates
    initial_count = len(df_combined)
    df_combined["headline_lower"] = df_combined["headline"].str.lower()
    df_combined = df_combined.drop_duplicates(subset=["headline_lower"])
    df_combined = df_combined.drop(columns=["headline_lower"])
    print(f"Combined dataset size: {initial_count} -> {len(df_combined)} (removed {initial_count - len(df_combined)} duplicates)")
    
    # 5. Dynamic Smart Balancing
    # Let's inspect class distribution
    print("\nPre-balanced distribution:")
    dist = df_combined["label"].value_counts()
    for label, count in dist.items():
        print(f"  {label:<25}: {count} headlines")
        
    # We want a balanced dataset. Let's aim to have 400-500 samples per class if possible.
    # To avoid neutral class over-dominance, we cap NEUTRAL at 450.
    # We also keep other classes balanced.
    balanced_dfs = []
    target_count = 400
    
    for label in ["FOMO", "HERD", "PANIC", "LOSS_AVERSION", "COGNITIVE_DISSONANCE", "NEUTRAL"]:
        df_class = df_combined[df_combined["label"] == label]
        
        if len(df_class) > target_count:
            # Under-sample to target_count
            df_class_balanced = df_class.sample(n=target_count, random_state=42)
            print(f"  Under-sampled {label:<21} from {len(df_class)} to {target_count}")
        else:
            # Keep all since it's below or at the target
            df_class_balanced = df_class
            print(f"  Kept all {len(df_class)} samples for {label:<21}")
            
        balanced_dfs.append(df_class_balanced)
        
    df_final = pd.concat(balanced_dfs, ignore_index=True)
    # Shuffle final dataset
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("\n--- Final Balanced Augmented Dataset Distribution ---")
    final_counts = df_final["label"].value_counts()
    for label, count in final_counts.items():
        print(f"  {label:<25}: {count} headlines")
    print(f"  Total Dataset Size: {final_counts.sum()} headlines")
    print("=" * 60)
    
    # Save to labelled_headlines.csv
    os.makedirs("data", exist_ok=True)
    df_final.to_csv(labelled_path, index=False, encoding="utf-8")
    print(f"Dataset successfully augmented and saved to '{labelled_path}'.")

if __name__ == "__main__":
    merge_and_balance_datasets()
