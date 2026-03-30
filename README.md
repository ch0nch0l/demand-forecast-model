# Demand Forecasting (LightGBM + TFT) — Developer README

This repository contains a **monthly demand forecasting pipeline** built from a sequence of notebooks:

1. **00 — Data preprocessing & external data integration**
2. **01 — Data cleaning**
3. **02 — Feature engineering (monthly panel + lags/rolling + targets)**
4. **03 — EDA + LightGBM baseline**
5. **04 — Temporal Fusion Transformer (TFT) multi-horizon model (12 months)**
6. **05 — Forecast reconciliation (LightGBM vs TFT) for top series**
7. **06 — Visualization dashboards (top revenue / top volume series)**

The pipeline produces:
- A dense monthly training panel
- A LightGBM baseline (validation/backtest)
- A TFT future forecast (quantiles)
- A reconciliation workbook and CSV outputs focused on **top revenue and top volume series**
- Portfolio + per-series plots for decision-making

---

## 0) Quick Start (TL;DR)

### Prerequisites
- **Python 3.10+** (recommended: 3.10–3.12 for best ecosystem compatibility)
- OS: Windows / macOS / Linux
- Optional: GPU (CUDA) for faster TFT training

### Create environment

```bash
# from repo root
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

python -m pip install --upgrade pip
```

### Install dependencies

```bash
# core pipeline
pip install pandas numpy openpyxl matplotlib seaborn scikit-learn lightgbm

# TFT (PyTorch Forecasting)
pip install torch lightning pytorch-forecasting
```

> If you run on Apple Silicon (M1/M2), install the appropriate PyTorch build from the official PyTorch instructions.

### Copy RAW data in data/raw directory

Before proceeding with the notebooks, make sure you have all yearly ERP data export are copied and placed under the directory

```
data/raw
```
Also place your product groups excel for which you want to forecast the model. A sample product group excel can be found under following directory:

```
data/raw/product_group_sample.xlsx
```
Copy the Excel file and update as per your requirement and save the file naming `product_group.xlsx`. Make sure the file name exactly matches, otherwise the execution will fail. Once done you can move to the next steps.

### Run the notebooks in order

Open Jupyter (or VS Code notebooks) and run:

```bash
jupyter lab
# then execute notebooks 00 → 06 sequentially
```

---

## 1) Repository Layout (expected)

Your folder structure should look like this (minimum):

```
.
├─ notebooks/
│  ├─ 00_data_preprocessing.ipynb
│  ├─ 01_data_cleaning.ipynb
│  ├─ 02_feature_engineering.ipynb
│  ├─ 03_eda_lightgbm_baseline.ipynb
│  ├─ 04_temporal_fusion_transformer.ipynb
│  ├─ 05_forecast_reconciliation.ipynb
│  └─ 06_forecast_visualization_top_series.ipynb
│
├─ scripts/
│  ├─ data_preprocess.py
│  ├─ external.py
│  └─ util.py
│
├─ data/
│  ├─ raw/
│  │  ├─ combined/
│  │  └─ product_groups_sample.xlsx
│  ├─ inputs/                # intermediate Excel outputs from notebook 00
│  ├─ cleaned/               # cleaned CSVs from notebook 01
│  └─ training/              # final training panel from notebook 02
│
├─ outputs/
│  ├─ baseline_lightgbm_forecast_results.csv
│  └─ tft_forecast_12m.csv
│
├─ reconcile_outputs/
│  ├─ reconcile_series_summary_v2.csv
│  ├─ reconcile_top_series_tft_forecasts_v2.csv
│  ├─ reconcile_top_series_lgbm_validation_v2.csv
│  └─ reconcile_top_series_v2.xlsx
│
└─ README.md
```

If your notebooks live at repo root (not under `notebooks/`), keep the same relative `data/`, `outputs/`, and `reconcile_outputs/` folders.

---

## 2) Data Contracts (Inputs/Outputs)

### Required input files

#### ERP Orders (raw)
- `data/raw/combined/erp_order_data.xlsx`
  - Expected sheet: `all_orders`
  - Expected fields (typical): customer/product identifiers, order date, quantities, revenue, unit price, etc.

#### Product filtering list
- `data/raw/ProductGroups.xlsx`

#### External economic indicators (loaded by scripts)
- Notebook 00 calls `scripts/external.py` to load and merge external datasets.

### Key intermediate artifacts

#### 00 — Preprocessing output
- `data/inputs/erp_data_combined.xlsx` (cleaned raw ERP export)
- `data/inputs/external_data_combined.xlsx` (combined external factors export)

#### 01 — Cleaning output (must exist before 02)
- `data/cleaned/erp_cleaned.csv`
- `data/cleaned/external_cleaned.csv`

### Modeling dataset (final)

#### 02 — Feature engineering output
- `data/training/training_data_final.csv`
  - Dense monthly panel per `(customer_id, product_id)` series
  - Contains lags/rolling stats, calendar features, external lags, and optional targets

---

## 3) Notebook-by-Notebook Guide

### Notebook 00 — Data Preprocessing & External Data Integration

**Goal:**
- Load ERP order data from Excel
- Filter to selected product groups
- Handle duplicates and standardize columns
- Load and merge external economic datasets

**Where to look / configure:**
- ERP input path is hard-coded to:
  - `data/raw/combined/erp_order_data.xlsx` (sheet: `all_orders`)
- Product group filter:
  - `data/raw/ProductGroups.xlsx`

**Outputs:**
- ERP export → `data/inputs/erp_data_combined.xlsx`
- External export → `data/inputs/external_data_combined.xlsx`

**Notes:**
- This notebook imports local modules: `scripts/data_preprocess.py`, `scripts/external.py`, `scripts/util.py`.
- Ensure your repo root is on `PYTHONPATH` (running from repo root usually works).

---

### Notebook 01 — Data Cleaning

**Goal:**
- Load ERP and external data from the previous step
- Remove invalid rows (missing keys)
- Create a monthly date index
- Export cleaned datasets for feature engineering

**Typical actions in this notebook:**
- Drop missing key identifiers
- Convert date columns to monthly frequency / month-start

**Outputs (required by Notebook 02):**
- `data/cleaned/erp_cleaned.csv`
- `data/cleaned/external_cleaned.csv`

---

### Notebook 02 — Feature Engineering (Monthly Forecasting Panel)

**Goal:**
- Create a **dense monthly panel** for each time series (customer-product)
- Build time features, internal lags/rolling stats, external lags/rolling stats
- (Optionally) create supervised targets `y_qty` and `y_revenue`

**Key configuration (top of notebook):**
- Input:
  - `ERP_PATH = "data/cleaned/erp_cleaned.csv"`
  - `EXT_PATH = "data/cleaned/external_cleaned.csv"`
- Output:
  - `OUT_PATH = "data/training/training_data_final.csv"`
- Forecasting setup:
  - `FORECAST_HORIZON = 1` (creates next-month target)
  - `CREATE_TARGETS = True` (creates `y_qty`, `y_revenue`)
- Lags/windows:
  - Internal lags: `(1, 2, 3, 6, 12)`
  - Internal rolling windows: `(3, 6, 12)`
  - External lags: `(1, 2, 3)`
  - External rolling windows: `(3, 6)`

**Important implementation notes:**
- Panel is “densified”: missing months become explicit rows with 0 demand.
- Adds observed/missing flags for key measures (helps models handle gaps).

**Output:**
- `data/training/training_data_final.csv`

---

### Notebook 03 — EDA + LightGBM Baseline

**Goal:**
- Establish a fast baseline model for validation/backtesting
- Provide per-series performance signals for reconciliation

**Core design:**
- Adds `time_idx` per series using cumulative month index
- Features: all engineered columns excluding identifiers and target
- Split strategy: last **12 months per series** assigned to validation (if series length > 12)

**Model:**
- `lightgbm.LGBMRegressor` with early stopping

**Outputs (expected):**
- `outputs/baseline_lightgbm_forecast_results.csv`
  - Should include: `Date`, `customer_id`, `product_id`, `forecast_qty`, and (if available) `y_qty`

---

### Notebook 04 — Temporal Fusion Transformer (TFT)

**Goal:**
- Train a **global multi-series** model
- Predict **12 months ahead** (multi-horizon)
- Export quantile forecasts (e.g., q10/q50/q90)

**Key parameters (typical):**
- Target: `ordered_qty`
- Encoder length: 60 months
- Prediction length: 12 months
- Uses `pytorch-forecasting` with `TimeSeriesDataSet` + `TemporalFusionTransformer`

**Outputs (expected):**
- `outputs/tft_forecast_12m.csv`
  - Must contain `Date`, `series_id`, and quantile columns (at least `q10`, `q50`, `q90`)

---

### Notebook 05 — Forecast Reconciliation (Top Series)

**Goal:**
- Compare and reconcile **LightGBM baseline** vs **TFT** forecasts
- Focus only on **Top-N** series by:
  - revenue and/or
  - volume
  computed over the **12 months immediately prior** to the forecast start.

**Configurable values:**
- `TOP_N_REVENUE = 200`
- `TOP_N_QTY = 200`
- Trend detection thresholds:
  - `TREND_PCT_THRESHOLD = 0.10`
  - `TREND_MIN_MEAN = 1e-6`

**Inputs:**
- History: `data/training/training_data_final.csv`
- TFT: `outputs/tft_forecast_12m.csv`
- LightGBM: `outputs/baseline_lightgbm_forecast_results.csv`

**Outputs:**
- `reconcile_outputs/reconcile_series_summary_v2.csv`
- `reconcile_outputs/reconcile_top_series_tft_forecasts_v2.csv`
- `reconcile_outputs/reconcile_top_series_lgbm_validation_v2.csv`
- `reconcile_outputs/reconcile_top_series_v2.xlsx`
  - Sheets: `Series_Summary`, `TFT_Forecast_12M`, `LGBM_Validation`

---

### Notebook 06 — Visualization (Top Revenue / Top Volume Series)

**Goal:**
- Visualize reconciled outputs for stakeholders and planners

**What it produces:**
- Portfolio-level dashboards:
  - trend distribution (stable/increasing/decreasing)
  - monthly totals over top series
  - top contributors
- Per-series deep dives:
  - history + forecast overlay
  - TFT uncertainty bands (`q10`–`q90` and `q50`)
- Baseline error distributions (MAE/WAPE) on top series (if actuals exist)

**Inputs:**
- Always required:
  - `data/training/training_data_final.csv`
  - `outputs/tft_forecast_12m.csv`
  - `outputs/baseline_lightgbm_forecast_results.csv`
- Optional (preferred if present):
  - `reconcile_outputs/*_v2.csv`

---

## 4) Configuration Tips

### Change forecast horizon
- LightGBM baseline is single-step (next month) by default via targets created in notebook 02.
- TFT is **multi-step** (12 months) configured in notebook 04.

If you change the horizon:
- Update notebook 04 `max_prediction_length`
- Ensure you regenerate outputs and rerun reconciliation + visualization

### Top series decision metric
- Current decision metric and visualizations are tuned to **top revenue and top volume series**.
- Adjust `TOP_N_REVENUE` and `TOP_N_QTY` in notebooks 05 and 06.

---
