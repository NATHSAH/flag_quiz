from flask import Flask, render_template, jsonify, request
import requests
import random

app = Flask(__name__)
app.secret_key = "dynamic_flag_master_key"

ALL_COUNTRIES = []

def load_countries():
    global ALL_COUNTRIES
    # We now fetch "region" so we can filter by continent
    url = "https://restcountries.com/v3.1/all?fields=name,flags,region"
    try:
        print("Fetching countries from the API, please wait...")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        ALL_COUNTRIES = [
            {"name": c['name']['common'], "flag": c['flags']['png'], "region": c['region']} 
            for c in response.json()
        ]
        print(f"Successfully loaded {len(ALL_COUNTRIES)} countries.")
    except Exception as e:
        print(f"API Error or timeout: {e}")
        print("Using fallback countries dataset.")
        # Fallback dataset so the app doesn't crash when getting a question
        ALL_COUNTRIES = [
            {"name": "United States", "flag": "https://flagcdn.com/w320/us.png", "region": "Americas"},
            {"name": "Canada", "flag": "https://flagcdn.com/w320/ca.png", "region": "Americas"},
            {"name": "France", "flag": "https://flagcdn.com/w320/fr.png", "region": "Europe"},
            {"name": "Japan", "flag": "https://flagcdn.com/w320/jp.png", "region": "Asia"},
            {"name": "Brazil", "flag": "https://flagcdn.com/w320/br.png", "region": "Americas"}
        ]

load_countries()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_question')
def get_question():
    continent = request.args.get('continent', 'All')
    
    # Filter list based on continent selection
    if continent != 'All':
        pool = [c for c in ALL_COUNTRIES if c['region'] == continent]
    else:
        pool = ALL_COUNTRIES

    if len(pool) < 4:
        pool = ALL_COUNTRIES # Fallback if pool is too small

    options = random.sample(pool, 4)
    target = random.choice(options)
    
    return jsonify({
        "flag": target['flag'],
        "answer": target['name'],
        "options": [c['name'] for c in options]
    })

if __name__ == '__main__':
    app.run(debug=True)