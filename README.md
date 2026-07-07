# EstateOps — Multi-Project ERP/CRM System (Django)

Welcome to **EstateOps**, a premium, multi-tenant ERP & CRM system built with Python/Django for construction project management, stock inventory control, site visitors monitoring, attendance logging, and client leads tracking.

The application features a modern, responsive design system with a deep navy sidebar, orange accents, clean UI cards, custom SweetAlert2 popup alerts/confirmations, and a robust role-based access control matrix.

---

## 💻 Prerequisites & Requirements

Before starting the setup on another PC, make sure you have the following installed:
1. **Python 3.10+** (Recommended: Python 3.12.x)
   * *Make sure to check the box "Add Python to PATH" during installation on Windows.*
2. **pip** (Python package installer, comes bundled with Python)
3. **virtualenv** (Optional, but highly recommended for isolating dependencies)
4. **Git** (Optional, to clone the project files)

---

## ⚡ Quick Windows Startup (No Commands Required)
If you are on Windows, you can automate the entire setup:
1. Extract the project ZIP file.
2. Double-click the **`run_project.bat`** file in the root folder.
* *This script automatically checks for Python, creates a virtual environment, installs dependencies, runs database migrations, seeds demonstration accounts, opens your web browser to `http://127.0.0.1:8000/`, and starts the development server!*

---

## 🛠️ Step-by-Step Manual Installation Guide

Follow these steps to set up the project on any Windows, macOS, or Linux machine:

### Step 1: Clone or Copy Project Files
Copy the project folder onto your computer, or clone it using Git:
```bash
git clone <repository_url>
cd estateops
```

### Step 2: Set Up Python Virtual Environment
Creating a virtual environment ensures that the packages do not conflict with other Python projects on your machine.
* **On Windows (Command Prompt / PowerShell):**
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
* **On macOS / Linux:**
  ```bash
  python -m venv venv
  source venv/bin/activate
  ```

### Step 3: Install Required Dependencies
With the virtual environment active, install all packages listed in the requirements file:
```bash
pip install -r requirements.txt
```

### Step 4: Perform Database Migrations
Initialize the SQLite database structure and generate the tables:
```bash
python manage.py migrate
```

### Step 5: Seed Demonstration Data
Populate the database with pre-configured construction projects, materials, leads, and demo user accounts for testing:
```bash
python manage.py seed_demo
```

### Step 6: Launch Development Server
Start the local development server:
```bash
python manage.py runserver
```

Now, open your web browser and navigate to: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**
You will be automatically redirected to the Login page.

---

## 🔑 Demo User Credentials (Created by `seed_demo`)

Use the following pre-configured credentials to log in and test different project workspaces and access roles:

### 1. Global / Super Admin Access
* **Role**: Can manage projects (create/edit/delete), view all dashboards, register users, and access all project contexts.
* **Username**: `admin`
* **Password**: `admin123`

---

### 2. Project Workspace 1: Estate Ops Ahmedabad (ID: 7)

| Username | Password | Role | Permissions |
| :--- | :--- | :--- | :--- |
| **`amd_admin`** | `admin123` | **Project Admin** | Full access to Ahmedabad dashboard, employees, logs, leads, assets, and users. |
| **`amd_hr`** | `hr123` | **HR Manager** | Manage Ahmedabad employees, salary records, check-in sheets, and leave approvals. |
| **`amd_sec`** | `sec123` | **Security Guard** | Log visitor check-ins/check-outs and record daily worker attendance. |
| **`amd_emp`** | `emp123` | **Employee** | Read-only view of Ahmedabad visitor lists, attendance history, and request leaves. |

---

### 3. Project Workspace 2: Estate Ops Rajkot (ID: 8)

| Username | Password | Role | Permissions |
| :--- | :--- | :--- | :--- |
| **`rjt_admin`** | `admin123` | **Project Admin** | Full access to Rajkot dashboard, inventory, leads, and team rosters. |
| **`rjt_hr`** | `hr123` | **HR Manager** | Manage Rajkot employees, salary schedules, and leaves. |

*Note: Accessing Ahmedabad URLs while logged in as a Rajkot user (or vice-versa) will trigger a customized **403 Access Denied** screen detailing your active session context and providing a switch user link.*

---

## 🏗️ Core Features & Code Modules

* **`accounts`**: Manages custom user profiles, multi-project scoping assignments, and authentication mechanisms.
* **`projects`**: Handles workspace-level tasks:
  * **Employee Profiles**: Photo ID card generation, salary tracking, and active rosters.
  * **Attendance Tracker**: Split layout for supervisors/security to log attendance; read-only full-screen log dashboard for Employees.
  * **Visitor Log**: Real-time checklist of site visitors with quick checkout triggers.
  * **Leave Manager**: Request portal for Employees and approval workflow for HR.
  * **Progress Updates**: Timeline tracking showing construction stage percentages, logs, and site photos.
* **`leads`**: CRM board tracking potential clients, client status, follow-up logs, and automated project context linking.
* **`stock`**: Daily material inventory tracking tool. Restricts raw item creation/deletion to Admins, allows logging daily material consumption (quantity validation guards against over-consumption).
* **`dashboard`**: Global analytics landing screen showing construction stages, client charts, and active projects stats.

---

## 🎨 Design & Customizations

* **Navy & Orange Accents**: Styled using custom CSS parameters (`static/css/style.css`) matching a premium modern layout.
* **SweetAlert2 Alerts**: All success/error notices and crucial action confirmations (e.g. deleting an asset or employee) have been upgraded to SweetAlert2 overlay alerts.
* **Responsive Layouts**: Optimised sidebar behavior and grids for seamless browsing on mobile, tablet, and desktop viewports.
