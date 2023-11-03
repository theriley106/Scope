from flask import Flask, request, render_template, jsonify, redirect
import json
import time
import random

app = Flask(__name__, static_url_path='/static/')
images = ["dropbox.png", "google.png", "gmail.png"]

def generate_response():
    return {"image": "/static/" + random.choice(images), "content": f"Fake response generated at {str(time.time())}"}


@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    data = request.get_json()
    search_term = data.get('term', '')
    print(search_term)
    
    random_results = [generate_response() for i in range(10)]
    
    return jsonify({"results": random_results})

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)