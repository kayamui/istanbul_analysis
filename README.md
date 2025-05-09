
# 📊 Istanbul Emergency Medical Services Analysis

**Author:** Muhammed Kaya  
**Team:** KodlaYaşat (Istanbul 112 Paramedic Developers)

---

## 🔍 Overview

This project is a comprehensive analytical toolkit designed to evaluate and optimize the performance of Istanbul's Emergency Medical Services (EMS). It includes a wide range of Python tools and Jupyter notebooks that analyze transport efficiency, GPS reactions, shift patterns, and case tracking — tailored specifically for the Istanbul 112 Ambulance Service.

---

## 📁 Project Structure

```
istanbul_analysis/
│
├── ambulance_working_distances.ipynb          # Ambulance coverage and distance calculations
├── asia_transport_chief_analysis.ipynb        # Shift and staff analytics for Asia region
├── extra_shift_analysis.ipynb                 # Evaluation of additional shift workloads
├── tensorflow_workout.ipynb                   # Experimentation with ML models
├── statistics_secondary_transports_original_file_workout.ipynb  # Second transport stat analysis
│
├── GPS Data Processor/
│   └── gps_reactions.py                       # Reaction time analysis based on GPS data
│
├── ambulance_troubles/
│   └── monthly_district_reach_times.py        # Average ambulance reach time per district
│
├── case_tracking/
│   └── call_list_creator/
│       ├── call_list_create_gui.py            # GUI for manual call list generation
│       ├── call_list_creator.py               # Logic for generating call lists
│       └── unlock_code.py                     # Unlocking mechanism for GUI access
│
├── .gitignore
└── README.md
```

---

## 🔧 Features

- 📍 **Geospatial Reach Analysis**  
  Analyze ambulance reach times per district using GIS and time metrics.

- 🧮 **Shift Workload Insights**  
  Monitor and assess additional shifts and staff activity.

- 🚑 **Call & Case Tracking Tools**  
  GUI-driven modules for building and exporting call lists.

- 🛰️ **GPS Reaction Analysis**  
  Evaluate real-time ambulance deployment speed using GPS logs.

- 🤖 **AI/ML Module (Experimental)**  
  Early-stage TensorFlow experiments to forecast EMS performance.

---

## 🛠️ Requirements

- Python 3.8+
- pandas, geopandas, folium, matplotlib
- tkinter (for GUI tools)
- Jupyter Notebook (for .ipynb files)
- XlsxWriter (for Excel export functionality)

Install with:
```bash
pip install -r requirements.txt
```

---

## 🚀 How to Use

1. Clone the repo:
   ```bash
   git clone https://github.com/kayamui/istanbul_analysis.git
   ```

2. Navigate into a notebook or Python module:
   ```bash
   cd istanbul_analysis
   ```

3. Run notebooks for analysis or use GUI scripts via:
   ```bash
   python case_tracking/call_list_creator/call_list_create_gui.py
   ```

---

## 📌 Use Case

This project is used by Istanbul's European Side Ambulance Service and UMKE (National Medical Rescue Team) to:

- Improve emergency response time
- Track ambulance effectiveness by region
- Plan efficient staffing and transport
- Enable offline call tracking during disasters

---

## 👨‍⚕️ Built By

A dedicated team of paramedics and data engineers on a mission to **code to save lives.**  
**Group Name:** KodlaYaşat  
**Focus:** Innovation in Emergency Services (112 EMS, UMKE)
