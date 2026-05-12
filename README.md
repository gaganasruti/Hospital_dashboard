# Hospital_dashboard
# 🏥 Healthcare Appointment No-Show Analytics Dashboard

A professional interactive analytics dashboard built with Streamlit and Plotly, 
inspired by Power BI design. Analyzes hospital appointment no-show patterns.

## 🔗 Live Demo
[Click here to view the dashboard](https://hospital-noshow-dashboard.streamlit.app/)

## 📊 Dashboard Features

### KPI Cards
- Total Appointments
- No-Show Count
- No-Show Percentage
- Average Patient Age

### Page 1 — Overview
- Appointment Attendance by Gender (Pie chart)
- Total Appointments by Age Group (Bar chart)
- No-Show Count by Age (Area chart)
- Missed Appointments by SMS Received (Bar chart)

### Page 2 — Patient & Medical
- No-Show Rate by Gender
- No-Show Rate by Medical Condition
- Attendance Rate by SMS Reminder
- Appointments & No-Show Rate by Comorbidity Count

### Page 3 — Time & Geography
- No-Show Rate by Wait Group
- No-Show Count Over Time
- Total Appointments Over Time
- No-Show Rate by Neighbourhood (Top 20)

## 🔍 Sidebar Filters
- Gender
- Age Group
- Appointment Day
- Scholarship
- SMS Received

## 📁 Dataset
Based on the **Kaggle Medical Appointment No-Shows** dataset containing:
- 110,521 appointments
- 62,298 unique patients
- 81 neighbourhoods
- Date range: April–June 2016

## 🛠️ Tech Stack
| Tool | Purpose |
|------|---------|
| Streamlit | Web app framework |
| Plotly | Interactive charts |
| Pandas | Data processing |
| Python | Core language |

## 🚀 Run Locally
```bash
pip install streamlit pandas plotly numpy
streamlit run hospital_dashboard.py
```

## 📂 Project Structure
hospital-dashboard/
│
├── hospital_dashboard.py   # Main dashboard app
├── cleaned.csv             # Cleaned dataset
├── requirements.txt        # Python dependencies
└── README.md               # This file
