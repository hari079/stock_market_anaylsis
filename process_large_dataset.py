#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
process_large_dataset.py - Scale dataset using Benzinga and Template Augmentation
Extracts real-world behavioral headlines from Benzinga dataset (prioritizing war context),
supplements underrepresented classes with template-expanded headlines,
and creates a balanced dataset of 24,000 headlines (4,000 per class).
"""

import os
import random
import pandas as pd

# Set seed for reproducibility
random.seed(42)

# Assets and templates for synthetic generation
ASSETS = [
    "Bitcoin", "Gold", "Oil", "Tesla", "Nvidia", "Apple", "Ethereum", 
    "Tech stocks", "S&P 500", "US Dollar", "Crude Oil", "Meme coins", 
    "Treasury yields", "Real estate", "Silver", "Crypto markets", "AI stocks",
    "Nasdaq", "Bank stocks", "Natural Gas", "Defense stocks", "Wheat", "Commodities"
]

PERCENTAGES = ["5", "10", "12", "15", "20", "25", "30", "40", "50", "60"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PRICES = ["$80", "$1,200", "$60,000", "$150", "$2,000", "$450", "$95", "$3,500", "$250", "$1,800"]

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
        "Late-stage FOMO drives massive surge in {asset} trading activity",
        "Wall Street piles into {asset} following military escalation",
        "Investors rush to buy {asset} amid rising geopolitical tensions",
        "FOMO grips safe havens as {asset} surges on war fears",
        "Buying frenzy in {asset} as traders bet on supply shortages",
        "Retail traders chase the {asset} rally as conflict deepens"
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
        "Follow-the-crowd behavior causes sharp retail drawdown in {asset}",
        "Retail investors flee {asset} as war concerns spread",
        "Herd mentality takes over as crowd dumps {asset} after strikes",
        "Exodus from {asset} intensifies as everyone exits risk assets",
        "Follow the crowd: retail stampede out of {asset} gathers steam",
        "Crowd floods into safe havens, leaving {asset} completely abandoned"
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
        "Sell-off accelerates in {asset} as fear index hits record high",
        "Bloodbath in {asset} market as escalation triggers panic selloff",
        "Panic selling grips {asset} as missile strikes spark crash",
        "Capitulation: traders dump {asset} in chaotic market rout",
        "Severe {asset} selloff as war headlines trigger margin calls",
        "{asset} plunges into free fall as geopolitical crisis worsens"
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
        "Holding {asset} all the way down: The psychological cost of loss aversion",
        "Investors hold onto {asset} despite severe war-driven drawdown hoping for rebound",
        "Refusing to sell: retail bagholders cling to {asset} despite military escalation",
        "Loss aversion keeps traders trapped in losing {asset} positions during crisis",
        "Stubborn investors refuse to cut losses on declining {asset} amid sanctions",
        "Unwilling to take losses, investors hold tight on {asset} through deep drawdown",
        "{asset} investors increase hedging strategies as drawdown deepens",
        "{asset} traders ramp up hedging to protect against further downside",
        "Fearing heavy losses, investors build hedging positions in {asset}",
        "Hedging strategies spike in {asset} as traders guard against price declines",
        "Faced with severe drawdown, investors buy {asset} as inflation hedge"
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
        "Markets remain blind to risk, extending rally on bad news",
        "{asset} shrugs off geopolitical tension, extending surprise rally",
        "Ignoring warnings: {asset} defies reports of military strikes",
        "{asset} rally continues despite escalation of border conflict",
        "Cognitive dissonance: markets ignore {asset} war risk and bid up prices",
        "Defying gravity: {asset} ignores macro shocks and rises anyway"
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
        "Cybersecurity updates released for major exchange systems",
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
        "Academic research paper reviews long-term utility of {asset}",
        "{asset} distribution remains stable amid ongoing peace talks",
        "Factual report: central bank reviews interest rates during geopolitical talks",
        "Scheduled military budget review completed without market impact for {asset}",
        "{asset} imports and exports hold steady in monthly trade data",
        "Economists publish revised baseline outlook for global {asset} supply chains"
    ]
}

# Centralized keywords loading
import json
import re

KEYWORDS_PATH = "data/keywords.json"
if os.path.exists(KEYWORDS_PATH):
    print(f"Loading keywords from '{KEYWORDS_PATH}'...")
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        KEYWORDS = json.load(f)
else:
    print(f"WARNING: '{KEYWORDS_PATH}' not found! Using fallback default keywords.")
    KEYWORDS = {}

FOMO_KEYWORDS = KEYWORDS.get("FOMO", [])
HERD_KEYWORDS = KEYWORDS.get("HERD", [])
LOSS_KEYWORDS = KEYWORDS.get("LOSS_AVERSION", [])
COG_KEYWORDS = KEYWORDS.get("COGNITIVE_DISSONANCE", [])
PANIC_KEYWORDS = KEYWORDS.get("PANIC", [])
NEUTRAL_EXCLUDE_KEYWORDS = KEYWORDS.get("NEUTRAL_EXCLUDE", [])
WAR_KEYWORDS = KEYWORDS.get("WAR", [])

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

def classify_headline(t):
    t_lower = t.lower()
    # Check custom regex-based hedging rules first to avoid false-exclusion on NEUTRAL_EXCLUDE
    if contains_hedging(t):
        return "LOSS_AVERSION"
    if any(k in t_lower for k in LOSS_KEYWORDS):
        return "LOSS_AVERSION"
    if any(k in t_lower for k in COG_KEYWORDS):
        return "COGNITIVE_DISSONANCE"
    if any(k in t_lower for k in FOMO_KEYWORDS):
        return "FOMO"
    if any(k in t_lower for k in HERD_KEYWORDS):
        return "HERD"
    if any(k in t_lower for k in PANIC_KEYWORDS):
        return "PANIC"
    if any(k in t_lower for k in NEUTRAL_EXCLUDE_KEYWORDS):
        return "EXCLUDE"
    return "NEUTRAL"

MODIFIERS = [
    "", "", "", "", # 40% chance of no modifier
    "Breaking: ", "Market Alert: ", "Update: ", "Analyst warning: ", 
    "Report: ", "Flash: ", "Just in: ", "Trading update: "
]

TIMEFRAMES = [
    "", "", "", "", # 40% chance of no timeframe
    "today", "this week", "in morning trade", "overnight", 
    "on Friday", "after hours", "this month", "suddenly"
]

def generate_synthetic(label, count):
    """
    Generates unique synthetic headlines for a class using templates, assets, modifiers, and timeframes.
    """
    generated = set()
    templates = TEMPLATES[label]
    
    # We loop until we get the desired count
    attempts = 0
    while len(generated) < count and attempts < count * 100:
        attempts += 1
        template = random.choice(templates)
        asset = random.choice(ASSETS)
        percent = random.choice(PERCENTAGES)
        day = random.choice(DAYS)
        price = random.choice(PRICES)
        modifier = random.choice(MODIFIERS)
        timeframe = random.choice(TIMEFRAMES)
        
        base_headline = template.format(
            asset=asset,
            percent=percent,
            day=day,
            price=price
        )
        
        # Combine modifier, base headline, and timeframe
        full_headline = f"{modifier}{base_headline} {timeframe}".strip()
        # Clean extra spaces
        full_headline = " ".join(full_headline.split())
        
        generated.add(full_headline)
        
    return list(generated)

def main():
    print("=" * 60)
    print("      SCALING BEHAVIOURAL FINANCE DATASET TO 24,000 SAMPLES")
    print("=" * 60)
    
    raw_path = "data/analyst_ratings_processed.csv"
    if not os.path.exists(raw_path):
        print(f"ERROR: {raw_path} not found! Please download the Benzinga dataset and put it there.")
        return
        
    # Read the dataset in chunks to extract behavioral headlines
    print("Reading Benzinga processed file and extracting behavioral headlines...")
    chunks = pd.read_csv(raw_path, chunksize=100000)
    
    extracted_records = {
        "FOMO": [],
        "HERD": [],
        "PANIC": [],
        "LOSS_AVERSION": [],
        "COGNITIVE_DISSONANCE": [],
        "NEUTRAL": []
    }
    
    # Track war-related headlines for higher priority/weight
    war_extracted_records = {
        "FOMO": [],
        "HERD": [],
        "PANIC": [],
        "LOSS_AVERSION": [],
        "COGNITIVE_DISSONANCE": [],
        "NEUTRAL": []
    }
    
    total_processed = 0
    for chunk in chunks:
        titles = chunk['title'].dropna()
        dates = chunk['date'].fillna('2020-01-01')
        
        for raw_title, raw_date in zip(titles, dates):
            t_lower = raw_title.lower()
            label = classify_headline(raw_title)
            if label == "EXCLUDE":
                continue
            is_war = any(w in t_lower for w in WAR_KEYWORDS)
            
            clean_date = str(raw_date).split(' ')[0] # Get YYYY-MM-DD
            
            record = {
                "headline": raw_title,
                "date": clean_date,
                "source": "Benzinga (Historical)",
                "query_source": "WAR_CONTEXT" if is_war else "HISTORICAL",
                "label": label
            }
            
            if is_war:
                war_extracted_records[label].append(record)
            else:
                extracted_records[label].append(record)
                
            total_processed += 1
            
    print(f"Processed {total_processed} historical headlines.")
    
    # Read live scraped raw headlines if available
    raw_path_scraped = "data/raw_headlines.csv"
    scraped_count = 0
    if os.path.exists(raw_path_scraped):
        try:
            df_raw = pd.read_csv(raw_path_scraped, encoding="utf-8")
            for idx, row in df_raw.iterrows():
                raw_title = row["headline"]
                raw_date = row.get("date", "2026-06-21")
                q_source = row.get("query_source", "HISTORICAL")
                
                # Use query_source label if it is one of our categories, otherwise classify
                if q_source in ["FOMO", "HERD", "LOSS_AVERSION", "COGNITIVE_DISSONANCE", "PANIC"]:
                    label = q_source
                else:
                    label = classify_headline(raw_title)
                    
                if label == "EXCLUDE":
                    continue
                    
                record = {
                    "headline": raw_title,
                    "date": str(raw_date).split(' ')[0],
                    "source": "Scraped RSS Feed",
                    "query_source": "RSS_LIVE",
                    "label": label
                }
                # RSS live scraped headlines are given priority (added to war_extracted_records so they are always included)
                war_extracted_records[label].append(record)
                scraped_count += 1
            print(f"Loaded {scraped_count} live scraped RSS headlines and merged into active set.")
        except Exception as e:
            print(f"Warning: Failed to load scraped raw headlines: {e}")
            
    TARGET_PER_CLASS = 4000
    final_dataset_records = []
    
    print("\n--- Constructing Balanced Dataset (4,000 per class) ---")
    for label in ["FOMO", "HERD", "PANIC", "LOSS_AVERSION", "COGNITIVE_DISSONANCE", "NEUTRAL"]:
        war_list = war_extracted_records[label]
        general_list = extracted_records[label]
        
        total_real = len(war_list) + len(general_list)
        print(f"Class {label}: Found {len(war_list)} war-related and {len(general_list)} general real headlines.")
        
        # Combine war-related first (priority), then general real
        if label == "NEUTRAL":
            # Stratify to prevent geopolitical context bias (limit war headlines to ~15% of the class)
            random.shuffle(war_list)
            real_combined = war_list[:600] + general_list
        else:
            real_combined = war_list + general_list
        
        # Clean duplicates in real combined
        seen_headlines = set()
        real_unique = []
        for r in real_combined:
            hl_lower = r["headline"].lower()
            if hl_lower not in seen_headlines:
                seen_headlines.add(hl_lower)
                real_unique.append(r)
                
        if label == "NEUTRAL":
            # For NEUTRAL, we only use real headlines
            class_records = real_unique[:TARGET_PER_CLASS]
            print(f"  -> Kept {len(class_records)} unique real headlines (fully balanced).")
        else:
            # For behavioral classes, always mix in a baseline of 1,000 synthetic headlines
            # to guarantee vocabulary coverage of theoretical keywords (e.g. piles into, hold tight)
            synthetic_target = 1000
            real_target = TARGET_PER_CLASS - synthetic_target
            
            if len(real_unique) >= real_target:
                selected_real = real_unique[:real_target]
                needed = synthetic_target
            else:
                selected_real = real_unique
                needed = TARGET_PER_CLASS - len(selected_real)
                
            print(f"  -> Kept {len(selected_real)} unique real headlines. Generating {needed} synthetic headlines for vocab coverage...")
            synthetic_headlines = generate_synthetic(label, needed)
            
            class_records = selected_real
            for sh in synthetic_headlines:
                class_records.append({
                    "headline": sh,
                    "date": "2026-06-21",
                    "source": "Academic Augmentation (Scaled)",
                    "query_source": "SYNTHETIC",
                    "label": label
                })
            print(f"  -> Completed class with {len(class_records)} total headlines.")
            
        final_dataset_records.extend(class_records)
        
    # Convert to DataFrame
    df_final = pd.DataFrame(final_dataset_records)
    
    # Shuffle final dataset
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print("\n--- Final balanced scaled dataset distribution ---")
    dist = df_final["label"].value_counts()
    for l, count in dist.items():
        print(f"  {l:<25}: {count} headlines ({count/len(df_final)*100:.1f}%)")
    print(f"  Total samples: {len(df_final)}")
    
    # Save to data/labelled_headlines.csv
    labelled_path = "data/labelled_headlines.csv"
    df_final.to_csv(labelled_path, index=False, encoding="utf-8")
    print(f"\nSaved scaled balanced dataset to '{labelled_path}' successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
