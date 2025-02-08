# Weather App with PyQt5

A weather monitoring application built using PyQt5 that displays weather alerts, forecasts, and hydrograph images with an embedded web view for additional content.


---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Code Structure](#code-structure)
- [Contributing](#contributing)
- [License](#license)
- [Final Thoughts](#final-thoughts)

---

## Overview
This project implements a weather monitoring application using PyQt5. The application:
- Fetches weather alerts and forecasts from the National Weather Service API.
- Displays alerts, forecasts, and hydrograph images in an intuitive GUI.
- Provides an embedded browser view to load local web content.
- Automatically updates the displayed data every 10 minutes.

---

## Features
- **Weather Alerts:** Retrieves and displays active weather alerts for predefined states.
- **Weather Forecast:** Fetches and shows detailed forecasts for selected locations.
- **Hydrographs:** Displays hydrograph images with a toggle button to switch between different views.
- **Embedded Browser:** Integrates a web view (using QWebKit) to display content from a local server.
- **Auto Update:** Refreshes alerts, forecasts, and hydrograph images every 10 minutes.

---

## Demo
<video src="demo_video.mp4" controls width="640" height="360">
</video>

---

## Requirements
- **Python 3.x**
- **PyQt5** – For building the GUI.
- **Requests** – For making HTTP requests to fetch weather data.

> **Note:** This project uses `PyQt5.QtWebKitWidgets` for the embedded browser. If you prefer, you can switch to `PyQt5.QtWebEngineWidgets`.

You can install the required packages using pip:
```bash
pip install PyQt5 requests
