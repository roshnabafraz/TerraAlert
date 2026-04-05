# TerraAlert Suggested References and Literature Review Guide

This document provides a structured foundation for generating the references and literature review chapters of your Final Year Project (FYP) report. It is tailored specifically to the technologies, machine learning algorithms, and disaster domains present within the TerraAlert codebase.

---

## 1. Suggested Literature Review Topics
When researching academic sources for the literature review chapter, structure your queries around the following domains to align with your project's features:
* **The Role of Early Warning Systems (EWS) in Disaster Risk Reduction:** Focus on how centralized dashboards improve response times.
* **Natural Language Processing (NLP) in Crisis Informatics:** Research how models categorize emergency texts, specifically the success of linear models (Logistic Regression) vs complex deep learning.
* **Feature Extraction techniques in noisy data:** Compare TF-IDF (which TerraAlert uses) against modern Word Embeddings (Word2Vec, BERT) for short text structures (like news headlines or RSS feeds).
* **Geospatial Web Applications:** Review the effectiveness of WebGIS structures (Leaflet/Web APIs) in disseminating geographic threats to civilians without specialized hardware.
* **Information Gaps (DIGD):** Research papers that discuss sensor/reporting failures during extreme weather events and how systems detect "blackouts" or blind-spots.

---

## 2. Official Documentation References

These references should be cited when explaining the structural software decisions, frameworks, and APIs utilized in the project.

**[1] Web Framework (Flask):**
> Pallets Projects, "Flask Documentation (3.0.x)," *Flask API Reference*, 2024. [Online]. Available: https://flask.palletsprojects.com/. [Accessed: April 2026].

**[2] Machine Learning Core (Scikit-Learn):**
> F. Pedregosa *et al.*, "Scikit-learn: Machine Learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825-2830, 2011.

**[3] Mapping & Visualization (Leaflet):**
> V. Agafonkin, "Leaflet - a JavaScript library for interactive maps," 2024. [Online]. Available: https://leafletjs.com. [Accessed: April 2026].

**[4] Geocoding Service (Nominatim):**
> OpenStreetMap Foundation, "Nominatim Usage Policy and Documentation," 2024. [Online]. Available: https://nominatim.org/release-docs/latest/. [Accessed: April 2026].

---

## 3. Disaster Management & Open Data References

These references justify the data sources driving TerraAlert and establish the domain constraints.

**[5] Global Feeds (GDACS):**
> Global Disaster Alert and Coordination System (GDACS), "GDACS RSS Data Feeds and Alert Mechanisms," United Nations & European Commission, 2024. [Online]. Available: https://www.gdacs.org/xml/. [Accessed: April 2026].

**[6] Geological Monitoring (USGS):**
> U.S. Geological Survey (USGS), "Earthquake Hazards Program: Real-time GeoJSON Feeds," U.S. Department of the Interior, 2024. [Online]. Available: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php. [Accessed: April 2026].

**[7] Weather & Flood Warnings (NOAA/NWS):**
> National Weather Service (NWS), "NWS Public API Web Services," NOAA, 2024. [Online]. Available: https://www.weather.gov/documentation/services-web-api. [Accessed: April 2026].

**[8] Disaster Risk Frameworks [Verify before submission]:**
> UNISDR, "Sendai Framework for Disaster Risk Reduction 2015-2030," United Nations Office for Disaster Risk Reduction, 2015. *(Note: Perfect citation for the theoretical basis on why Early Warning Systems like TerraAlert are necessary)*.

---

## 4. Machine Learning & Algorithm References

These references provide mathematical backing for the algorithms utilized in the `ml/` directory (TF-IDF and Logistic Regression) and exponential decay logic.

**[9] Foundational NLP & TF-IDF:**
> C. D. Manning, P. Raghavan, and H. Schütze, *Introduction to Information Retrieval*. Cambridge: Cambridge University Press, 2008, pp. 109-122. *(Note: Canonical textbook for citing TF-IDF extraction mechanisms)*.

**[10] Logistic Regression for Classification:**
> D. W. Hosmer Jr, S. Lemeshow, and R. X. Sturdivant, *Applied Logistic Regression*, 3rd ed. Hoboken, NJ: John Wiley & Sons, 2013.

**[11] Crisis Informatics & ML [Verify before submission]:**
> M. Imran, C. Castillo, F. Diaz, and S. Vieweg, "Processing Social Media Messages in Mass Emergency: A Survey," *ACM Computing Surveys*, vol. 47, no. 4, pp. 1-38, 2015. *(Note: Excellent foundational paper analyzing how textual feeds act as real-time sensors during floods and earthquakes).*

**[12] Time-Decay and Relevance Functions in Streaming Data [Verify before submission]:**
> G. Cormode, V. Shkapenyuk, D. Srivastava, and K. Xu, "Forward decay: A practical time decay model for streaming systems," in *25th IEEE International Conference on Data Engineering*, Shanghai, China, 2009, pp. 138-149. *(Note: Use this to mathematically justify TerraAlert's Half-life Recency Decay algorithmic core).*

---

### Tips for Final Submission
* Ensure all `[Accessed: April 2026]` tags match the actual month your report is turned in.
* For the `[Verify before submission]` entries, ensure you review the abstracts on Google Scholar to properly align them with your exact university report narrative.
* You may want to add one extra citation covering the history of the **SQLite** embedded engine directly to bolster the argument for lightweight spatial storage.
