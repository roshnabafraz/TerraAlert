# TerraAlert Final Year Project: Technical Documentation Report

This document serves as an exhaustive, academically structured technical report detailing the **TerraAlert** system. The analysis relies directly upon deep inspection of the repository structure, codebase algorithms, logic execution flows, and integrations.

---

## 1. Project Purpose and Problem Solved
TerraAlert addresses the critical global challenge of fragmented disaster risk awareness. During unfolding natural disasters—such as floods, earthquakes, heatwaves, and cyclones—publicly available data is heavily disjointed. 
The system solves this real-world problem by autonomously aggregating data from multiple official remote feeds, classifying raw reports using a machine learning pipeline, applying a mathematically sound heuristic formula to score risk recency, and generating localized, human-readable alert guidance. The purpose is to centralize disaster intelligence to aid civilian preparedness via a simple localized dashboard.

## 2. High-Level System Overview
TerraAlert operates as a monolithic web application structured around the Flask framework. The platform interacts dynamically with external remote APIs and RSS feeds to securely transmit updates on geological and meteorological anomalies.
Raw responses are parsed, sanitized, and channeled into a Machine Learning classification model (`LogisticRegression` combined with a `TfidfVectorizer`) when source categorization is unidentifiable. A core rule engine then calculates exponential-decay risk ratings and writes the output directly into a local SQLite database for historical logging and visual deployment. The web frontend empowers users to lookup risk profiles geographically through HTML5 Leaflet integrations mapping out live threats.

## 3. Folder Structure and Explanations
* `README.md` & `requirements.txt`: Describe the contextual roadmap and Python dependency graph mapping.
* `run.py` & `wsgi.py`: Root application entry points configured for WSGI deployment protocols.
* `app/`: Houses the core Flask application.
  * `__init__.py`: Implements a factory design pattern to scaffold the routing structure, template directories, and configuration settings safely without global circular dependencies.
  * `config.py`: Dedicated configuration structure interpreting injected environment properties gracefully.
  * `models/`: Regulates all data-access parameters explicitly (`database.py`), managing SQLite initialization and parameter-bound query injections for safety.
  * `routes.py`: Flask network controller mapping HTML/JSON views to the HTTP request cycle.
  * `services/`: Primary host for isolated business logic. Composed of `alert_generator.py`, `classifier.py`, `data_collector.py`, `digd_detector.py`, `location_analyzer.py`, `permanent_location.py`, and `risk_calculator.py`.
  * `utils/`: Reusable micro-helpers executing JSON deserializations, datetime casting, and text sanitization.
  * `static/`: Encapsulates client-side assets comprising modular SCSS derivatives and JavaScript Leaflet DOM logic (`map.js`).
* `ml/`: Sub-module specifically containing artificial intelligence logic. Features `train_model.py` and `evaluate_model.py`, including corresponding model output artifacts (`.pkl` dumps) and structured `datasets/`.
* `data/`: Storage pool for local JSON context dictionaries (`contacts.json`, `guidance/`, `sources/`) and SQLite blobs.
* `scripts/`: Offline processing tooling (`init_db.py`, `populate_guidance.py`, `schedule_scraper.py`).
* `templates/`: Implements the Jinja2 context HTML template UI hierarchy.
* `tests/`: Project unit and integration tests executing under `pytest`.

## 4. Architecture Style
TerraAlert embodies a modern **Monolithic Model-View-Controller (MVC) enhanced by a Service Layer architecture**.
* **Controllers**: Imposed via `app/routes.py`, dictating presentation logic and interface negotiation.
* **Services Layer**: Disentangles the HTTP context from business models by channeling core processes (e.g., calculations, ML) into testable `app/services` components.
* **Models**: Data manipulation executed raw-level using Python's primitive `sqlite3` cursors without an intermediary ORM, providing exceptionally lightweight transactions.
* **Views**: Evaluated using Flask's native Jinja2 engine combined directly with browser-parsed HTML/JS artifacts.

## 5. Core Modules/Components
* **Data Collector (`data_collector.py`)**: Consumes JSON configurations representing live agency pipelines (e.g., USGS and NWS APIs, Atom/GDACS). Capable of gracefully managing distinct structures automatically via standard request polling.
* **Classifier (`classifier.py`)**: Employs ML object prediction arrays mapping unstructured event summaries to core classes like "flood" or "earthquake" alongside derived severity tiers.
* **Risk Calculator (`risk_calculator.py`)**: Manages quantitative exposure thresholds through mathematical half-lives dynamically scaling down ancient data relevance.
* **DIGD Detector (`digd_detector.py`)**: Detects Information Gaps in Disasters (DIGD). Systematically isolates locations reflecting high-severity phrasing but low volume indices, suggesting critical reporting dropoffs indicative of infrastructure outages.
* **Alert Generator (`alert_generator.py`)**: Translates numeric boundaries from the Calculator into persistent textual emergency statuses sent directly towards the DB storage node.

## 6. Data Flow
1. Consumer submits target localized telemetry on the browser Dashboard.
2. HTTP POST interacts with `routes.py`, which initializes synchronous `collect_disaster_data()` events.
3. Defined external APIs are sequentially requested via `requests`; HTTP response structures are destructured and standardized into unified dictionary items.
4. Aggregated arrays run sequentially through `classify_reports()`, appending normalized `disaster_type` strings based on lexical keyword maps and AI analysis.
5. Content is isolated strictly via target geographical string boundaries using `filter_by_location()`.
6. Stored permanently referencing relational constraints inside SQLite.
7. Fresh data subsets invoke `calculate_risk_summary()` constructing the temporal metrics calculations.
8. The overarching percentages derive logical boundaries dictating `generate_alerts()` payloads prior to persistence.
9. Final contextual payload yields natively into the Jinja representation parsing back up to the end-user representation logic.

## 7. Business Logic
* **Data Normalization**: Translates vastly incongruent geographic and temporal fields across varying international frameworks strictly to `UTC ISO-8601` timestamps standardizing comparisons.
* **Temporal Prioritization**: Algorithm scales down event risks sequentially applying a three-day decay half-life, ensuring the platform highlights genuinely imminent catastrophes.
* **Information Gap Assessment**: Disconnect tracking triggers automatically identifying disparities between high semantic urgency and anomalously low quantitative aggregation volume signaling localized network partitioning.

## 8. User Roles
The application currently maintains a highly flattened permission domain modeling a generalized **Guest** system model. 
* *Inference:* The logic driving `permanent_location.py` contains hard-coded parameters pointing toward a `user_id="default_user"`. This represents a strong foundation implying future enhancements intend to embrace multi-tenant authenticated profiles, however, inside this version, the user context runs globally unprotected.

## 9. Major Endpoints/Services
* **`GET /`**: Presents the generic `index.html` landing page while validating any pre-existent localized `permanent_location`.
* **`GET|POST /dashboard`**: Primary core controller. Validates target locators explicitly utilizing `parse_location_input`. If inputs are confirmed, fully ignites the synchronous REST pipeline compiling risks locally mapped into the context array.
* **`GET /alerts`**: Retrieves bulk stored chronological DB logs restricting bounds up to 50 items formatting cleanly by presentation tier.
* **`GET /guidance`**: Maps raw emergency instructional references consumed via localized JSON (`guidance/precautions.json`).
* **`GET /help`**: Dynamically maps regional emergency contacts or fallbacks safely to hardcoded constants mitigating downtime constraints.
* **`GET /api/risk`**: Implements JSON parity exposing the full Dashboard capabilities context objects programmatically mapping mobile client consumption.
* **CRUD API `/api/permanent-location`**: `GET`, `POST`, and `DELETE` hooks binding persistent address values globally.

## 10. Database Schema and Models
SQLite3 executes transparent, lightweight, raw SQL executions mapping strictly normalized relational elements.
* **`disaster_reports`**: Comprises raw events maintaining tracking of (`id`, `title`, `content`, `source`, `published_at`, `location`, `disaster_type`, `severity`, `created_at`).
* **`guidance`**: Tenuously normalized static table preserving (`disaster_type`, `tips`).
* **`alerts`**: Tracks final generated alerts restricting against duplication spam retaining fields (`id`, `created_at`, `location`, `disaster_type`, `level`, `message`, `risk_percentage`).

## 11. APIs Used/Exposed
* **Consumed Dependencies**: 
   * **USGS Earthquake API**: Parses custom `geojson_usgs` representations tracking realtime planetary tremors.
   * **NWS Alerts API**: Consumes strictly bound geographic alerts routing dynamically using custom string variables mapped explicitly inside `features/properties`.
   * **RSS Syndications**: Implemented using pure Python `feedparser` digesting global atom streams (GDACS, NHC).
* **Exposed Elements**: JSON HTTP endpoints `/api/risk` alongside location managers dictating preferences via REST.

## 12. Authentication and Authorization
Implementation remains natively absent. Users interact completely anonymously exposing generic functional interactions. The application binds exclusively default mock identifiers.

## 13. External Libraries & SDKs
* **Flask**: Minimalist WSGI Python routing chassis optimizing request flows asynchronously without overhead.
* **Requests / Feedparser**: Orchestrating all networking bindings. `Requests` serves REST parsing natively whereas `Feedparser` guarantees safety against corrupted XML formats common in international feeds.
* **Scikit-Learn, Joblib**: Provides structural ML frameworks predicting textual variables rapidly leveraging CPU architectures cleanly without dictating massive dependencies alongside complex vector matrix transformations.
* **Pandas**: Manages internal raw statistical matrix ingestion pipelines for CSV mappings locally generating predictions securely.
* **Leaflet**: Frontend Javascript interface interpreting location coordinates mapping directly into robust graphical user views instantly.

## 14. State, Async & Error Handling
* **State Execution**: HTTP transactions reside inherently stateless besides global config objects instantiated inside memory loops preserving SQLite transactional integrity cleanly handling requests simultaneously without session congestion.
* **Async Approach**: Event boundaries compile strictly inside synchronous locking paths implying that remote dependencies effectively pause HTML rendering dynamically triggering blocking execution sequences. *Inference:* Offline processing occurs separately targeting explicit cron scheduling mapping towards `schedule_scraper.py`.
* **Error Bounds**: Comprehensive exception mitigation encapsulates external fetching (`try: request ... except Exception: continue`). Defective remote infrastructure simply omits iterations without terminating platform rendering.

## 15. Important Algorithms & Workflows
* **Recency Decay Formula**: Implemented mathematically inside `risk_calculator.py`. Formats natively as: `math.exp(-age_days / max(half_life_days, 0.1))` enforcing explicit penalties preventing minor historic occurrences impacting scores perpetually.
* **Risk Score Ceiling Mitigation**: Totals represent aggregations mapped natively as `SUM(ScoreBase * SeverityWeight * RecencyWeight)` capped intelligently leveraging primitive `min(100, round(score))` protecting frontend limits strictly locking scales universally.
* **Classifier Heuristic Fail-Safe**: A dynamic multi-level classification funnel exists. If the dataset `pkl` binary is missing or corrupted on startup, operations scale downward relying purely upon hardcoded substring normalization array indexing protecting operational uptime constantly.

## 16. Validation & Security
* Structural query injection mitigations actively prevent parameter manipulation dynamically encoding fields transparently over raw `?` parameterized queries handling DB interactions securely.
* The system utilizes specific user-agents dictating headers effectively routing network bans cleanly inside `Config` structures preventing global bot filters dropping critical payloads externally over prolonged interactions gracefully.
* Configuration properties bind directly against OS environment variables natively avoiding explicitly committing secret structures exposing vulnerability tokens cleanly.
* *Constraint*: The system noticeably excludes inherent API rate-limiting structures leaving open risks for simple denial-of-service iterations.

## 17. Model Training & Inference Workflow
1. The developer instantiates explicit training loops interacting manually across the `train_model.py` environment pulling structures directly referencing `ml/datasets/labeled/training_data.csv`.
2. Pipeline generates automated mapping splitting targets 80/20 executing `TfidfVectorizer` logic indexing word n-grams directly against traditional algorithmic `LogisticRegression` structures pushing files directly upon outputs.
3. System loads vectors autonomously upon request cycle initializations loading binary dependencies transparently routing unstructured paragraph payloads outputting categorized text strings directly into functional workflows seamlessly resolving unknowns securely.

## 18. Setup, Configuration
Dependencies strictly defined mapping Python PIP protocols matching exact library versions within requirements parsing directly utilizing conventional `.env` setups indexing application keys gracefully dictating variables securely managing global execution weights strictly inside standard constant environments.

## 19. Build & Deployment
Application contains defined `wsgi.py` patterns directly compatible interfacing over standard Linux `Gunicorn` deployments alongside explicit serverless infrastructure integrations binding properties managing `vercel.json` configurations actively rendering completely scalable remote server operations efficiently globally.

## 20. Technical Constraints
* **Synchronous Bottlenecks**: Web handlers process upstream API interactions dynamically slowing page renderings substantially across delayed networks blocking user experience capabilities tangibly.
* **Date Destructuring**: Formats across varied global platforms differ unpredictably forcing heavy reliance upon automated date-util guesses resulting occasionally inside default UTC overrides compromising data precision.

## 21. Suggestions for Future Improvements
1. **Asynchronous Architecture Implementation**: Rewrite API fetching sub-routines applying Python's non-blocking `asyncio/aiohttp` frameworks or pushing operations permanently offline relying on background queue orchestrators like `Celery/Redis`.
2. **Database Scale Upgrading**: Transcribing SQLite raw instructions utilizing mature ORMs dictating robust PostgreSQL server implementations protecting heavy write bottlenecks cleanly.
3. **API Security Implementation**: Introduction identifying secure JWT or session token handlers protecting rate limits dynamically resolving user authentication barriers cleanly structuring profile architectures uniquely allowing location tracking independently.
4. **Enhanced ML Pipelines**: Introduce deeper Transformer/BERT neural networks dynamically parsing complex nuanced linguistic structures preventing string collision false positives explicitly guaranteeing precise detection cleanly.
