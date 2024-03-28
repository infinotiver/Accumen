import requests
import os
import json


def text_moderation(text):
    url = "https://text-moderator.p.rapidapi.com/api/v1/moderate"
    payload = {"input": text}

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": os.environ["rapidapi"],
        "X-RapidAPI-Host": "text-moderator.p.rapidapi.com",
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        data = response.json()
        # Define thresholds
        thresholds = {
            "toxic": 0.95,
            "threat": 0.8,
            "offensive": 0.95,
            "erotic": 0.5,
            "indecent": 1,  # Practically impossible
            "spam": 0.95,  # Higher threshold for spam to avoid false positives
        }

        # Check if any score exceeds the corresponding threshold
        for category, score in data.items():
            if score > thresholds[category]:
                confidence = score * 100
                return (
                    True,
                    f"Message flagged for **{category.capitalize()}**. Confidence: **{confidence:.4f}**",
                )

        # No flags raised
        return False, ""

    except (KeyError, json.JSONDecodeError) as e:
        # Handle potential errors in the API response
        print(f"Error processing moderation response: {e}")
        return False, ""
