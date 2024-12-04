from flask import Flask, render_template, request, jsonify
import requests
import logging

app = Flask(__name__)

# 正しいURL設定
AREA_LIST_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
WEATHER_URL_TEMPLATE = "https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    try:
        data_json = requests.get(AREA_LIST_URL)
        data_json.raise_for_status()
        areas = data_json.json().get('class10s', {})
        return render_template('index.html', areas=areas)
    except requests.exceptions.RequestException as e:
        logging.error(f"地域リストの取得に失敗しました: {str(e)}")
        return "地域リストの取得に失敗しました。", 500

@app.route('/weather', methods=['GET'])
def weather():
    area_code = request.args.get('area_code')
    if not area_code:
        return jsonify({"error": "地域コードが指定されていません。"}), 400

    weather_url = WEATHER_URL_TEMPLATE.format(area_code=area_code)
    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        weather_data = response.json()
        return jsonify(weather_data)
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
        return jsonify({"error": "天気情報の取得に失敗しました。"}), 500
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
        return jsonify({"error": "天気情報の取得に失敗しました。"}), 500

if __name__ == '__main__':
    app.run(debug=True)