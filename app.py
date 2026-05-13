from flask import Flask, request, jsonify
import json
import random
import joblib

app = Flask(__name__)

# =========================
# LOAD GEOJSON FILE
# =========================
with open("Wards.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# =========================
# LOAD MODEL
# =========================
model = joblib.load("flood_model.pkl")

# =========================
# CREATE WARDS LIST
# =========================
wards = []

# CHECK GEOJSON STRUCTURE
if isinstance(geojson_data, dict) and "features" in geojson_data:

    features = geojson_data["features"]

elif isinstance(geojson_data, list):

    features = geojson_data

else:

    features = []

# =========================
# LOOP THROUGH FEATURES
# =========================
for feature in features:

    # IF properties EXISTS
    if isinstance(feature, dict) and "properties" in feature:

        props = feature["properties"]

    else:

        props = feature

    ward = {

        "ward_no": props.get("Ward_No", 0),

        "zone_no": props.get("Zone_No", "Unknown"),

        "zone_name": props.get("Zone_Name", "Unknown"),

        # TEMP VALUES
        "elevation": round(random.uniform(1, 15), 2),

        "water_distance": round(random.uniform(0.1, 5), 2)
    }

    wards.append(ward)

print(f"Loaded {len(wards)} wards")

# =========================
# RISK LEVEL FUNCTION
# =========================
def get_risk_level(score):

    if score > 120:

        return "HIGH"

    elif score >= 80:

        return "MEDIUM"

    else:

        return "LOW"

# =========================
# REASON FUNCTION
# =========================
def generate_reason(elevation, water_distance):

    if elevation < 4 and water_distance < 0.5:

        return "Low elevation and very close to water"

    elif elevation < 5:

        return "Low elevation increases flood risk"

    elif water_distance < 0.5:

        return "Close to water body increases risk"

    else:

        return "Moderate conditions"

# =========================
# HOME ROUTE
# =========================
@app.route("/")
def home():

    return """
    <h1>Flood Risk API Running 🚀</h1>

    <p>Click below:</p>

    <a href="/get-risk?rainfall=250">
        Check Flood Risk
    </a>
    """

# =========================
# MAIN API
# =========================
@app.route("/get-risk", methods=["GET"])
def get_risk():

    rainfall = request.args.get("rainfall")

    # CHECK INPUT
    if rainfall is None:

        return jsonify({
            "error": "Rainfall required"
        }), 400

    # CONVERT TO FLOAT
    try:

        rainfall = float(rainfall)

    except:

        return jsonify({
            "error": "Invalid rainfall"
        }), 400

    result = []

    # =========================
    # LOOP THROUGH ALL WARDS
    # =========================
    for ward in wards:

        elevation = ward["elevation"]

        water_distance = ward["water_distance"]

        # =========================
        # MODEL PREDICTION
        # =========================
        score = model.predict([
            [rainfall, elevation, water_distance]
        ])[0]

        score = float(round(score, 2))

        # GET LEVEL
        level = get_risk_level(score)

        # GET REASON
        reason = generate_reason(
            elevation,
            water_distance
        )

        # FINAL RESULT
        result.append({

            "ward_no": ward["ward_no"],

            "zone_no": ward["zone_no"],

            "zone_name": ward["zone_name"],

            "score": score,

            "level": level,

            "elevation": elevation,

            "water_distance": water_distance,

            "rainfall": rainfall,

            "reason": reason
        })

    # =========================
    # SORT BY HIGH RISK
    # =========================
    result = sorted(
        result,
        key=lambda x: x["score"],
        reverse=True
    )

    # =========================
    # RETURN JSON
    # =========================
    return jsonify({

        "total_wards": len(result),

        "data": result
    })

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
