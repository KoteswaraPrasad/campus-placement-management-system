# Campus Placement Management System

A full-stack, enterprise-grade **Campus Placement Management System** built with **Python 3**, **Django**, **Bootstrap 5**, and **Chart.js** as a college academic project.

The system connects students, university placement officers, and corporate recruiters into a unified digital portal. It automates candidate eligibility checking, manages company participation and job openings, tracks multi-stage application pipelines, provides real-time notifications, and renders interactive recruitment analytics with CSV report generation.

---

## 🌟 Key Highlights & Features

### 🎓 1. Student Portal
- **Secure Registration & Authentication**: Student registration with university registration number, engineering department, current semester, CGPA, backlogs count, phone number, technical skills, and resume upload.
- **Profile Dossier**: Real-time profile completion meter, editable academic/personal records, and resume replacement.
- **Automated Eligibility Engine**: When browsing job postings, the server evaluates student criteria (minimum CGPA, backlog thresholds, eligible branches, and semester limits) and displays clear eligibility badges or explicit mismatch rationales.
- **Job Applications**: One-click application with registered profile and snapshot resume; prevents duplicate applications and submissions after deadlines.
- **Application Tracking & Timeline**: Multi-stage status pipeline (`Applied`, `Under Review`, `Shortlisted`, `Interview Scheduled`, `Selected`, `Rejected`, `Withdrawn`) with full status history and officer feedback notes.
- **Withdrawal**: Students can withdraw active applications in early stages (`Applied` / `Under Review`).
- **Announcements & Notifications**: View drive announcements, schedule updates, and receive instant in-app alerts on status transitions.

### 🏢 2. Placement Officer Portal
- **Executive Analytics Dashboard**: Real database metrics showing total registered students, active partner companies, live job drives, total applications, placed candidate counts, and institutional placement rate.
- **Chart.js Visualizations**:
  - *Applications by Status* (Doughnut chart)
  - *Students Placed by Engineering Department* (Bar chart)
  - *Job Openings by Corporate Partner* (Horizontal Bar chart)
- **Company Management**: Add, update, inspect, and toggle active/inactive status for participating corporate organizations.
- **Job Drive Management**: Create, edit, publish, close, and archive job postings with fine-grained eligibility rules (CGPA, backlog cap, branch multi-selection, semester filters, salary/CTC, opening/deadline dates).
- **Application Review & Decisioning**: Filter applications by company, job, status, or department. Screen applicant profiles, download candidate resumes securely, update statuses, record interviewer feedback, and trigger student notifications.
- **Student Database**: Searchable and filterable student directory with CGPA and backlog thresholds.
- **Placement Notices**: Publish pinned or categorized announcements (`Placement Drive`, `Interview Schedule`, `New Job Opening`, `Deadline Alert`, `General`).
- **Institutional Reporting & CSV Export**:
  - Export complete applications list to CSV.
  - Export placed candidates list to CSV.
  - Export department-wise placement summary with placement percentages.

### 🛡️ 3. Security & Architecture
- **Strict Backend Role-Based Access Control (RBAC)**: Custom decorators (`@student_required`, `@officer_required`) ensure students cannot access administrative URLs, and officers cannot spoof student submissions.
- **Protected File Access**: Uploaded student resumes are stored securely and served only to the student owner or authorized placement officers.
- **Safe Database Interactions**: Built exclusively with Django ORM, protecting against SQL injection, CSRF attacks, and session hijacking.
- **Unique Constraints**: Database-level unique constraint on `(job, student)` prevents duplicate applications.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **Backend Framework** | Python 3.13 / Django 6.x (or 5.x) |
| **Database** | SQLite3 (`db.sqlite3`) |
| **Frontend UI** | HTML5, CSS3, JavaScript (ES6) |
| **CSS Framework** | Bootstrap 5.3.3 |
| **Icons** | Bootstrap Icons 1.11.3 |
| **Data Visualization** | Chart.js |
| **Authentication** | Django Auth System (PBKDF2 Password Hashing) |

---

## 📂 Project Structure

```text
campus_placement/
├── manage.py                     # Django management script
├── requirements.txt              # Project dependencies
├── README.md                     # Documentation
├── config/                       # Project configuration
│   ├── settings.py               # Django settings, apps, templates, media
│   ├── urls.py                   # Central routing
│   ├── wsgi.py                   # WSGI deployment gateway
│   └── asgi.py                   # ASGI gateway
├── accounts/                     # Authentication & Custom User model
│   ├── models.py                 # User model with role choices
│   ├── decorators.py             # Role-based access control (@student_required, @officer_required)
│   ├── forms.py                  # StudentRegistrationForm, LoginForm
│   ├── views.py                  # Register, login, logout, password change
│   ├── urls.py                   # Auth endpoints
│   └── tests.py                  # Auth & RBAC test suite
├── students/                     # Student Profiles & Academic Records
│   ├── models.py                 # StudentProfile model
│   ├── validators.py             # Resume file type & size validators
│   ├── forms.py                  # StudentProfileForm
│   ├── views.py                  # Profile views & secure resume download
│   └── urls.py                   # Student profile routes
├── companies/                    # Corporate Recruiting Partners
│   ├── models.py                 # Company model
│   ├── forms.py                  # CompanyForm
│   ├── views.py                  # Company CRUD & activation toggle
│   └── urls.py                   # Company endpoints
├── jobs/                         # Job Drives & Eligibility Rules
│   ├── models.py                 # Job model with server-side check_eligibility()
│   ├── forms.py                  # JobForm with branch multi-selection
│   ├── views.py                  # Job listings, details, status toggling
│   ├── urls.py                   # Job endpoints
│   └── tests.py                  # Automated eligibility testing suite
├── applications/                 # Application Pipeline & Audit History
│   ├── models.py                 # Application & ApplicationStatusHistory
│   ├── forms.py                  # ApplicationApplyForm, StatusUpdateForm
│   ├── views.py                  # Job apply, history, officer decisions
│   ├── urls.py                   # Application routes
│   └── tests.py                  # Application workflow & duplicate prevention tests
├── notifications/                # Notices & User Alerts
│   ├── models.py                 # Announcement & Notification models
│   ├── context_processors.py     # Unread notification count for navbar badge
│   ├── forms.py                  # AnnouncementForm
│   ├── views.py                  # Announcement CRUD & notifications inbox
│   └── urls.py                   # Notification endpoints
├── dashboard/                    # Dashboards, Reports & Seed Command
│   ├── views.py                  # Student dashboard, Officer analytics, CSV exports
│   ├── urls.py                   # Dashboard routes
│   ├── management/commands/      # Custom commands
│   │   └── seed_data.py          # Populates realistic demo accounts & data
│   └── tests.py                  # Analytics & placement rate calculation tests
├── templates/                    # Django HTML Templates
│   ├── base.html                 # Master layout (Bootstrap 5, Chart.js, alerts)
│   ├── navbar.html               # Sticky topbar with notification badge dropdown
│   ├── sidebar.html              # Dynamic role-tailored sidebar
│   ├── accounts/                 # Login, register, change password
│   ├── dashboard/                # Landing, student & officer dashboards, reports
│   ├── students/                 # Profile view, edit, officer directory
│   ├── companies/                # Company grid, profile, creation form
│   ├── jobs/                     # Job listings, detail with eligibility box, form
│   ├── applications/             # Apply confirmation, student list, officer table
│   └── notifications/            # Announcements list, form, notifications list
├── static/                       # Static assets
│   ├── css/custom.css            # University portal design styles
│   └── js/main.js                # Interactive sidebar & alert handling
└── media/                        # Secure local media storage
    └── resumes/                  # Student uploaded resumes
```

---

## 🚀 Setup & Installation Guide (Windows PowerShell)

Follow these steps to set up and run the system locally on Windows:

### Step 1: Open PowerShell and Navigate to the Project
```powershell
cd C:\Users\Koteswara_prasad\Downloads\portfolio\campus_placement
```

### Step 2: Set Up Virtual Environment (Recommended)
```powershell
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```
*(If script execution is restricted in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run Database Migrations
Initialize the SQLite database schema:
```powershell
python manage.py migrate
```

### Step 5: Populate Realistic Sample Data (Instant Demo)
Run the built-in seeding command to populate demo users, companies, job drives, applications, announcements, and resumes:
```powershell
python manage.py seed_data
```

### Step 6: Create an Administrator Superuser (Optional)
If you wish to create a custom superuser manually:
```powershell
python manage.py createsuperuser
```

### Step 7: Launch the Development Server
```powershell
python manage.py runserver
```

Open your browser and navigate to:
👉 **http://127.0.0.1:8000/**

---

## 🔑 Pre-Configured Demo Accounts

After running `python manage.py seed_data`, you can immediately test the portal with these ready-to-use accounts:

| Role | Username | Password | Email | Highlights |
|---|---|---|---|---|
| **Placement Officer** | `officer` | `officer123` | `placement.officer@university.edu` | Full placement management, analytics charts, status decisioning, CSV exports. |
| **Student (Eligible & Placed)** | `student1` | `student123` | `aarav.patel@student.edu` | CSE (CGPA 9.15, 0 backlogs). Placed at Google India. |
| **Student (Placed)** | `student2` | `student123` | `priya.nair@student.edu` | IT (CGPA 8.60, 0 backlogs). Placed at Microsoft. |
| **Student (1 Backlog)** | `student3` | `student123` | `rohan.verma@student.edu` | ECE (CGPA 7.40, 1 backlog). Applied to TCS Digital. |
| **Student (AI / DS)** | `student4` | `student123` | `ananya.deshmukh@student.edu` | AIDS (CGPA 8.90, 0 backlogs). Placed at TCS Research. |
| **Student (Mechanical)** | `student5` | `student123` | `vikram.reddy@student.edu` | MECH (CGPA 6.85, 0 backlogs). Demonstrates branch-based eligibility rules. |
| **Administrator** | `admin` | `admin123` | `admin@university.edu` | Django backend administration (`http://127.0.0.1:8000/admin/`). |

---

## 🧪 Running Automated Unit Tests

A comprehensive suite of 20 unit tests validates student authentication, role restrictions, eligibility logic, deadline enforcement, status history logging, and placement analytics.

Run all tests from the `campus_placement` directory:
```powershell
python manage.py test accounts jobs applications dashboard
```

Expected output:
```text
Creating test database for alias 'default'...
....................
----------------------------------------------------------------------
Ran 20 tests in 10-15s

OK
Destroying test database for alias 'default'...
```

---

## 📊 Institutional Reporting & Data Export

Placement Officers can navigate to **Reports & Analytics** (`/officer/reports/`) to view live tables and export real database data into standard CSV spreadsheets:
1. **Export Applications CSV**: Candidate name, registration number, email, department, semester, CGPA, backlogs, applied position, company, CTC, current status, and timestamp.
2. **Export Placed Students CSV**: Detailed roster of candidates who received verified corporate offers.
3. **Export Department Summary CSV**: Institutional department-wise breakdown comparing registered students against placed students with calculated placement percentages.

---

## 📜 Academic Project Certification

This project was developed strictly adhering to academic software engineering principles, modular Django design, normalized database relationships, and strict server-side validation.
