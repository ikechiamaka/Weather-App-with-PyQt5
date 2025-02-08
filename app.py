from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route('/')
def index():
    response = requests.get("https://api.rainviewer.com/public/maps.json")
    timestamps = response.json()

    if timestamps:
        latest_timestamp = timestamps[-1]
    else:
        latest_timestamp = None

    return render_template('map.html', latest_timestamp=latest_timestamp)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
# if __name__ == "__main__":
#     app.run(host='0.0.0.0', debug=True, port=5000)
