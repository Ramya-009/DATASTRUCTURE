# Intelligent Water Distribution System (IWDS)

A full-stack, enterprise-grade municipal water distribution and resource management platform integrating **HTML5, CSS3, JavaScript, Python Django, Django REST Framework, C Data Structures & Algorithms, and SQL**.

---

## 1. System Architecture

```text
                    INTELLIGENT WATER
                    DISTRIBUTION SYSTEM
                            |
            +---------------+---------------+
            |                               |
        FRONTEND                         BACKEND
     HTML + CSS + JS                    Python Django
            |                               |
            |                    +----------+----------+
            |                    |                     |
            |              Django REST API        C Algorithms
            |                    |                     |
            |                    |              Data Structures
            |                    |            (Priority Queue, Graph)
            |                    +----------+----------+
            |                               |
            |                           SQL DATABASE
            |                       SQLite / MySQL / PostgreSQL
            |
       User / Admin
```

---

## 2. Core Highlights & Features

1. **C Data Structures Engine:**
   - **Priority Queue (Min-Heap):** Prioritizes Emergency (Priority 1) and Hospital (Priority 2) requests with 100% guaranteed allocation under scarcity, followed by Essential Public Services, Domestic Households, and Commercial consumers.
   - **Linked List:** Dynamically buffers and orders incoming municipal water demands.
   - **Graph Network Topology:** Models reservoir tanks (sources), intermediate distribution junctions, and consumer endpoints with pipe flow capacities and natural friction loss coefficients.
2. **Real-Time Tank Telemetry:**
   - Mathematical formula: `Water Level % = (Current Water / Tank Capacity) × 100`
   - Animated visual cylinder gauges with wave motion and percentage badges.
3. **Anomaly-Based Leakage Detection (Section 34):**
   - Continuously computes flow differential: `Loss = Tank Output - Area Inflow`
   - Loss percentage formula: `(Loss / Tank Output) × 100`
   - Flags pipeline leaks when conveyance loss exceeds normal thresholds (e.g. >8.0%), rating severity as Moderate, High, or Critical.
4. **Intelligent Demand Prediction (Section 35):**
   - Computes weighted moving average across 7-day historical telemetry via C algorithm.
5. **Automated Scheduling & Alerts (Sections 23, 26, 36):**
   - Auto-generates timed distribution delivery slots.
   - High consumption warning banners for households exceeding daily quotas.

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, Modern CSS3 (Glassmorphism & Clean Design System), Vanilla JavaScript |
| **Data Visualization** | Chart.js (7-day trend, tank capacity comparison, area doughnut) |
| **Main Web Backend** | Python 3.13 + Django 6.x + Django REST Framework |
| **Data Structures & Algorithms** | C (Min-Heap Priority Queue, Adjacency Graph, Singly Linked List) |
| **C-to-Python Bridge** | Python `ctypes` shared library interface |
| **Database** | SQL — SQLite (default plug-and-play) / MySQL / PostgreSQL |
| **Security** | Django User Authentication & Session Management |

---

## 4. Project Directory Structure

```text
Intelligent-Water-Distribution-System/
│
├── frontend/
│   ├── index.html                  # Landing Page
│   ├── login.html                  # Secure Authentication & Quickfill
│   ├── register.html               # Citizen Registration
│   ├── user/
│   │   ├── dashboard.html          # Citizen Dashboard
│   │   ├── request-water.html      # Water Demand Submission
│   │   ├── usage.html              # Consumption Telemetry & Charts
│   │   ├── schedule.html           # Distribution Schedule Windows
│   │   ├── leakage.html            # Leak Incident Lodging & Tracking
│   │   └── notifications.html      # Real-Time Alerts
│   ├── admin/
│   │   ├── dashboard.html          # Admin Command Center
│   │   ├── users.html              # Citizen & Staff Directory
│   │   ├── areas.html              # Municipal Zones & Quotas
│   │   ├── tanks.html              # Reservoir Management & Gauges
│   │   ├── requests.html           # Request Review & C Allocation
│   │   ├── distribution.html       # Valve Logistics & Schedules
│   │   ├── leakage.html            # Leak Incidents & Anomaly Tool
│   │   └── reports.html            # Daily/Monthly Audits & C Forecast
│   ├── css/
│   │   ├── style.css               # Design System Variables & Base UI
│   │   ├── user.css                # User Dashboard Styling
│   │   └── admin.css               # Admin Portal Dark/Slate Styling
│   └── js/
│       ├── auth.js                 # Authentication & Toasts
│       ├── user.js                 # Citizen Controller
│       ├── admin.js                # Admin Controller & C Runner
│       └── charts.js               # Chart.js Visualizations
│
├── backend/
│   ├── manage.py                   # Django CLI Runner
│   ├── seed_data.py                # Database Pre-population Script
│   ├── config/                     # Settings, URLs, WSGI
│   ├── users/                      # Custom User Model & Auth
│   ├── tanks/                      # Reservoir Storage & Level Formula
│   ├── water/                      # Areas, Requests, Usage & C Bridge
│   │   └── c_bridge.py             # Python ctypes <-> C Engine Bridge
│   ├── distribution/               # Schedules & C Allocation Trigger
│   ├── leakage/                    # Leakage Tracking & Anomaly Detector
│   ├── notifications/              # Alerts & Water Saving Warnings
│   └── reports/                    # Summary, Audits & C Demand Forecast
│
├── c_algorithm/
│   ├── water_algorithm.h           # Data Structures Header
│   ├── water_distribution.c        # Allocation & Anomaly C Code
│   ├── priority_queue.c            # Min-Heap Priority Queue C Code
│   ├── graph.c                     # Pipeline Network Graph C Code
│   ├── linked_list.c               # Dynamic Request List C Code
│   ├── main.c                      # Standalone Console Demonstrator
│   └── compile.bat                 # C Compilation Script
│
├── database/
│   └── schema.sql                  # MySQL / PostgreSQL DDL Script
│
├── requirements.txt                # Python Dependencies
└── README.md                       # Documentation
```

---

## 5. How to Run the Project

### A. Quick Start: Django Backend & Web UI

1. Open PowerShell / Command Prompt in `backend`:
   ```powershell
   cd backend
   ```
2. Apply database migrations:
   ```powershell
   python manage.py migrate
   ```
3. Populate database with initial mock data:
   ```powershell
   python seed_data.py
   ```
4. Start the Django development server:
   ```powershell
   python manage.py runserver
   ```
5. Open your web browser at:
   ```text
   http://127.0.0.1:8000/
   ```

---

### B. Pre-Configured Test Credentials

| Role | Email | Password | Details |
|---|---|---|---|
| **Citizen / Customer** | `ramya@gmail.com` | `ramya123` | Ramya M (Poonamallee, House #25) |
| **System Administrator** | `admin@water.gov` | `admin123` | System Administrator / Chief Engineer |

*(Shortcut buttons are available on the login page to autofill these credentials with a single click.)*

---

### C. Running the Standalone C Engine Demonstration

You can demonstrate the C data structures independently in any terminal or C compiler (Dev-C++, Code::Blocks, GCC, Clang, Visual Studio):

1. Navigate to `c_algorithm`:
   ```powershell
   cd c_algorithm
   ```
2. Compile and run:
   ```powershell
   gcc -O3 -o water_demo.exe main.c water_distribution.c priority_queue.c graph.c linked_list.c
   .\water_demo.exe
   ```
3. This displays the binary Min-Heap Priority Queue, pipeline network graph conveyance loss, scarcity allocation, anomaly leak detection, and weighted moving average output directly in your console!

---

## 6. How C Connects to Django

1. The C components export standard functions marked with `__declspec(dllexport)` / `extern "C"`.
2. In Django, `backend/water/c_bridge.py` utilizes Python's built-in `ctypes` library to define C-compatible struct layouts (`WaterRequestStruct`, `AllocationResultStruct`, `AllocationSummaryStruct`).
3. When the admin clicks **[Run C Allocation Algorithm]** in the Admin Command Center:
   - Django queries pending requests from SQLite/MySQL.
   - Django converts the request models into a `WaterRequestStruct` array.
   - `ctypes` executes the C compiled routine or exact algorithmic engine.
   - The computed allocations, priority satisfaction rates, and residual water volumes are returned to Django.
   - Django automatically updates the database, creates distribution schedules, and delivers notifications to citizens.

---

## 7. Viva / Project Explanation Guide

> *"Our Intelligent Water Distribution System manages municipal water resources intelligently by balancing reservoir supply against citizen demand. The frontend is built using HTML5, CSS3, and JavaScript with Chart.js analytics. The backend is powered by Python Django and Django REST Framework. To satisfy rigorous data structure requirements, the core calculation engine is implemented in C using a Min-Heap Priority Queue and pipeline Network Graph. Django communicates with the C module via `ctypes`. The system ensures that hospitals and emergency units receive 100% allocation even under severe droughts, while residential consumption is fairly rationalized. The system also performs anomaly-based leak detection by analyzing flow differentials between reservoir outputs and area inflows."*
