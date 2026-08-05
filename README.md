# ZYNAPSE

AI-powered Fashion Product Demand Prediction & Recommendation System

## How to Run

1. Install MongoDB.
2. Download the Kaggle dataset.
3. Put all images inside:

static/images/

4. Run:

python scripts/migrate_to_mongo.py

5. Start the project:

python -m uvicorn main:app --reload