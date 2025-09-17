from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from atproto_client import Client
from client_wrapper import *
from api_driver import *
from configparser import ConfigParser
import requests

app = Flask(__name__)
CORS(app)
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
        print("inside get_data_from_api")
        response = requests.get('https://api.example.com/data')  # Replace with the actual API URL
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500  # Return error message with 500 status code


@app.route('/skeet/data', methods=['GET'])
def get_skeet_data_from_api():
    try:
        latest = Driver().perform_get_skeets(client)
        data = json.dumps(latest)
        return jsonify(latest)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500  # Return error message with 500 status code

@app.route('/skeet/data/', methods=['GET'])
def get_skeet_data_from_api_withdate():
    from_date = request.args.get('from_date', 'Unknown')
    until_date = request.args.get('until_date', 'Unknown')
    try:
        latest = Driver().perform_get_skeets_from(client, from_date, until_date)
        data = json.dumps(latest)
        return jsonify(latest)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500  # Return error message with 500 status code

@app.route('/skeet/inactive', methods=['GET'])
def get_inactive_skeet_data_from_api():
    try:
        limit = 50
        latest = Driver().perform_get_inactive_skeets(client, limit)
        data = json.dumps(latest)
        return jsonify(latest)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500  # Return error message with 500 status code


@app.route('/skeet/delete/<id>', methods=['DELETE'])
def delete_skeet(id: str):
    try:
        print("Deleting the post at the uri : " + id)
        #Driver().delete_skeet(client, id)
        return jsonify({'message': 'Item deleted'}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500  # Return error message with 500 status code

@app.route('/skeet/nukem/', methods=['GET'])
def delete_skeet_by_nukem():
    # Access parameters from the request body (form-encoded data)
    uri_id = request.args.get('uri_id')
    # Process the parameters
    try:
        limit = 20
        print("Deleting the last : " + str(limit) + " inactive skeets")
        latest = Driver().perform_delete_inactive_skeets(client, limit)
        data = json.dumps(latest)
        return jsonify({'message': 'Item deleted'}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500  # Return error message with 500 status code


@app.route('/skeet/delete/', methods=['GET'])
def delete_skeet_by_get():
    # Access parameters from the request body (form-encoded data)
    uri_id = request.args.get('uri_id')
    # Process the parameters
    try:
        print("Deleting the post at the uri : " + str(uri_id))
        Driver().delete_skeet(client, str(uri_id))
        return jsonify({'message': 'Item deleted'}), 200
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500  # Return error message with 500 status code


if __name__ == '__main__':
    app.run(debug=True)
