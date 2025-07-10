# Istanbul EMS Analysis

**Author**: Muhammed Kaya  
**Team**: KodlaYaşat (Istanbul 112 Paramedic Developers)

A comprehensive analytical toolkit designed to evaluate and optimize the performance of Istanbul's Emergency Medical Services (EMS). This project includes Python tools and Jupyter notebooks that analyze transport efficiency, GPS reactions, shift patterns, and case tracking — tailored specifically for the Istanbul 112 Ambulance Service.

## 🚑 About

This project is actively used by Istanbul's European Side Ambulance Service and UMKE (National Medical Rescue Team) to improve emergency response efficiency and save lives through data-driven insights.

**Mission**: A dedicated team of paramedics and data engineers on a mission to code to save lives.

## 📊 Key Features

- **📍 Geospatial Reach Analysis**: Analyze ambulance reach times per district using GIS and time metrics
- **🧮 Shift Workload Insights**: Monitor and assess additional shifts and staff activity
- **🚑 Call & Case Tracking Tools**: GUI-driven modules for building and exporting call lists
- **🛰️ GPS Reaction Analysis**: Evaluate real-time ambulance deployment speed using GPS logs
- **🤖 AI/ML Module (Experimental)**: Early-stage TensorFlow experiments to forecast EMS performance

## 📁 Project Structure

```
istanbul_analysis/
│
├── ambulance_working_distances.ipynb          # Ambulance coverage and distance calculations
├── asia_transport_chief_analysis.ipynb       # Shift and staff analytics for Asia region
├── extra_shift_analysis.ipynb                # Evaluation of additional shift workloads
├── tensorflow_workout.ipynb                  # Experimentation with ML models
├── statistics_secondary_transports_original_file_workout.ipynb # Second transport stat analysis
│
├── GPS Data Processor/
│   └── gps_reactions.py                      # Reaction time analysis based on GPS data
│
├── ambulance_troubles/
│   └── monthly_district_reach_times.py       # Average ambulance reach time per district
│
├── case_tracking/
│   └── call_list_creator/
│       ├── call_list_create_gui.py           # GUI for manual call list generation
│       ├── call_list_creator.py              # Logic for generating call lists
│       └── unlock_code.py                    # Unlocking mechanism for GUI access
│
├── .gitignore
└── README.md
```

## 🔧 Prerequisites

- Python 3.8+
- pandas, geopandas, folium, matplotlib
- tkinter (for GUI tools)
- Jupyter Notebook (for .ipynb files)
- XlsxWriter (for Excel export functionality)

## 📦 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/kayamui/istanbul_analysis.git
cd istanbul_analysis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Running Jupyter Notebooks

Navigate to the project directory and launch Jupyter:
```bash
jupyter notebook
```

**Key Notebooks:**
- `ambulance_working_distances.ipynb` - Analyze ambulance coverage areas and optimal positioning
- `asia_transport_chief_analysis.ipynb` - Staff performance and shift analysis for Asian side
- `extra_shift_analysis.ipynb` - Workload analysis for additional shifts
- `tensorflow_workout.ipynb` - Machine learning experiments for predictive analytics

### Running GUI Applications

Launch the call list creator GUI:
```bash
python case_tracking/call_list_creator/call_list_create_gui.py
```

### Running Analysis Scripts

**GPS Reaction Analysis:**
```bash
python "GPS Data Processor/gps_reactions.py"
```

**District Reach Time Analysis:**
```bash
python ambulance_troubles/monthly_district_reach_times.py
```

## 📈 Analysis Modules

### 1. Ambulance Coverage Analysis
- **File**: `ambulance_working_distances.ipynb`
- **Purpose**: Calculate optimal ambulance positioning and coverage areas
- **Output**: Distance matrices, coverage maps, efficiency metrics

### 2. Shift Performance Analytics
- **File**: `asia_transport_chief_analysis.ipynb`
- **Purpose**: Analyze staff performance and shift patterns
- **Output**: Workload reports, efficiency metrics, staff utilization

### 3. GPS Reaction Time Analysis
- **File**: `GPS Data Processor/gps_reactions.py`
- **Purpose**: Evaluate ambulance deployment speed using GPS data
- **Output**: Reaction time statistics, response efficiency metrics

### 4. District Reach Time Monitoring
- **File**: `ambulance_troubles/monthly_district_reach_times.py`
- **Purpose**: Track average ambulance reach times per district
- **Output**: Monthly reports, district-wise performance metrics

### 5. Call List Management
- **Files**: `case_tracking/call_list_creator/`
- **Purpose**: Generate and manage emergency call lists
- **Features**: GUI interface, Excel export, offline disaster tracking

### 6. Secondary Transport Analysis
- **File**: `statistics_secondary_transports_original_file_workout.ipynb`
- **Purpose**: Analyze secondary transport efficiency and patterns
- **Output**: Transport statistics, optimization recommendations

## 🎯 Real-World Applications

This toolkit is actively used to:

- **Improve Emergency Response Time**: Optimize ambulance positioning and deployment
- **Track Ambulance Effectiveness**: Monitor performance metrics by region and time
- **Plan Efficient Staffing**: Analyze shift patterns and workload distribution
- **Enable Disaster Response**: Offline call tracking during emergencies
- **Predict Service Demand**: ML models for forecasting EMS requirements

## 📊 Key Metrics Analyzed

- **Response Time**: Average time from call to ambulance arrival
- **Coverage Area**: Geographic reach and service area optimization
- **Shift Efficiency**: Staff utilization and workload distribution
- **Transport Patterns**: Primary and secondary transport analysis
- **GPS Accuracy**: Real-time tracking and deployment optimization

## 🏥 Target Users

- **EMS Managers**: Performance monitoring and strategic planning
- **Paramedics**: Operational efficiency and workload analysis
- **Data Analysts**: Healthcare analytics and optimization
- **Emergency Planners**: Disaster response and resource allocation

## 🤝 Contributing

We welcome contributions from the emergency services and healthcare analytics community!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/emergency-optimization`)
3. Commit your changes (`git commit -m 'Add emergency response optimization'`)
4. Push to the branch (`git push origin feature/emergency-optimization`)
5. Open a Pull Request

### Development Guidelines

- Follow healthcare data privacy regulations
- Test with anonymized data only
- Document all analysis methodologies
- Ensure code works with Turkish locale settings

## 📋 Data Requirements

- **GPS Data**: Ambulance location and movement logs
- **Call Records**: Emergency call timestamps and locations
- **Shift Data**: Staff schedules and workload information
- **Geographic Data**: Istanbul district boundaries and road networks

*Note: All data should be anonymized and comply with healthcare privacy regulations.*

## 🔒 Security & Privacy

- All patient data must be anonymized
- Geographic data should not include sensitive locations
- Access controls implemented via unlock mechanisms
- Compliance with Turkish healthcare data protection laws

## 🏆 Team KodlaYaşat

**Focus**: Innovation in Emergency Services (112 EMS, UMKE)  
**Mission**: Leveraging technology and data science to save lives

## 📞 Support

For questions about implementation or collaboration:
- Open an issue in this repository
- Contact the KodlaYaşat team through official channels

## 📜 License

This project is developed for humanitarian purposes to improve emergency medical services. Please ensure compliance with local healthcare regulations when using this code.

## 🙏 Acknowledgments

- Istanbul 112 Ambulance Service
- UMKE (National Medical Rescue Team)
- All paramedics and emergency responders who provide the data that makes this analysis possible
- The healthcare analytics community for their continued support

---

*"In emergency medicine, every second counts. Through data analysis, we make those seconds count even more."*