# TerraAlert 🌍💧

**TerraAlert** is a web-based, AI-assisted disaster risk awareness system. It aggregates real-time natural disaster telemetry from around the world, classifies incident reports using Machine Learning, calculates localized risk probabilities utilizing a temporal decay algorithm, and provides geospatial alerts & precautionary guidelines.

With TerraAlert, fragmented disaster data becomes centralized intelligence, empowering civilian preparedness through a streamlined, localized dashboard.

---

## ✨ Key Features

- **🌐 Live Data Aggregation:** Automatically consumes remote APIs and RSS/Atom feeds (USGS, NWS, GDACS, NOAA) to track geological and meteorological anomalies natively.
- **🧠 Machine Learning Classification:** Utilizes Scikit-learn (`LogisticRegression` + `TfidfVectorizer`) to categorize unstructured report texts into known disaster types (e.g., `flood`, `earthquake`, `heatwave`, `cyclone`). Features an intelligent dictionary-based fallback if the model is unavailable.
- **📉 Dynamic Risk Scoring (Temporal Decay):** Employs an exponential-decay mathematical formula to adjust risk levels based on time and severity to highlight genuinely imminent catastrophes.
- **🗺️ Geospatial Mapping:** Renders active localized risks intelligently via Leaflet.js on an interactive HTML5 dashboard.
- **⚠️ DIGD Detection:** Automatically identifies "Information Gaps in Disasters" (DIGD)—situations with high semantic urgency but low reporting volume, signaling potential infrastructure and network outages.
- **💾 Local SQLite Caching:** Ensures fast reads and deduplicates redundant alerts to prevent notification spam.

---

## 🛠️ Tech Stack

### Backend
- **Python 3 / Flask:** Core WSGI web application framework and routing routing chassis.
- **SQLite3:** Lightweight relational database utilizing raw SQL statements without an ORM for speed and transparency.
- **Requests & Feedparser:** Robust handlers for parsing external REST APIs and corrupted XML/RSS schemas cleanly.

### Machine Learning (AI)
- **Scikit-Learn & Joblib:** Fast, CPU-compatible linear classification arrays saving models as portable `.pkl` binaries.
- **Pandas:** Handles the internal CSV data structures for training pipeline management.

### Frontend
- **HTML5 / CSS / JS:** Server-side rendered templates using Jinja2 context variables.
- **Leaflet.js:** Interactive geospatial maps logic.
- **SCSS:** Modular presentation stylesheets.

---

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/roshnabafraz/TerraAlert.git
cd TerraAlert
```

### 2. Create a Virtual Environment
It's strongly recommended to use a virtual environment.

**Windows:**
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install all required libraries via pip:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Set up required configuration variables using the provided template:
```bash
cp .env.example .env
```
Open `.env` and customize parameters such as `RISK_WINDOW_DAYS`, `HIGH_RISK_THRESHOLD`, and `NWS_USER_AGENT` if needed.

### 5. Initialize the Database
Bootstraps the raw SQLite dataset tables (`disaster_reports`, `alerts`, `guidance`):
```bash
python scripts/init_db.py
```

### 6. Train the ML Model (Highly Recommended)
While the app has a keyword-match fallback, the prediction accuracy drastically improves with the ML model. Run the training script to parse `training_data.csv` and generate `ml/models/disaster_classifier.pkl`:
```bash
python ml/train_model.py
```

### 7. Run the Application
Start the Flask development server:
```bash
python run.py
```
Open up your browser and navigate to `http://127.0.0.1:5000` to interact with the TerraAlert dashboard!

---

## 📊 System Architecture

TerraAlert maintains a lightweight **Monolithic MVC structure integrated with a Service Layer**.
- **Controllers (`app/routes.py`)**: Interacts with frontend templates and the core backend services.
- **Services (`app/services/`)**: Highly cohesive business-logic isolation (`classifier.py`, `risk_calculator.py`, `data_collector.py`).
- **Data Integrations**: Polling asynchronous API feeds synchronously during request lifecycles.
- **Machine Learning**: Pre-trained textual vectors process incoming unknown emergency inputs into actionable categories in under `10ms`.

---

## ☁️ Deployment

The repository includes a `vercel.json` file and a `wsgi.py` entry point. It is tailored to smoothly deploy on serverless platforms like Vercel or standard Linux VMs via Gunicorn.

---

## 📜 Legal & License

Created as a formal academic Final Year Project. Usage of public API feeds strictly conform to the originating organization bounds.
