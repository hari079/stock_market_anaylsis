# Stock Market Behavioral Sentiment Analyzer

> **"From Fear to Capitulation: A Behavioral Analysis of Investor Sentiment During the 2026 Iran War Period"**

A machine learning system that classifies financial news headlines into **6 behavioral finance categories** grounded in academic theory — detecting PANIC, FOMO, HERD behavior, LOSS_AVERSION, COGNITIVE_DISSONANCE, and NEUTRAL sentiment in real time.

---

## 🧠 What This Does

This project scrapes live financial headlines from Google News, labels them using behavioral finance theory, trains a TF-IDF + Logistic Regression classifier, and serves a professional web dashboard for real-time behavioral sentiment analysis.

**Model Accuracy: 96.67%** across 2,400 balanced headlines.

---

## 📊 Behavioral Classes

| Class | Theory | Pioneer |
|---|---|---|
| **PANIC** | Prospect Theory — loss aversion at scale | Kahneman & Tversky (1979) |
| **FOMO** | Narrative Economics — story-driven buying | Shiller (2019) |
| **HERD** | Financial Instability Hypothesis | Minsky (1986) |
| **LOSS_AVERSION** | Prospect Theory — refusing to realize loss | Kahneman & Tversky (1979) |
| **COGNITIVE_DISSONANCE** | EMH Critique — market ignores bad news | Shiller (2000) |
| **NEUTRAL** | Efficient Market Hypothesis baseline | Fama (1970) |

---

## 🗂️ Project Structure

```
sentiment_stock_anaylzer/
│
├── 01_scrape.py          # Google News RSS scraper
├── 02_label_helper.py    # Manual labeling helper CLI
├── 03_train_model.py     # TF-IDF + Logistic Regression trainer
├── 04_predict.py         # CLI prediction interface
├── 05_charts.py          # Visualization generator
├── auto_label.py         # Rule-based keyword auto-labeler
├── augment_data.py       # Template-based dataset augmentation
├── app.py                # Flask web dashboard (backend + frontend)
│
├── data/
│   ├── raw_headlines.csv         # Scraped raw headlines
│   ├── labelled_headlines.csv    # Labeled training dataset
│   └── metrics.json              # Model evaluation results
│
├── static/               # Frontend CSS/JS assets
├── templates/            # Flask HTML templates
│
├── confusion_matrix.png  # Model evaluation chart
├── top_keywords.png      # Predictive keywords per class
├── phase_timeline.png    # Behavioral phase timeline
├── label_distribution.png # Dataset class distribution
│
└── requirements.txt      # Python dependencies
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Scrape Fresh Headlines
```bash
python 01_scrape.py
```

### 3. Augment & Balance Dataset
```bash
python augment_data.py
```

### 4. Train the Model
```bash
python 03_train_model.py
```

### 5. Launch the Dashboard
```bash
python app.py
```
Then open: **http://localhost:5000**

---

## 📈 Model Performance

| Class | Precision | Recall | F1-Score |
|---|---|---|---|
| COGNITIVE_DISSONANCE | 98.8% | 98.8% | 98.8% |
| FOMO | 96.3% | 98.8% | 97.5% |
| HERD | 97.5% | 98.8% | 98.1% |
| LOSS_AVERSION | 93.7% | 92.5% | 93.1% |
| NEUTRAL | 100.0% | 98.8% | 99.4% |
| PANIC | 93.7% | 92.5% | 93.1% |
| **Overall** | **96.7%** | **96.7%** | **96.7%** |

---

## 🔬 Research Paper

**Title:** *From Fear to Capitulation: A Behavioral Analysis of Investor Sentiment During the 2026 Iran War Period*

**Core Finding:** Investor behavior during the 2026 Iran geopolitical crisis follows a predictable arc (FOMO → HERD → PANIC → LOSS_AVERSION) consistent with the Minsky Cycle, detectable with 96.67% accuracy from financial headline text alone.

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **scikit-learn** — TF-IDF + Logistic Regression pipeline
- **Flask** — Web dashboard backend
- **pandas / numpy** — Data processing
- **matplotlib / seaborn** — Visualizations
- **feedparser** — Google News RSS scraping

---

## 📚 Key References

- Kahneman, D. & Tversky, A. (1979). Prospect Theory. *Econometrica*
- Shiller, R.J. (2019). *Narrative Economics.* Princeton University Press
- Minsky, H. (1986). *Stabilizing an Unstable Economy.* Yale
- Fama, E.F. (1970). Efficient Capital Markets. *Journal of Finance*

---

*Built as part of a behavioral finance research project on investor sentiment during geopolitical crises.*
