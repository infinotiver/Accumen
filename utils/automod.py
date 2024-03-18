import requests
import os
import json
def text_moderation(text):
  url = "https://text-moderator.p.rapidapi.com/api/v1/moderate"
  payload = {"input": text}

  headers = {
      "content-type": "application/json",
      "X-RapidAPI-Key": os.environ["rapidapi"],
      "X-RapidAPI-Host": "text-moderator.p.rapidapi.com"
  }

  response = requests.post(url, json=payload, headers=headers)

  try:
      data = response.json()
      print(data)
      # Define thresholds 
      thresholds = {
          "toxic": 0.1,
          "indecent": 0.2,
          "threat": 0.05,
          "offensive": 0.1,
          "erotic": 0.05,
          "spam": 0.7  # Higher threshold for spam to avoid false positives
      }

      # Check if any score exceeds the corresponding threshold
      for category, score in data.items():
          if score > thresholds[category]:
              return True, f"Message flagged for {category.capitalize()}. Score: {score:.4f}"

      # No flags raised
      return False, ""

  except (KeyError, json.JSONDecodeError) as e:
      # Handle potential errors in the API response
      print(f"Error processing moderation response: {e}")
      return False, ""
