# 🏦 Credit Portfolio Governance Engine

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📌 Executive Summary
This repository contains a **2nd Line of Defense (LOD2) Quantitative Risk System** designed for Wholesale/Investment Banking portfolios. It demonstrates full-stack capabilities combining data engineering, quantitative risk monitoring, and interactive visualization. 

Created for **Portfolio Risk Officer** and **Credit Quant** roles to oversee Legal Lending Limits (LLL), Large Regulatory Exposures, and Early Warning Triggers.

## 🏗️ Architecture & Modules
- **`src/db_generator.py`**: ETL simulation engine building a relational SQLite DB representing 500 institutional obligors, facilities, and 24-months stochastic exposure histories.
- **`src/portfolio_limits_monitor.py`**: OOP-based limit monitoring engine computing `Total Exposure = Drawn + MtM + PFE`. Monitors facilities breaching approved LLL and calculates Large Exposures against a simulated $10B Tier-1 Capital baseline.
- **`src/credit_triggers_backtest.py`**: Time-series backtester isolating systemic anomalies (e.g., simultaneous rating downgrades to High Yield with facility utilization > 85%).
- **`app.py`**: Interactive **Streamlit** dashboard with Plotly for dynamic reporting, limit breach investigations, and watchlist monitoring.
