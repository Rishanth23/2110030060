from flask import Flask, jsonify, request
import requests
from collections import deque
from statistics import mean
import time
import logging

app = Flask(__name__)

WINDOW_SIZE = 10
NUMBER_SOURCES = {
    'p': 'http://20.244.56.144/test/primes',
    'f': 'http://20.244.56.144/test/fibo',
    'e': 'http://20.244.56.144/test/even',
    'r': 'http://20.244.56.144/test/rand'
}

window = deque(maxlen=WINDOW_SIZE)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Authorization token (replace with your actual token)
AUTH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzE4ODYzODc0LCJpYXQiOjE3MTg4NjM1NzQsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6IjNmOGM0YWZmLTlmN2ItNDk3ZC1hMDZhLTc5OGIzZjgyYWYyMiIsInN1YiI6IjIxMTAwMzAwNjBAa2xoLmVkdS5pbiJ9LCJjb21wYW55TmFtZSI6ImdvTWFydCIsImNsaWVudElEIjoiM2Y4YzRhZmYtOWY3Yi00OTdkLWEwNmEtNzk4YjNmODJhZjIyIiwiY2xpZW50U2VjcmV0IjoiWUpYTnVic3BpTlNVWVBLZyIsIm93bmVyTmFtZSI6IlJpc2hhbnRoIiwib3duZXJFbWFpbCI6IjIxMTAwMzAwNjBAa2xoLmVkdS5pbiIsInJvbGxObyI6IjIxMTAwMzAwNjAifQ.yZAkuzy2rarhrsWAzlQDocxK5YFG4WcAYviHwia-srI'


@app.route('/numbers/<numberid>', methods=['POST'])
def get_numbers(numberid):
    if numberid not in NUMBER_SOURCES:
        return jsonify({"error": "Invalid number ID"}), 400

    url = NUMBER_SOURCES[numberid]
    headers = {'Authorization': f'Bearer {AUTH_TOKEN}'}
    start_time = time.time()

    try:
        logging.debug(f"Fetching numbers from {url}")
        response = requests.get(url, headers=headers,
                                timeout=5)  # Include headers and increase timeout to 5 seconds for testing
        response_time = time.time() - start_time

        if response.status_code != 200:
            logging.error(f"Invalid response: {response.status_code}")
            return jsonify({"error": f"Invalid response: {response.status_code}"}), 500

        if response_time >= 5:
            logging.error("Response timeout")
            return jsonify({"error": "Response timeout"}), 500

        numbers = response.json().get('numbers', [])

        # Ensure uniqueness of the numbers
        unique_numbers = list(set(numbers))

        # Capture the previous state of the window
        window_prev_state = list(window)

        # Update the window with new unique numbers, maintaining the window size
        for number in unique_numbers:
            if len(window) == WINDOW_SIZE:
                window.popleft()
            window.append(number)

        # Capture the current state of the window
        window_curr_state = list(window)

        # Calculate the average
        if window_curr_state:
            avg = mean(window_curr_state)
        else:
            avg = 0

        return jsonify({
            "numbers": unique_numbers,
            "windowPrevState": window_prev_state,
            "windowCurrState": window_curr_state,
            "avg": round(avg, 2)
        })

    except requests.RequestException as e:
        logging.error(f"Request exception: {e}")
        return jsonify({"error": "Failed to fetch numbers or response timeout"}), 500
    except ValueError as e:
        logging.error(f"Value error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=9876, debug=True)
