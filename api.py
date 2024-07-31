
from flask import Flask, request, jsonify
import subprocess
import os
import json

app = Flask(__name__)

@app.route('/add_url', methods=['POST'])
def add_url():
    data = request.get_json()
    urls = data.get('urls', [])
    if urls:
        with open('my_scraper/urls.txt', 'a') as f:
            for url in urls:
                f.write(url + '\n')
        return jsonify({"message": "URLs added", "urls": urls}), 200
    return jsonify({"message": "No URLs provided"}), 400

@app.route('/list_urls', methods=['GET'])
def list_urls():
    if os.path.exists('my_scraper/urls.txt'):
        with open('my_scraper/urls.txt', 'r') as f:
            urls = f.readlines()
        return jsonify({"urls": [url.strip() for url in urls]}), 200
    return jsonify({"message": "No URLs found"}), 404

@app.route('/clear_urls', methods=['DELETE'])
def clear_urls():
    if os.path.exists('my_scraper/urls.txt'):
        os.remove('my_scraper/urls.txt')
        return jsonify({"message": "All URLs cleared"}), 200
    return jsonify({"message": "No URLs to clear"}), 404

@app.route('/set_proxy', methods=['POST'])
def set_proxy():
    data = request.get_json()
    proxy = data.get('proxy', "")
    if proxy:
        with open('my_scraper/proxy.txt', 'w') as f:
            f.write(proxy)
        return jsonify({"message": "Proxy set", "proxy": proxy}), 200
    return jsonify({"message": "No proxy provided"}), 400

@app.route('/clear_proxy', methods=['DELETE'])
def clear_proxy():
    if os.path.exists('my_scraper/proxy.txt'):
        os.remove('my_scraper/proxy.txt')
        return jsonify({"message": "Proxy cleared"}), 200
    return jsonify({"message": "No proxy to clear"}), 404

@app.route('/run_scraper', methods=['POST'])
def run_scraper():
    if os.path.exists('my_scraper/urls.txt'):
        proxy = None
        if os.path.exists('my_scraper/proxy.txt'):
            with open('my_scraper/proxy.txt', 'r') as f:
                proxy = f.read().strip()
        command = ['python', 'my_scraper/scraper.py']
        if proxy:
            command.append(proxy)
        subprocess.run(command)
        return jsonify({"message": "Scraper executed"}), 200
    return jsonify({"message": "No URLs found. Add URLs before running the scraper."}), 400

@app.route('/report_error', methods=['POST'])
def report_error():
    data = request.get_json()
    error_message = data.get('error_message', '')
    if error_message:
        # Log the error message
        with open('error_log.txt', 'a') as f:
            f.write(error_message + '\n')
        return jsonify({"message": "Error reported", "error_message": error_message}), 200
    return jsonify({"message": "No error message provided"}), 400

@app.route('/request_improvement', methods=['POST'])
def request_improvement():
    data = request.get_json()
    improvement_request = data.get('improvement_request', '')
    if improvement_request:
        # Log the improvement request
        with open('improvement_requests.txt', 'a') as f:
            f.write(improvement_request + '\n')
        return jsonify({"message": "Improvement request submitted", "improvement_request": improvement_request}), 200
    return jsonify({"message": "No improvement request provided"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
