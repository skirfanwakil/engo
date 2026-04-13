# UnityLink: Hyper-Local Community Resource Orchestrator 🤝

**UnityLink** is a decentralized community assistance platform built to bridge the gap between people in need and local volunteers. By leveraging real-time data synchronization and proximity-based matching, UnityLink ensures that help reaches the right person at the right time.

---

## 📖 Overview
In times of crisis or community need, information is often fragmented. UnityLink centralizes this data using a lightweight, cloud-integrated architecture. Whether it's food distribution, medical support, or educational tutoring, the platform connects users to the nearest available resource provider.

## ✨ Key Features
- **Smart Proximity Matching:** Uses a custom algorithm to calculate distance between Pincodes, displaying the nearest helpers first.
- **Data Integrity (Multi-Column Deduplication):** A robust "Strict Prevention" logic that blocks duplicate entries based on a composite key of `Contact Number + Help Type`.
- **Automated Database Maintenance:** Includes a standalone utility script (`CleanData.py`) to optimize and scrub the Google Sheets backend.
- **Dynamic Real-time Search:** Users receive instant matching results upon registration without a page reload.

---

## 🛠️ Technical Architecture
- **Backend:** Python 3.11 + Flask (RESTful API Design)
- **Database:** Google Sheets API v4 (Serverless Database approach)
- **Frontend:** Responsive HTML5, CSS3 (Modern UI), and Vanilla JavaScript
- **Security:** Service Account integration with OAuth2 for secure cloud communication.

---

## 📁 Project Structure
```text
unitylink/
├── app.py              # Main application logic & API endpoints
├── CleanData.py        # Database optimization & maintenance script
├── credentials.json    # Secure API credentials (GCP)
├── templates/          # User and Volunteer portal views
├── static/             # UI components and styling
└── README.md           # Documentation
