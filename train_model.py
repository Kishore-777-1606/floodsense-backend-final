import json
import pandas as pd
from xgboost import XGBRegressor
import joblib

# Load ward data
with open('wards_data.json') as f:
    wards = json.load(f)

training_data = []

# Rainfall samples
rainfalls = [50, 80, 100, 120, 150, 180, 200, 250]

# Generate training data
for rain in rainfalls:

    for ward in wards:

        elevation = ward['elevation']
        water_distance = ward['water_distance']

        # Flood score formula
        score = (
            (rain * 0.5) +
            ((10 - elevation) * 3) +
            ((1 / water_distance) * 10)
        )

        training_data.append([
            rain,
            elevation,
            water_distance,
            score
        ])

# Create dataframe
df = pd.DataFrame(
    training_data,
    columns=[
        'rainfall',
        'elevation',
        'water_distance',
        'score'
    ]
)

# Features
X = df[['rainfall', 'elevation', 'water_distance']]

# Target
y = df['score']

# XGBoost Model
model = XGBRegressor(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=5,
    random_state=42
)

# Train model
model.fit(X, y)

# Save model
joblib.dump(model, 'flood_model.pkl')

print("✅ XGBoost Model Trained Successfully")