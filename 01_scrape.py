#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
01_scrape.py - Behavioural Finance News Headline Scraper
Scrapes 100% real-world headlines from RSS feeds and Google News search feeds.
Expanded search queries are used to find more articles for minority categories.
"""

import os
import re
import time
import urllib.parse
from datetime import datetime
import pandas as pd
import feedparser

KEYWORDS = [
    "gold", "bitcoin", "crypto", "oil", "surge", "crash", "panic", "fear", 
    "fomo", "herd", "rally", "sell-off", "plunge", "soar", "iran", 
    "geopolitical", "safe haven", "investors flee", "pile in", "dump", 
    "capitulate", "bubble", "spike", "exodus", "bloodbath", "shrug", 
    "dismiss", "despite", "refuse", "hold", "loss aversion", "cognitive dissonance"
]

def clean_title(title, source):
    title = title.strip()
    if " - " in title:
        parts = title.rsplit(" - ", 1)
        suffix = parts[1].lower()
        if any(s in suffix for s in [source.lower(), "reuters", "cnbc", "coindesk", "investing", "marketwatch", "yahoo", "wsj", "bloomberg", "forbes", "ft", "economist"]):
            title = parts[0].strip()
    
    title = re.sub(r'<[^>]+>', '', title)
    title = title.replace('"', '').strip()
    return title

def match_keywords(title):
    title_lower = title.lower()
    for kw in KEYWORDS:
        if kw in title_lower:
            return True
    return False

def scrape_feeds():
    print("=" * 60)
    print("      REAL-WORLD BEHAVIOURAL FINANCE HEADLINE SCRAPER")
    print("=" * 60)
    
    os.makedirs("data", exist_ok=True)
    
    feeds = [
        {"name": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=15839069", "query_type": "GENERAL"},
        {"name": "CNBC", "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147", "query_type": "GENERAL"},
        {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml", "query_type": "GENERAL"},
        {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/category/markets/?outputType=xml", "query_type": "GENERAL"},
        {"name": "Investing.com", "url": "https://www.investing.com/rss/news_95.rss", "query_type": "GENERAL"},
        {"name": "MarketWatch", "url": "http://feeds.marketwatch.com/marketwatch/topstories/", "query_type": "GENERAL"},
    ]
    
    # 2. General market/geopolitical searches (crawling major sources for 2026 Iran War context)
    sources = ["reuters.com", "cnbc.com", "coindesk.com", "investing.com", "marketwatch.com", "finance.yahoo.com", "wsj.com", "bloomberg.com"]
    general_queries = [
        "gold OR oil OR geopolitical OR iran",
        "bitcoin OR crypto OR crash OR rally OR panic OR fear OR fomo",
        "market OR safe haven OR plunge OR surge OR sell-off"
    ]
    
    for src in sources:
        for q in general_queries:
            query_str = f"site:{src} ({q})"
            encoded = urllib.parse.quote_plus(query_str)
            feeds.append({
                "name": src.split(".")[0].capitalize(),
                "url": f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en",
                "query_type": "GENERAL"
            })
            
    # 3. Expanded Behavioral Finance Google News RSS searches to find actual, real-world headlines
    behavioral_searches = [
        # FOMO
        {"label": "FOMO", "query": "FOMO OR \"buying frenzy\" OR \"pile in\" OR \"retail mania\" (investors OR stocks OR crypto OR market)"},
        {"label": "FOMO", "query": "\"fear of missing out\" OR \"buying spree\" OR \"market mania\" (investors OR stock OR crypto)"},
        # HERD
        {"label": "HERD", "query": "(\"herd behavior\" OR \"herd mentality\" OR \"investors flee\" OR \"exodus\" OR \"mass dump\") (investors OR finance OR stocks OR crypto)"},
        {"label": "HERD", "query": "(\"flock to buy\" OR \"panic selling herd\" OR \"retail crowd\") (investors OR market OR stocks)"},
        # LOSS_AVERSION
        {"label": "LOSS_AVERSION", "query": "(\"loss aversion\" OR \"refuse to sell\" OR \"holding onto\" OR \"drawdown\") (investors OR finance OR stock OR crypto)"},
        {"label": "LOSS_AVERSION", "query": "(\"holding losing\" OR \"drawdown hoping\" OR \"unwilling to sell\" OR \"lock in losses\") (investors OR market)"},
        # COGNITIVE_DISSONANCE
        {"label": "COGNITIVE_DISSONANCE", "query": "(\"cognitive dissonance\" OR \"shrugs off\" OR \"dismisses bad news\" OR \"ignores warning\") (investors OR market OR stocks OR crypto)"},
        {"label": "COGNITIVE_DISSONANCE", "query": "(\"market ignores\" OR \"shrug off war\" OR \"rally continues despite\" OR \"stocks defy\") (investors OR finance)"},
        # PANIC
        {"label": "PANIC", "query": "(panic OR bloodbath OR capitulate OR rout OR plunge OR crash) (investors OR finance OR stock OR crypto OR market)"},
        {"label": "PANIC", "query": "(market panic OR panic selling OR panic sell OR capitulation) (investors OR stocks OR crypto)"}
    ]
    
    for bs in behavioral_searches:
        encoded_query = urllib.parse.quote_plus(bs["query"])
        feeds.append({
            "name": "Google News Search",
            "url": f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en",
            "query_type": bs["label"]
        })
        
    all_headlines = []
    
    for idx, feed in enumerate(feeds, 1):
        name = feed["name"]
        url = feed["url"]
        q_type = feed["query_type"]
        
        display_url = url[:60] + "..." if len(url) > 60 else url
        print(f"[{idx}/{len(feeds)}] Scraping {name} ({q_type}) from {display_url}")
        
        try:
            parsed = feedparser.parse(url)
            if not parsed.entries:
                continue
                
            for entry in parsed.entries:
                raw_title = entry.get("title", "")
                if not raw_title:
                    continue
                    
                cleaned = clean_title(raw_title, name)
                
                if q_type == "GENERAL" and not match_keywords(cleaned):
                    continue
                
                if 'published_parsed' in entry and entry.published_parsed:
                    date_str = time.strftime('%Y-%m-%d', entry.published_parsed)
                elif 'updated_parsed' in entry and entry.updated_parsed:
                    date_str = time.strftime('%Y-%m-%d', entry.updated_parsed)
                else:
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    
                all_headlines.append({
                    "source": name,
                    "headline": cleaned,
                    "date": date_str,
                    "query_source": q_type,
                    "label": ""
                })
        except Exception as e:
            print(f"  WARNING: Failed to scrape {name}: {e}. Continuing...")
            
    if not all_headlines:
        print("\nERROR: No headlines collected!")
        return
        
    df = pd.DataFrame(all_headlines)
    
    initial_count = len(df)
    df["headline_lower"] = df["headline"].str.lower()
    df = df.drop_duplicates(subset=["headline_lower"])
    df = df.drop(columns=["headline_lower"])
    final_count = len(df)
    
    print("\n" + "=" * 60)
    print("                     SCRAPING STATISTICS")
    print("=" * 60)
    print(f"  Total Raw Articles Scraping   : {initial_count}")
    print(f"  Duplicates Removed            : {initial_count - final_count}")
    print(f"  Total Unique Headlines Saved  : {final_count}")
    print("=" * 60)
    
    df.to_csv("data/raw_headlines.csv", index=False, encoding="utf-8")
    print("\nSaved raw headlines to 'data/raw_headlines.csv' successfully.")

if __name__ == "__main__":
    scrape_feeds()
