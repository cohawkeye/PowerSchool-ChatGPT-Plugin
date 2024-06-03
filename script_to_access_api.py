import requests
from flask import Flask, jsonify
import os
import base64
import json

# Initialize Flask app
#Generate your own secret if you choose.  
app = Flask(__name__)
app.secret_key = "{Secret}"

# PowerSchool API Configuration
# Adjust {data} to what is collected from Plugin Configuration>Plugin>Data Provider Configuration
PS_API_URL = "{PowerSchoolURL}"
client_id = "{client_id}"
client_secret = "{client_secret}"


def get_bearer_token(client_id, client_secret):
    url = f"{PS_API_URL}/oauth/access_token"
    credentials = base64.b64encode(
        f"{client_id}:{client_secret}".encode("utf-8")
    ).decode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Authorization": f"Basic {credentials}",
    }
    payload = "grant_type=client_credentials"

    app.logger.debug(f"Requesting token from URL: {url}")
    response = requests.post(url, headers=headers, data=payload)

    app.logger.debug(f"Response status code: {response.status_code}")
    app.logger.debug(f"Response content: {response.text}")

    if response.status_code == 200:
        try:
            return response.json().get("access_token")
        except ValueError:
            app.logger.error("Response content is not valid JSON")
            raise Exception("Response content is not valid JSON")
    else:
        app.logger.error(
            f"Failed to retrieve bearer token: {response.status_code} {response.text}"
        )
        raise Exception(
            f"Failed to retrieve bearer token: {response.status_code} {response.text}"
        )

#This function can probably go but it's a method to retrieve one building.  
def get_school_data(school_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    url = f"{PS_API_URL}/ws/v1/school/{school_id}"

    app.logger.debug(f"Requesting school data from URL: {url}")
    response = requests.get(url, headers=headers)

    app.logger.debug(f"Response status code: {response.status_code}")
    app.logger.debug(f"Response content: {response.text}")

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            app.logger.error(f"Non-JSON response: {response.text}")
            return None
    else:
        app.logger.error(
            f"Error fetching school data: {response.status_code} {response.text}"
        )
        return None


@app.route("/all-data", methods=["GET"])
def all_data():
    try:
        access_token = get_bearer_token(client_id, client_secret)
        all_schools_data = []

        # Assuming school IDs range from 1 to 100
        # Not a fan of this loop, just haven't figured out a way to return all data yet.  
        for school_id in range(1, 101):
            school_data = get_school_data(school_id, access_token)
            if school_data:
                all_schools_data.append(school_data)

        return jsonify({"schools": all_schools_data})
    except Exception as e:
        app.logger.error(f"Error in /all-data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/get-token", methods=["GET"])
def get_token():
    try:
        token = get_bearer_token(client_id, client_secret)
        return jsonify({"access_token": token})
    except Exception as e:
        app.logger.error(f"Error in /get-token: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/test", methods=["GET"])
def test_api():
    return jsonify({"message": "API is working!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
