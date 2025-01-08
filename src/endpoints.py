from flask import Flask, jsonify
import os
from atproto_client import Client
from client_wrapper import *
from api_driver import *
from configparser import ConfigParser
import requests

app = Flask(__name__)
config = ConfigParser()
script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "..//settings.ini")
config.read(config_file_path)
account = config.get('main-section', 'account')
token = config.get('main-section', 'api_token')
client_wrapper = ClientWrapper(account, token)
client = client_wrapper.init_client()


@app.route('/api/data', methods=['GET'])
def get_data_from_api():
    try:
        response = requests.get('https://api.example.com/data') # Replace with the actual API URL
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500 # Return error message with 500 status code

@app.route('/skeet/data', methods=['GET'])
def get_skeet_data_from_api():
    try:
        latest = Driver().perform_get_skeets(client)
        data = json.dumps(latest)
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500 # Return error message with 500 status code

@app.route('/skeet/<string:uri_id>', methods=['DELETE'])
def skeet(uri_id):
    try:
        Driver().delete_skeet(client, uri_id)
        return jsonify({'message': 'Item deleted'}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500 # Return error message with 500 status code

if __name__ == '__main__':
    app.run(debug=True)
