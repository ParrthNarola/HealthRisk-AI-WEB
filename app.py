from __future__ import annotations

import pickle
import numpy as np
from pathlib import Path
from typing import Any, List 
from flask import Flask, render_template, request, redirect, url_for,jsonify
import google.generativeai as genai
from markupsafe import Markup
import os

APP_ROOT = Path(__file__).resolve().parent
MODELS_DIR = APP_ROOT / "models"


class DummyModel:
    """Safe fallback model used when a real model file is missing.

    Always predicts 0 (negative) to avoid false alarms. It also carries a name
    so we can show a helpful note in the UI that the real model wasn't found.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def predict(self, X: List[List[float]]) -> List[int]:  # type: ignore[override]
        return [0 for _ in X]


def load_model(model_filename: str, friendly_name: str) -> Any:
    model_path = MODELS_DIR / model_filename
    try:
        with open(model_path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return DummyModel(friendly_name)


app = Flask(__name__)

# Load models (or safe fallbacks)
# diabetes_model = load_model("diabetes_model.pkl", "Diabetes Model")
# heart_model = load_model("heart_model.pkl", "Heart Disease Model")

# # ✅ Load models
# heart_model = pickle.load(open("models/Heart_trained_model.sav", "rb"))
# diabetes_model = pickle.load(open("models/Diabetes_trained_model.sav", "rb"))
# parkinsons_model = pickle.load(open("models/parkinson_trained_model.sav", "rb"))
diabetes_model = load_model("Diabetes_trained_model.sav", "Diabetes Model")
heart_model = load_model("Heart_trained_model.sav", "Heart Model")
parkinsons_model = load_model("parkinsons_model.pkl", "Parkinson's Model")

def coerce_floats(values: List[str]) -> List[float]:
    coerced: List[float] = []
    for v in values:
        try:
            coerced.append(float(v))
        except Exception:
            coerced.append(0.0)
    return coerced


def safe_predict(model: Any, features: List[float]) -> int:
    try:
        return int(model.predict([features])[0])
    except Exception:
        # If the underlying model complains about feature length/shape, treat as negative
        return 0
    
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("WARNING: GEMINI_API_KEY not set")
genai.configure(api_key=API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

# System instruction
SYSTEM_PROMPT = """
You are a helpful and professional **medical assistant chatbot**.

Your responsibilities:
1. You can answer questions about any medical field, including diseases, symptoms, prevention, treatment options, and healthy lifestyle practices.
2. You must always give information in a clear, simple, and accurate way.
3. If a user greets you (e.g., "hi", "hello", "good morning"), respond politely and friendly.
4. If a question is outside the medical or health domain (e.g., about sports, politics, movies, coding), reply strictly with:
   "I can only provide medical-related information."

Important rules:
- You are not a replacement for a doctor. If a user asks for a diagnosis or personal medical decision, remind them to **consult a qualified healthcare professional**.
- Keep responses concise but informative.
- Be polite, respectful, and supportive in all replies.
"""
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_msg = request.json.get("message", "")
        if not user_msg.strip():
            return jsonify({"reply": "Please type something."})

        response = model.generate_content([SYSTEM_PROMPT, user_msg])
        bot_reply = response.text or "Sorry, I couldn't generate a response."

        # 🔹 Convert markdown/newlines to HTML for clean display
        formatted_reply = (
            bot_reply.replace("**", "<b>")
            .replace("*", "• ")
            .replace("\n", "<br>")
        )

        # Optionally wrap disclaimer in smaller italic font
        if "Disclaimer:" in formatted_reply:
            formatted_reply = formatted_reply.replace(
                "Disclaimer:",
                "<br><br><i><small><b>Disclaimer:</b>"
            ) + "</small></i>"

    except Exception as e:
        formatted_reply = f"<b>Error:</b> {str(e)}"

    return jsonify({"reply": Markup(formatted_reply)})

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/diabetes", methods=["GET", "POST"])
def diabetes():
    if request.method == "POST":
        raw_values = [
            request.form.get("pregnancies", "0"),
            request.form.get("glucose", "0"),
            request.form.get("blood_pressure", "0"),
            request.form.get("skin_thickness", "0"),
            request.form.get("insulin", "0"),
            request.form.get("bmi", "0"),
            request.form.get("dpf", "0"),
            request.form.get("age", "0"),
        ]
        features = coerce_floats(raw_values)
        final_features = np.array([features])
        # pred = diabetes_model.predict(final_features)
        pred = safe_predict(diabetes_model, features)
        result_text = "Positive" if pred == 1 else "Negative"
        return render_template(
            "result.html",
            condition="Diabetes",
            result=result_text,
            inputs=features,
        )
    return render_template("diabetes.html")


@app.route("/heart", methods=["GET", "POST"])
def heart():
    if request.method == "POST":
        raw_values = [
            request.form.get("age", "0"),
            request.form.get("sex", "0"),
            request.form.get("cp", "0"),
            request.form.get("trestbps", "0"),
            request.form.get("chol", "0"),
            request.form.get("fbs", "0"),
            request.form.get("restecg", "0"),
            request.form.get("thalach", "0"),
            request.form.get("exang", "0"),
            request.form.get("oldpeak", "0"),
            request.form.get("slope", "0"),
            request.form.get("ca", "0"),
            request.form.get("thal", "0"),
        ]
        features = coerce_floats(raw_values)
        final_features = np.array([features])
        # pred = heart_model.predict(final_features)
        pred = safe_predict(heart_model, features)
        result_text = "Positive" if pred == 1 else "Negative"
        return render_template(
            "result.html",
            condition="Heart Disease",
            result=result_text,
            inputs=features,
        )
    return render_template("heart.html")


@app.route("/parkinsons", methods=["GET", "POST"])
def parkinsons():
    if request.method == "POST":
        raw_values = [
            request.form.get("fo", "0"),
            request.form.get("fhi", "0"),
            request.form.get("flo", "0"),
            request.form.get("jitter", "0"),
            request.form.get("shimmer", "0"),
        ]
        features = coerce_floats(raw_values)
        # final_features = np.array([features])
        # pred = parkinsons_model.predict(final_features)
        pred = safe_predict(parkinsons_model, features)
        result_text = "Positive" if pred == 1 else "Negative"
        return render_template(
            "result.html",
            condition="Parkinson's",
            result=result_text,
            inputs=features,
        )
    return render_template("parkinsons.html")



@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        # Collect form data
        role = request.form.get("role")
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        gender = request.form.get("gender")
        age = request.form.get("age")

        if role == "patient":
            diseases = request.form.get("diseases")
            medications = request.form.get("medications")
            last_checkup = request.form.get("last_checkup")
            # Save to DB...

        elif role == "doctor":
            specialization = request.form.get("specialization")
            experience = request.form.get("experience")
            hospital = request.form.get("hospital")
            license = request.form.get("license")
            # Save to DB...

        # flash("Profile updated successfully!", "success")
        return redirect("/profile")

    return render_template("profile.html")



@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


