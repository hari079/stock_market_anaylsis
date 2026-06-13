#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
05_charts.py - Behavioural Finance Paper Visualisations
Loads labelled headlines and generates three publication-ready figures:
1. Label Distribution Bar Chart (label_distribution.png)
2. Sentiment Pie Chart (sentiment_pie.png)
3. Behavioural Phase Timeline (phase_timeline.png)
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Global chart style settings for publication readiness
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

def generate_charts():
    print("=" * 60)
    print("      GENERATING RESEARCH-PAPER VISUALISATIONS")
    print("=" * 60)
    
    labelled_path = "data/labelled_headlines.csv"
    if not os.path.exists(labelled_path):
        print(f"ERROR: '{labelled_path}' not found! Run 01_scrape.py and augment_data.py first.")
        return
        
    df = pd.read_csv(labelled_path, encoding="utf-8")
    df = df.dropna(subset=["label"])
    df = df[df["label"].str.strip() != ""]
    
    # Get class counts
    counts = df["label"].value_counts()
    
    # -------------------------------------------------------------
    # Chart 1 — Label Distribution Bar Chart (label_distribution.png)
    # -------------------------------------------------------------
    print("Creating Chart 1: Label Distribution...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    
    # Tailored HSL-like color palette
    colors = ["#4a90e2", "#f5a623", "#e2844a", "#d0021b", "#7ed321", "#9013fe"]
    
    bars = ax.bar(counts.index, counts.values, color=colors[:len(counts)], edgecolor='#444444', linewidth=1, alpha=0.9)
    
    # Clean, minimal styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#888888')
    ax.get_yaxis().set_visible(False) # No gridlines or axis on y
    
    # Put counts on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2.,
            height + 15,
            f"{int(height)}",
            ha='center',
            va='bottom',
            fontsize=10,
            fontweight='bold',
            color='#333333'
        )
        
    plt.title("Distribution of Behavioural Signals in Financial Headlines\n(2026 Iran War Period)", fontsize=13, fontweight='bold', pad=20)
    plt.xticks(rotation=20, ha='right', fontsize=9)
    plt.tight_layout()
    plt.savefig("label_distribution.png", dpi=150)
    plt.close()
    print("  Saved 'label_distribution.png'")
    
    # -------------------------------------------------------------
    # Chart 2 — Sentiment Pie Chart (sentiment_pie.png)
    # -------------------------------------------------------------
    print("Creating Chart 2: Sentiment Proportions Pie Chart...")
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    
    # Explode the largest slice (which is NEUTRAL)
    explode = [0.05 if idx == 0 else 0 for idx in range(len(counts))]
    
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct='%1.1f%%',
        startangle=140,
        explode=explode,
        colors=colors[:len(counts)],
        wedgeprops=dict(edgecolor='#FFFFFF', linewidth=1.5, alpha=0.9),
        textprops=dict(fontsize=9, fontweight='medium')
    )
    
    # Bold the percentage labels
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        
    plt.title("Investor Sentiment Distribution — 2026 Iran War Headlines", fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig("sentiment_pie.png", dpi=150)
    plt.close()
    print("  Saved 'sentiment_pie.png'")
    
    # -------------------------------------------------------------
    # Chart 3 — Behavioural Phase Timeline (phase_timeline.png)
    # -------------------------------------------------------------
    print("Creating Chart 3: Behavioural Phase Timeline Flow Diagram...")
    fig, ax = plt.subplots(figsize=(14, 5.5), dpi=150)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Box configuration
    box_width = 0.18
    box_height = 0.22
    y_start = 0.45
    x_positions = [0.05, 0.29, 0.53, 0.77]
    
    # Curated phase information
    phases = [
        {
            "num": "Phase 1",
            "name": "FOMO",
            "date": "Jan–Feb 2026",
            "color": "#fff59d",  # Soft yellow
            "border": "#fbc02d",
            "desc": "Retail buyers pile in\nfearing missing gains\nas gold & bitcoin rally"
        },
        {
            "num": "Phase 2",
            "name": "Panic Buying",
            "date": "Feb 28 2026",
            "color": "#ffcc80",  # Soft orange
            "border": "#f57c00",
            "desc": "Iran missile strike sparks\nsupply shock & massive\nrush to safe havens"
        },
        {
            "num": "Phase 3",
            "name": "Herd Selling",
            "date": "Mar 2026",
            "color": "#ef9a9a",  # Soft red
            "border": "#d32f2f",
            "desc": "Mass retail capitulation;\nsheep-like panic herds\ndump risk assets in rout"
        },
        {
            "num": "Phase 4",
            "name": "Smart Money",
            "date": "Apr 2026",
            "color": "#a5d6a7",  # Soft green
            "border": "#388e3c",
            "desc": "Institutional buying and\nsmart accumulation at\nundervalued bottoms"
        }
    ]
    
    # Draw boxes, text, and arrows
    for idx, ph in enumerate(phases):
        x = x_positions[idx]
        
        # Add FancyBboxPatch (rounded corner rectangle)
        rect = patches.FancyBboxPatch(
            (x, y_start),
            box_width,
            box_height,
            boxstyle="round,pad=0.01",
            facecolor=ph["color"],
            edgecolor=ph["border"],
            linewidth=2,
            zorder=2
        )
        ax.add_patch(rect)
        
        # Header inside the box (Phase Number)
        ax.text(
            x + box_width/2,
            y_start + box_height - 0.05,
            ph["num"],
            ha='center',
            va='center',
            fontsize=10,
            fontweight='bold',
            color='#555555'
        )
        
        # Phase Name inside the box
        ax.text(
            x + box_width/2,
            y_start + box_height/2 + 0.01,
            ph["name"],
            ha='center',
            va='center',
            fontsize=12,
            fontweight='bold',
            color='#111111'
        )
        
        # Date inside the box
        ax.text(
            x + box_width/2,
            y_start + 0.04,
            ph["date"],
            ha='center',
            va='center',
            fontsize=9,
            style='italic',
            color='#444444'
        )
        
        # Description below the box
        ax.text(
            x + box_width/2,
            y_start - 0.05,
            ph["desc"],
            ha='center',
            va='top',
            fontsize=9.5,
            color='#333333',
            linespacing=1.3
        )
        
        # Draw arrow connecting to next phase
        if idx < len(phases) - 1:
            x_arrow_start = x + box_width + 0.015
            x_arrow_end = x_positions[idx+1] - 0.015
            y_arrow = y_start + box_height/2
            
            # Draw beautiful arrow
            ax.annotate(
                '',
                xy=(x_arrow_end, y_arrow),
                xytext=(x_arrow_start, y_arrow),
                arrowprops=dict(
                    arrowstyle="-|>",
                    lw=2.5,
                    color='#777777',
                    mutation_scale=15,
                    shrinkA=0,
                    shrinkB=0
                )
            )
            
    plt.title("The Four-Phase Behavioural Cycle — 2026 Iran War", fontsize=15, fontweight='bold', y=0.92, pad=10)
    plt.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.02)
    plt.savefig("phase_timeline.png", dpi=150)
    plt.close()
    print("  Saved 'phase_timeline.png'")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    generate_charts()
