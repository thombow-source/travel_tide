# TravelTide Customer Rewards Program & Segmentation

This repository contains the Data Analytics & Machine Learning pipeline for segmenting TravelTide customers and assigning personalized perk rewards.

## 📁 Repository Structure
- `notebooks/`: Jupyter Notebooks for Data Cleaning, EDA, and Modeling
  - `eda.ipynb`: Exploratory Data Analysis & Feature Scaling
  - `features.ipynb`: Perk Index Construction & Composite Scores
  - `modelling_fuzzy.ipynb`: Rule-Based Fuzzy Rank Segmentation
  - `modelling_ml.ipynb`: Unsupervised Machine Learning (K-Means / PCA)
- `data/`: Aggregated datasets (excluded from Git via .gitignore)

## 🎯 Target Cohort Criteria
Active customers booking since January 4, 2023, with $\ge 4$ sessions and $\ge 1$ booked trip.

## 🛠️ Tech Stack
- Python (Pandas, NumPy, Matplotlib, Seaborn, Scikit-Learn)
- PostgreSQL & Beekeeper Studio