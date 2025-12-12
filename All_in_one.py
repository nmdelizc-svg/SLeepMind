import warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)

import joblib
import pandas as pd
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser


# ============================================================
# SPOTIFY CONFIG
# Basic configuration values and keyword mappings
# used for retrieving playlists from the Spotify API.
# ============================================================

CLIENT_ID = "1"
CLIENT_SECRET = "1"

SEARCH_TERMS = {
    "Very_Deficient": "deep sleep healing relaxing",
    "Deficient": "sleep relaxation stress relief",
    "Regular": "soft sleep ambient chill",
    "Acceptable": "relax sleep calm focus",
    "Very_Good": "focus sleep meditation",
    "Excelent": "peaceful sleep meditation zen"
}


# Creates and returns a Spotify client using client credentials.
# If authentication fails, the function returns None.
def create_spotify_client():
    result = None
    client = None
    credentials = None

    try:
        credentials = SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        client = spotipy.Spotify(auth_manager=credentials)
    except Exception:
        client = None

    result = client
    return result


# Searches for playlist recommendations based on the predicted
# sleep category. Returns up to 'limit' playlist results.
def search_playlists_for_category(category_label, limit=3):
    result = []
    playlists = []
    client = None
    query = None
    response = None
    playlist_section = None
    items = None

    client = create_spotify_client()

    if client is not None:
        query = SEARCH_TERMS.get(category_label, "sleep relaxing calm")

        try:
            response = client.search(q=query, type="playlist", limit=limit)
        except Exception:
            response = None

        if response is not None:
            playlist_section = response.get("playlists", {})
            items = playlist_section.get("items", [])

            for item in items:
                if item is not None:
                    if isinstance(item, dict):
                        name = item.get("name")
                        owner = item.get("owner", {})
                        external = item.get("external_urls", {})
                        url = None

                        if name is not None:
                            url = external.get("spotify")

                            if url is not None:
                                playlist = {}
                                playlist["name"] = name
                                playlist["by"] = owner.get("display_name", "Unknown")
                                playlist["url"] = url
                                playlists.append(playlist)

    result = playlists
    return result


# Opens a playlist URL in the default web browser.
def open_playlist(url):
    result = None

    if url is not None:
        webbrowser.open(url)

    return result



# ===================================================================
# SLEEP PREDICTOR + PHI-2 FEEDBACK
# Handles model loading, prediction, and AI-generated feedback.
# ===================================================================

class SleepPredictor:

    def __init__(self, model_path=None, use_phi2=True):

        # Determine where the model is located
        base_dir = Path(__file__).resolve().parent
        default_path = base_dir / "model" / "sleepmind_randomforest_v2.pkl"
        self.model_path = model_path if model_path is not None else default_path

        self.model = None
        self.use_phi2 = use_phi2
        self.phi2_model = None
        self.phi2_tokenizer = None

        # Load the Random Forest classifier
        self._load_model()

        # Human-readable descriptions for each prediction category
        self.category_description = {
            "Very_Deficient": {"label": "Very Deficient", "message": "Critical sleep conditions."},
            "Deficient": {"label": "Deficient", "message": "Your sleep is not enough."},
            "Regular": {"label": "Regular", "message": "Your sleep was okay but could be better."},
            "Acceptable": {"label": "Acceptable", "message": "Good sleep! Could improve slightly."},
            "Very_Good": {"label": "Very Good", "message": "Excellent sleep quality!"},
            "Excelent": {"label": "Excelent", "message": "Perfect sleep schedule!"}
        }

        # Load the Phi-2 language model if enabled
        if self.use_phi2:
            self._load_phi2()

    # Loads the Random Forest sleep prediction model.
    def _load_model(self):
        model = None
        try:
            model = joblib.load(self.model_path)
        except Exception:
            model = None
        self.model = model


    # Loads the Phi-2 language model for feedback generation.
    def _load_phi2(self):
        try:
            model_name = "microsoft/phi-2"
            print(f"\nLoading {model_name}...")

            # Initialize tokenizer
            self.phi2_tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            self.phi2_tokenizer.pad_token = self.phi2_tokenizer.eos_token

            start_time = time.time()

            # Load the model into CPU memory
            self.phi2_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                dtype=torch.float32,
                trust_remote_code=True
            ).to("cpu")

            load_time = time.time() - start_time
            print(f"Phi-2 loaded in {load_time:.1f} seconds")

        except Exception as error:
            print("Warning loading Phi-2:", error)
            self.use_phi2 = False


    # Generates natural language feedback based on user inputs and predictions.
    # The text is cleaned to ensure a readable, professional paragraph.
    def _generate_phi2_feedback(self, user_input, prediction):

        if not self.use_phi2:
            return None

        try:
            # Construct the LLM prompt using the user's data
            prompt = f"""
    You are a sleep-health expert. Analyze the data below and provide evidence-based feedback in 4–5 sentences. Write only a single paragraph. Do not include lists, bullet points, titles, or instructions.

    User Data:
    - Age: {user_input['age']} years
    - Hours slept: {user_input['hours_slept']}
    - Stress level: {user_input['stress_general']}/10
    - Caffeine intake: {user_input['caffeine']}/10
    - Exercise: {user_input['exercise']}/10
    - Screen time: {user_input['screen_time']} hours
    - Predicted sleep quality: {prediction}

    Output:
    """

            # Encode the prompt for the model
            inputs = self.phi2_tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(self.phi2_model.device) for k, v in inputs.items()}

            # Generate a full paragraph response
            generated = self.phi2_model.generate(
                **inputs,
                max_new_tokens=200,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=self.phi2_tokenizer.eos_token_id,
                eos_token_id=self.phi2_tokenizer.eos_token_id
            )

            # Decode into text
            decoded = self.phi2_tokenizer.decode(
                generated[0],
                skip_special_tokens=True
            )

            # Extract only the portion after "Output:"
            if "Output:" in decoded:
                cleaned = decoded.split("Output:", 1)[1].strip()
            else:
                cleaned = decoded.strip()

            # Remove any additional paragraphs
            if "\n\n" in cleaned:
                cleaned = cleaned.split("\n\n")[0].strip()

            # Remove unintended instructions generated by the model
            stop_phrases = [
                "You are an", "You're an",
                "You are a", "You're a",
                "tasked with",
                "Your role",
                "The following",
                "As an",
                "as an",
                "assistant",
                "constraints"
            ]

            for phrase in stop_phrases:
                if phrase in cleaned:
                    cleaned = cleaned.split(phrase)[0].strip()

            cleaned = cleaned.strip()
            return cleaned

        except Exception:
            return None


    # Runs the model prediction and assembles a full prediction report
    # including probability distribution and LLM feedback.
    def predict(self, age, hours_slept, exercise, caffeine, stress, screen_time):

        # Construct a one-row DataFrame for the model input
        df = pd.DataFrame({
            "age": [age],
            "hours_slept": [hours_slept],
            "exercise": [exercise],
            "caffeine": [caffeine],
            "stress_general": [stress],
            "screen_time": [screen_time]
        })

        prediction = self.model.predict(df)[0]
        probabilities = self.model.predict_proba(df)[0]

        prob_dict = {cat: float(prob) for cat, prob in zip(self.model.classes_, probabilities)}

        confidence = float(max(probabilities))
        confidence_text = f"{confidence * 100:.1f}%"

        description = self.category_description.get(
            prediction,
            {"label": prediction, "message": "Unknown"}
        )

        # Generate sleep advice using Phi-2
        feedback = self._generate_phi2_feedback(
            {
                "age": age,
                "hours_slept": hours_slept,
                "exercise": exercise,
                "caffeine": caffeine,
                "stress_general": stress,
                "screen_time": screen_time
            },
            description["label"]
        )

        # Final structured result
        return {
            "success": True,
            "prediction": prediction,
            "probabilities": prob_dict,
            "confidence": confidence,
            "confidence_percent": confidence_text,
            "description": description,
            "phi2_feedback": feedback
        }


# ===================================================================
# SLEEP LENGTH CALCULATOR
# Computes total hours slept based on AM/PM time input.
# ===================================================================

def sleepAmount(results):

    # Helper function to convert AM/PM time into minutes from midnight
    def to_minutes(hour, minute, period):
        hour = int(hour)
        minute = int(minute)

        # Convert AM/PM into 24-hour format
        if period == "AM":
            if hour == 12:
                hour = 0
        else:
            if hour != 12:
                hour += 12

        return hour * 60 + minute

    # Extract sleep and wake data from the results dictionary
    sleepHour = results["sleepHours"]
    sleepMinute = results["sleepMinutes"]
    sleepPeriod = results["sleepPeriod"]

    wakeHour = results["wakeHours"]
    wakeMinute = results["wakeMinutes"]
    wakePeriod = results["wakePeriod"]

    sleepingMinute = to_minutes(sleepHour, sleepMinute, sleepPeriod)
    wakingMinute = to_minutes(wakeHour, wakeMinute, wakePeriod)

    # If the wake time is earlier, assume the sleep passed midnight
    if wakingMinute < sleepingMinute:
        wakingMinute += 24 * 60

    slept_minutes = wakingMinute - sleepingMinute
    slept_hours = round(slept_minutes / 60, 2)

    return slept_hours


# ===================================================================
# COLLECT USER DATA
# Converts raw form inputs into numerical values for prediction.
# ===================================================================

def collect_user_data(results, age):

    data = {
        "age": int(age),
        "hours_slept": float(sleepAmount(results)),
        "exercise": int(results["exerciseLevel"]),
        "caffeine": int(results["caffeineLevel"]),
        "stress_general": int(results["stressLevel"]),
        "screen_time": int(results["screenTime"])
    }

    # Print for debugging purposes
    print(data.items())

    return data


# ===================================================================
# PROGRESS BAR
# Simple animated progress bar for CLI visualization.
# ===================================================================

def progress_bar():
    print("\nCalculando eficiencia del sueño...")

    bar = "■■■■■■■■■■■■■■■■■■■■"
    size = len(bar)
    index = 1

    while index <= size:
        percent = int((index / size) * 100)
        sys.stdout.write(f"\r[{bar[:index]:<20}] {percent}%")
        sys.stdout.flush()
        time.sleep(0.03)
        index += 1

    print("\n")


# ===================================================================
# MAIN EXECUTION
# Orchestrates all steps: data collection, prediction,
# feedback generation, and playlist assignment.
# ===================================================================

def start(results, age):

    print("SLEEP PREDICTOR CON FEEDBACK PERSONALIZADO PHI-2")

    predictor = SleepPredictor(use_phi2=True)
    running = True

    while running:

        # Convert inputs into model-ready values
        user_data = collect_user_data(results, age)

        print("\nAnalizando...")
        progress_bar()

        # Run prediction using Random Forest and Phi-2
        result = predictor.predict(
            user_data["age"],
            user_data["hours_slept"],
            user_data["exercise"],
            user_data["caffeine"],
            user_data["stress_general"],
            user_data["screen_time"]
        )

        # Store results if prediction was successful
        if result["success"]:

            results["sleepEfficiency"] = result["description"]["label"]

            # Sort categories by probability (highest first)
            sorted_probs = sorted(
                result["probabilities"].items(),
                key=lambda x: x[1],
                reverse=True
            )

            feedback = result["phi2_feedback"]
            if feedback is not None:
                results["sleep"] = sleepAmount(results)
                results["recommendation"] = feedback

            # Retrieve Spotify playlist suggestions
            playlists = search_playlists_for_category(result["prediction"])

            if len(playlists) >= 1:
                results["spotifyFirstName"] = f"{playlists[0]['name']}"
                results["spotifyPlayListOne"] = f"{playlists[0]['url']}"

            if len(playlists) >= 2:
                results["spotifySecondName"] = f"{playlists[1]['name']}"
                results["spotifyPlayListTwo"] = f"{playlists[1]['url']}"

            if len(playlists) >= 3:
                results["spotifyThirdName"] = f"{playlists[2]['name']}"
                results["spotifyPlayListThree"] = f"{playlists[2]['url']}"

        running = False

    # Final updated results dictionary
    return results
