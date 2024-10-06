"""
This module contains the GoogleAPI class, which interacts with the
Google Geolocation API to retrieve latitude and longitude coordinates.
"""

import os
import requests
from dotenv import load_dotenv


load_dotenv()


class GoogleAPI:
    """
    A class that interacts with the Google Geolocation API to retrieve
    latitude and longitude coordinates.

    Attributes:
        key (str): The API key used for authentication.
        url (str): The URL endpoint for the Geolocation API.

    Methods:
        geolocate() -> dict:
            Sends a POST request to the Geolocation API and returns the latitude
            and longitude coordinates if the request is successful. Otherwise,
            returns an error message.

    """

    def __init__(self):
        self.key = os.getenv('GOOGLE_API_KEY')
        self.url = f'https://www.googleapis.com/geolocation/v1/geolocate?key={
            self.key}'

    def geolocate(self) -> dict:
        """
        Geolocates the user's IP address using the Google Maps Geolocation API.

        Returns:
            dict: A dictionary containing the latitude and longitude of the user's
            location if successful, or an error message if the request fails.
        """

        data = {
            "considerIp": "true"
        }

        try:
            response = requests.post(self.url, json=data, timeout=10)
        except requests.exceptions.RequestException as e:
            return {"error": "Request failed", "message": str(e)}

        if response.status_code == 200:
            response_data = response.json()

            latitude = response_data.get('location', {}).get('lat')
            longitude = response_data.get('location', {}).get('lng')

            return {
                "latitude": latitude,
                "longitude": longitude
            }
        return {"error": response.status_code, "message": response.text}
