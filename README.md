# Istanbul Analysis

## Overview

This repository contains a collection of Python scripts and Jupyter notebooks for analyzing emergency medical response data in Istanbul. It includes tools for tracking ambulance movements, analyzing response times, visualizing case distributions, and automating various data-related processes.

## Table of Contents

- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Detailed File Descriptions](#detailed-file-descriptions)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

```
istanbul_analysis-main/
│── GPS Data Processor/
│   └── GPS_based_reactions/gps_reactions.py
│── ambulance_troubles/
│   └── monthly_district_reach_times/monthly_district_reach_times.py
│── case_tracking/
│   ├── case_tracker/case_tracker_automated.py
│   ├── daily_hourly_case_counts/hourly_case_counts.py
│   ├── daily_hourly_case_counts/hourly_case_counts_2.py
│   ├── sea_cases_drowns/sea_cases.py
│── champions_league/
│   ├── visualize_champions.py
│── data_visualisation/
│   ├── hourly_case_intensity.py
│── departments/
│   ├── Electronic Data System/hbys_analiz.py
│   ├── Electronic Data System/Gui Program/hbys_gui.py
│   ├── Electronic Data System/Gui Program/hbys_gui.pyw
│── google_sheets_scripts/
│   └── convert_multiple_excel_files_into_google_sheets/
│── late_exits/
│── patient_types/
│── staff_troubles/
│── ambulance_working_distances.ipynb
│── extra_shift_analysis.ipynb
│── tensorflow_workout.ipynb
│── .gitignore
│── README.md (not present)
```

## Installation

To use this repository, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/kayamui/istanbul_analysis.git
   ```
2. Navigate into the project folder:
   ```bash
   cd istanbul_analysis-main
   ```
3. Install dependencies (if applicable):
   ```bash
   pip install -r requirements.txt
   ```
   *Ensure that a ******`requirements.txt`****** file exists in the repository listing required Python libraries.*

## Usage

Each script serves a specific purpose, from analyzing ambulance response times to visualizing case distributions. To run a script, use:

```bash
python script_name.py
```

Replace `script_name.py` with the actual file you wish to execute.

For Jupyter notebooks, launch Jupyter and open the `.ipynb` file:

```bash
jupyter notebook
```

## Detailed File Descriptions

### **1. GPS Data Processor**

- **`gps_reactions.py`**: Processes ambulance GPS data to analyze reactions and movements.

### **2. Ambulance Troubles**

- **`monthly_district_reach_times.py`**: Evaluates ambulance reach times in different districts monthly.

### **3. Case Tracking**

- **`case_tracker_automated.py`**: Automates emergency case tracking.
- **`hourly_case_counts.py / hourly_case_counts_2.py`**: Analyzes and reports hourly emergency case counts.
- **`sea_cases.py`**: Investigates water-related emergencies, such as drowning cases.

### **4. Champions League**

- **`visualize_champions.py`**: Visualizes high-performing ambulance crews and response teams.

### **5. Data Visualization**

- **`hourly_case_intensity.py`**: Creates visualizations for emergency case intensity per hour.

### **6. Departments - Electronic Data System**

- **`hbys_analiz.py`**: Analyzes hospital-based information systems.
- **`hbys_gui.py / hbys_gui.pyw`**: GUI applications for interacting with hospital information systems.

### **7. Other Notable Files**

- **`ambulance_working_distances.ipynb`**: Investigates ambulance travel distances.
- **`extra_shift_analysis.ipynb`**: Analyzes extra work shifts among emergency personnel.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature_branch`).
3. Commit changes (`git commit -m "Description"`).
4. Push to the branch (`git push origin feature_branch`).
5. Open a pull request for review.

## License

This project is licensed under the MIT License.

