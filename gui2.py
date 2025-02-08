import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSplitter
# from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebKitWidgets import QWebView
import requests
from PyQt5.QtCore import QTimer

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from io import BytesIO
STATES = ['NY', 'NJ']


def get_forecast(latitude, longitude):
    points_url = f'https://api.weather.gov/points/{latitude},{longitude}'
    try:
        response = requests.get(points_url)
        response.raise_for_status()
        grid_x = response.json()['properties']['gridX']
        grid_y = response.json()['properties']['gridY']
        office = response.json()['properties']['cwa']

        forecast_url = f'https://api.weather.gov/gridpoints/{office}/{grid_x},{grid_y}/forecast'
        response = requests.get(forecast_url)
        response.raise_for_status()
        for period in response.json()['properties']['periods']:
            name = period['name']
            temperature = period['temperature']
            detailed_forecast = period['detailedForecast']
            print(f"{name}: {temperature}°. {detailed_forecast}")

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")


def download_image(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Image successfully downloaded as {filename}")

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")


def fetch_state_alerts():
    alerts = []
    for state in STATES:
        try:
            url = f'https://api.weather.gov/alerts/active?area={state}'
            response = requests.get(url)
            # Debug print
            print(f"Response for {state}: {response.status_code}")
            response.raise_for_status()
            json_data = response.json()
            print(f"JSON data for {state}: {json_data}")  # Debug print
            state_alerts = json_data['features']
            alerts.extend(state_alerts)
        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error for {state}: {err}")
        except Exception as err:
            print(f"An error occurred for {state}: {err}")
    return alerts


class WeatherApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Weather App")

        # To fit the window to the entire screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.setGeometry(screen_geometry)

        # Splitter for two main parts of the window
        main_splitter = QSplitter()

        # Initialize hydrographs
        hydro_image1_data = requests.get(
            'https://water.weather.gov/resources/hydrographs/pppn4_hg.png').content
        self.hydro_image1 = QPixmap()
        self.hydro_image1.loadFromData(BytesIO(hydro_image1_data).read())

        hydro_image2_data = requests.get(
            'https://water.weather.gov/resources/hydrographs/pinn4_hg.png').content
        self.hydro_image2 = QPixmap()
        self.hydro_image2.loadFromData(BytesIO(hydro_image2_data).read())

        self.current_hydro_image = self.hydro_image1

        # Adding radar (web view) to the left of the splitter
        self.browser = QWebView(self)
        self.browser.setUrl(QUrl("http://localhost:5000/"))
        main_splitter.addWidget(self.browser)

        # Layout for the right side of the splitter
        right_layout = QVBoxLayout()

        # Header for Alerts
        self.alerts_header = QLabel("Alerts", self)
        self.alerts_header.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #333;")
        right_layout.addWidget(self.alerts_header)

        # Adding alerts and forecast to the right layout
        self.alerts_text = QTextEdit(self)
        self.alerts_text.setPlaceholderText("Loading alerts...")
        self.alerts_text.setStyleSheet(
            "background-color: #e6e6e6; border-radius: 5px; padding: 10px;")
        right_layout.addWidget(self.alerts_text, 1)

        # Header for Forecast
        self.forecast_header = QLabel("Forecast", self)
        self.forecast_header.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #333;")
        right_layout.addWidget(self.forecast_header)

        self.forecast_text = QTextEdit(self)
        self.forecast_text.setPlaceholderText("Loading forecast...")
        self.forecast_text.setStyleSheet(
            "background-color: #e6e6e6; border-radius: 5px; padding: 10px;")

        right_layout.addWidget(self.forecast_text, 1)

        # Layout for hydrograph image and button
        hydro_layout = QVBoxLayout()
        self.hydro_label = QLabel(self)
        self.hydro_label.setPixmap(self.current_hydro_image)
        hydro_layout.addWidget(self.hydro_label)

        self.toggle_button = QPushButton("PRESS TO TOGGLE", self)
        # Style the button
        self.toggle_button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 12px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)

        self.toggle_button.clicked.connect(self.toggle_hydrographs)
        hydro_layout.addWidget(self.toggle_button)

        # Adding hydrograph layout to the right layout
        right_layout.addLayout(hydro_layout, 2)

        # Create a widget to set the right layout, then add this widget to the splitter
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        main_splitter.addWidget(right_widget)

        # Set the splitter as the central widget
        self.setCentralWidget(main_splitter)
        self.setStyleSheet("background-color: #f2f2f2;")
        # Split the widgets 50-50 in the splitter
        width = screen_geometry.width()
        main_splitter.setSizes([width // 2, width // 2])
        # Placeholder data fetch on app start
        self.update_alerts()
        self.update_forecast()
        self.auto_update()

    def update_alerts(self):
        alerts = fetch_state_alerts()
        self.alerts_text.clear()
        for alert in alerts:
            properties = alert['properties']
            self.alerts_text.append(f"Area: {properties['areaDesc']}")
            self.alerts_text.append(f"Alert: {properties['headline']}")
            self.alerts_text.append(
                f"Description: {properties['description']}")
            self.alerts_text.append(
                f"Instruction: {properties['instruction']}\n")

    def toggle_hydrographs(self):
        if self.current_hydro_image == self.hydro_image1:
            self.current_hydro_image = self.hydro_image2
            self.toggle_button.setText("POMPTON RIVER AT POMPTON PLAINS")
        else:
            self.current_hydro_image = self.hydro_image1
            self.toggle_button.setText("PASSAIC RIVER AT PINE BROOK")
        self.hydro_label.setPixmap(self.current_hydro_image)

    def update_forecast(self):
        self.forecast_text.clear()
        for loc, lat, lon in [("New York", 40.720800, -73.982200), ("New Jersey", 40.7178, -74.0431)]:
            self.forecast_text.append(f"{loc} Forecast:")
            points_url = f'https://api.weather.gov/points/{lat},{lon}'
            response = requests.get(points_url)
            grid_x = response.json()['properties']['gridX']
            grid_y = response.json()['properties']['gridY']
            office = response.json()['properties']['cwa']
            forecast_url = f'https://api.weather.gov/gridpoints/{office}/{grid_x},{grid_y}/forecast'
            forecast_data = requests.get(forecast_url).json()
            for period in forecast_data['properties']['periods']:
                self.forecast_text.append(
                    f"{period['name']}: {period['temperature']}°. {period['detailedForecast']}")
            self.forecast_text.append("")

    def update_hydrographs(self):
        hydro_image1_data = requests.get(
            'https://water.weather.gov/resources/hydrographs/pppn4_hg.png').content
        self.hydro_image1.loadFromData(BytesIO(hydro_image1_data).read())

        hydro_image2_data = requests.get(
            'https://water.weather.gov/resources/hydrographs/pinn4_hg.png').content
        self.hydro_image2.loadFromData(BytesIO(hydro_image2_data).read())

        # If you want to immediately update the currently displayed hydrograph
        if self.current_hydro_image == self.hydro_image1:
            self.hydro_label.setPixmap(self.hydro_image1)
        else:
            self.hydro_label.setPixmap(self.hydro_image2)

    def auto_update(self):
        self.update_alerts()
        self.update_forecast()
        self.update_hydrographs()
        # Refresh browser content (since the map is served through localhost)
        self.browser.reload()
        # Update every 10 minutes
        QTimer.singleShot(60000, self.auto_update)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
