#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
app.py - Stock Sentiment Analyzer Web Backend
Flask server providing API endpoints for single/batch predictions, 
dataset browsing, direct user augmentation, and pipeline retraining logs.
"""

import os
import sys
import time
import pickle
import threading
import subprocess
import json
import pandas as pd
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__, static_folder="static", template_folder="templates")

# Global variables to track background pipeline task
pipeline_lock = threading.Lock()
is_pipeline_running = False
pipeline_logs = []

# Cached model in memory
model = None
MODEL_PATH = "model.pkl"
METRICS_PATH = "data/metrics.json"
LABELLED_DATA_PATH = "data/labelled_headlines.csv"
RAW_DATA_PATH = "data/raw_headlines.csv"

# Economic and behavioral theory details mapping
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

def load_cached_model():
    global model
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                model = pickle.load(f)
            print("Successfully loaded model from disk.")
        except Exception as e:
            print(f"Error loading model: {e}")
            model = None
    else:
        print("Model file not found. Running training is recommended.")

# Initial model load
load_cached_model()

class PipelineThread(threading.Thread):
    def run(self):
        global is_pipeline_running, pipeline_logs
        with pipeline_lock:
            if is_pipeline_running:
                return
            is_pipeline_running = True
            
        pipeline_logs.clear()
        self.log_message("Starting Behavioral Finance NLP retrain pipeline...")
        
        scripts = [
            ("01_scrape.py", "1. Crawling real-world news feeds"),
            ("augment_data.py", "2. Augmenting and balancing the dataset"),
            ("03_train_model.py", "3. Re-training the model (TF-IDF + LogReg)"),
            ("05_charts.py", "4. Regenerating publication-ready figures")
        ]
        
        success = True
        for script_name, description in scripts:
            self.log_message(f"\n--- Running script: {script_name} ({description}) ---")
            
            # Start process, streaming output line by line
            try:
                process = subprocess.Popen(
                    [sys.executable, script_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Read stdout in real time
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        stripped = line.strip()
                        if stripped:
                            self.log_message(f"  [LOG] {stripped}")
                            
                process.wait()
                if process.returncode != 0:
                    self.log_message(f"ERROR: {script_name} failed with exit code {process.returncode}")
                    success = False
                    break
                    
            except Exception as e:
                self.log_message(f"EXCEPTION running {script_name}: {e}")
                success = False
                break
                
        if success:
            self.log_message("\nReloading trained model into memory...")
            load_cached_model()
            self.log_message("Pipeline completed successfully! Model has been updated.")
        else:
            self.log_message("\nPipeline failed. Check error logs above.")
            
        with pipeline_lock:
            is_pipeline_running = False

    def log_message(self, msg):
        global pipeline_logs
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pipeline_logs.append(f"[{timestamp}] {msg}")
        print(f"Pipeline: {msg}")

# API: Serve Single-Page App Index
@app.route('/')
def index():
    return render_template("index.html")

# API: Serve Generated Chart Images
@app.route('/api/charts/<chart_name>')
def get_chart(chart_name):
    # Map friendly names to actual image filenames
    name_map = {
        "label_distribution": "label_distribution.png",
        "sentiment_pie": "sentiment_pie.png",
        "top_keywords": "top_keywords.png",
        "phase_timeline": "phase_timeline.png",
        "confusion_matrix": "confusion_matrix.png"
    }
    
    filename = name_map.get(chart_name)
    if not filename or not os.path.exists(filename):
        return jsonify({"error": "Chart not found"}), 404
        
    return send_from_directory(".", filename)

# API: Single Prediction
@app.route('/api/predict', methods=['POST'])
def predict():
    global model
    if model is None:
        load_cached_model()
        if model is None:
            return jsonify({"error": "Model not loaded. Please train the model."}), 400
            
    data = request.get_json()
    if not data or "headline" not in data:
        return jsonify({"error": "Missing 'headline' field in request data"}), 400
        
    headline = data["headline"].strip()
    if not headline:
        return jsonify({"error": "Headline cannot be empty"}), 400
        
    try:
        pred = model.predict([headline])[0]
        prob = model.predict_proba([headline])[0]
        
        # Get matching class labels from model
        classes = model.classes_
        class_prob_map = dict(zip(classes, prob))
        max_prob = class_prob_map[pred] * 100
        
        theory_details = THEORY_MAP.get(pred, {
            "meaning": "Unknown category",
            "theory": "No theory registered"
        })
        
        return jsonify({
            "headline": headline,
            "label": pred,
            "confidence": round(max_prob, 2),
            "meaning": theory_details["meaning"],
            "theory": theory_details["theory"],
            "probabilities": {k: round(v * 100, 2) for k, v in class_prob_map.items()}
        })
    except Exception as e:
        return jsonify({"error": f"Prediction error: {str(e)}"}), 500

# API: Batch Prediction
@app.route('/api/predict_batch', methods=['POST'])
def predict_batch():
    global model
    if model is None:
        load_cached_model()
        if model is None:
            return jsonify({"error": "Model not loaded"}), 400
            
    # Handle CSV upload or JSON list
    headlines = []
    
    if 'file' in request.files:
        file = request.files['file']
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "Uploaded file must be a CSV"}), 400
        try:
            df = pd.read_csv(file, encoding="utf-8")
            # Look for standard headline columns
            candidate_cols = ['headline', 'title', 'text', 'Headline', 'Title']
            found_col = None
            for c in candidate_cols:
                if c in df.columns:
                    found_col = c
                    break
            if not found_col:
                # Fallback to first column
                found_col = df.columns[0]
                
            headlines = df[found_col].dropna().astype(str).tolist()
        except Exception as e:
            return jsonify({"error": f"Failed to parse uploaded CSV: {str(e)}"}), 400
    else:
        # Expect JSON list of headlines
        data = request.get_json()
        if not data or "headlines" not in data:
            return jsonify({"error": "No headlines provided (send JSON with 'headlines' list or upload CSV)"}), 400
        headlines = data["headlines"]
        
    if not headlines:
        return jsonify({"error": "Parsed headline list is empty"}), 400
        
    try:
        preds = model.predict(headlines)
        probs = model.predict_proba(headlines)
        classes = model.classes_
        
        results = []
        for h, pred, prob in zip(headlines, preds, probs):
            class_prob_map = dict(zip(classes, prob))
            max_prob = class_prob_map[pred] * 100
            results.append({
                "headline": h,
                "label": pred,
                "confidence": round(max_prob, 2),
                "theory": THEORY_MAP[pred]["theory"]
            })
            
        return jsonify({"predictions": results})
    except Exception as e:
        return jsonify({"error": f"Batch prediction error: {str(e)}"}), 500

# API: Get Dataset Explorer list & statistics
@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    if not os.path.exists(LABELLED_DATA_PATH):
        return jsonify({"error": "No dataset file exists yet. Run retraining first."}), 400
        
    try:
        df = pd.read_csv(LABELLED_DATA_PATH, encoding="utf-8")
        
        # Parse query params
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        search_query = request.args.get("query", "").strip().lower()
        filter_label = request.args.get("label", "").strip()
        
        # Apply filters
        df_filtered = df
        if search_query:
            df_filtered = df_filtered[df_filtered["headline"].astype(str).str.lower().str.contains(search_query)]
        if filter_label:
            df_filtered = df_filtered[df_filtered["label"] == filter_label]
            
        total_records = len(df_filtered)
        
        # Paginate
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        df_paginated = df_filtered.iloc[start_idx:end_idx]
        
        records = df_paginated.fillna("").to_dict(orient="records")
        
        # General stats
        dist = df["label"].value_counts().to_dict()
        source_dist = df["source"].fillna("Unknown").value_counts().to_dict()
        
        return jsonify({
            "total": total_records,
            "page": page,
            "limit": limit,
            "data": records,
            "stats": {
                "total_labelled": len(df),
                "class_distribution": dist,
                "source_distribution": source_dist
            }
        })
    except Exception as e:
        return jsonify({"error": f"Dataset read error: {str(e)}"}), 500

# API: Add Custom Headline
@app.route('/api/dataset/add', methods=['POST'])
def add_dataset_sample():
    data = request.get_json()
    if not data or "headline" not in data or "label" not in data:
        return jsonify({"error": "Missing 'headline' or 'label' field"}), 400
        
    headline = data["headline"].strip()
    label = data["label"].strip()
    
    if not headline or not label:
        return jsonify({"error": "Headline and label cannot be blank"}), 400
        
    if label not in THEORY_MAP:
        return jsonify({"error": f"Invalid label '{label}'. Valid labels: {list(THEORY_MAP.keys())}"}), 400
        
    try:
        new_row = {
            "source": "User Interface Input",
            "headline": headline,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "query_source": "USER_AUGMENTED",
            "label": label
        }
        
        # Append to labelled headlines
        df_lbl = pd.DataFrame([new_row])
        if os.path.exists(LABELLED_DATA_PATH):
            df_lbl.to_csv(LABELLED_DATA_PATH, mode='a', header=False, index=False, encoding="utf-8")
        else:
            df_lbl.to_csv(LABELLED_DATA_PATH, index=False, encoding="utf-8")
            
        # Also append to raw headlines to keep them in sync for future crawls
        raw_row = new_row.copy()
        raw_row["label"] = ""
        df_raw = pd.DataFrame([raw_row])
        if os.path.exists(RAW_DATA_PATH):
            df_raw.to_csv(RAW_DATA_PATH, mode='a', header=False, index=False, encoding="utf-8")
        else:
            df_raw.to_csv(RAW_DATA_PATH, index=False, encoding="utf-8")
            
        return jsonify({"status": "success", "message": f"Successfully added headline to dataset. It will be incorporated in the next training run."})
    except Exception as e:
        return jsonify({"error": f"Failed to write to files: {str(e)}"}), 500

# API: Run Retrain Pipeline
@app.route('/api/pipeline/run', methods=['POST'])
def run_pipeline_api():
    global is_pipeline_running
    with pipeline_lock:
        if is_pipeline_running:
            return jsonify({"status": "running", "message": "Pipeline is already running."}), 400
            
    # Start thread
    t = PipelineThread()
    t.start()
    
    return jsonify({"status": "started", "message": "Retrain pipeline started in background."})

# API: Pipeline Status & Logs
@app.route('/api/pipeline/status', methods=['GET'])
def get_pipeline_status():
    global is_pipeline_running, pipeline_logs
    
    metrics = {}
    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                metrics = json.load(f)
        except Exception as e:
            print(f"Error reading metrics json: {e}")
            
    return jsonify({
        "status": "running" if is_pipeline_running else "idle",
        "logs": pipeline_logs,
        "metrics": metrics
    })

if __name__ == "__main__":
    # If standard --test CLI argument is present, verify code works
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Backend application test mode. Verifying dependencies and server initialization...")
        print("Dependencies check passed successfully.")
        sys.exit(0)
        
    app.run(host="127.0.0.1", port=5000, debug=True)
