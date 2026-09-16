# EquipShare — Peer-to-Peer Equipment Rental & Sharing Platform

[![Vue 3](https://img.shields.io/badge/Frontend-Vue%203-42b883?logo=vuedotjs)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Build-Vite%205-646cff?logo=vite)](https://vitejs.dev/)
[![Pinia](https://img.shields.io/badge/State-Pinia-ffd859)](https://pinia.vuejs.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask%203.0-000000?logo=flask)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-d71f00)](https://www.sqlalchemy.org/)
[![Flask-Security](https://img.shields.io/badge/Auth-Flask--Security--Too-29b6f6)](https://flask-security-too.readthedocs.io/)
[![Celery](https://img.shields.io/badge/Jobs-Celery%205.4-37814a?logo=celery)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/Broker-Redis-dc382d?logo=redis)](https://redis.io/)

**EquipShare** is a web-based platform where users can **list equipment they own and make it available for temporary rental**, while others can search, request, reserve, return, and review items.

The platform is designed for peer-to-peer sharing in:
* **Universities & Student Communities** (lab sensors, cameras, laptops, test equipment)
* **Makerspaces & Creator Hubs** (drills, soldering stations, 3D printing tools)
* **Photography & Videography Collectives** (DSLRs, lenses, lighting, gimbals)
* **Local Neighborhoods & Hobby Groups** (camping gear, sound systems, projectors)

Instead of everyone purchasing expensive hardware individually, EquipShare enables resource pooling, reduces electronic waste, and allows owners to monetize idle equipment.

---

## 1. Core Workflow

The platform provides a guided lifecycle:

```text
Browse / Search Gear
       ↓
Submit Booking Request (Start Date, End Date, Note)
       ↓
Owner Review (Approve or Decline)
       ↓
Active Rental (Equipment status locked to 'rented')
       ↓
Return Confirmation (Availability restored to 'available')
       ↓
Community Review (1–5 Star Rating & Verified Review)
```

---

## 2. User Roles & Capabilities

### 👤 Regular Member (`USER`)
* **Authentication**: Register with email/username, login with secure token persistence, manage profile credentials.
* **Browse & Search**: Real-time keyword search (name, description, location), category filter chips, condition filtering (New, Like New, Excellent, Good, Fair), and price sorting.
* **Listing Management**: List owned equipment with daily rates, category, condition, location, and photos/specs. Update details, edit prices, or remove listings in **My Equipment**.
* **Rental Requests**:
  - Request any available gear for specific calendar dates.
  - View live rental duration and estimated cost breakdown.
  - Cancel pending inquiries anytime.
  - Review incoming requests for own gear with **Approve** and **Decline** controls.
* **Active Rental Tracking**: Monitor currently rented gear, view counterpart contact info, and execute one-click return confirmations in **My Rentals**.
* **Reviews & Ratings**: Submit 1 to 5 star ratings and feedback for returned rentals. Equipment listings display verified average ratings.
* **Notifications**: Receive instant alerts on request approvals, incoming bookings, return confirmations, and reminders.

### 🛡️ Administrator (`ADMIN`)
* **Platform Metrics Dashboard**: Real-time statistics on total registered users, listed gear, active rentals, completed rentals, and total platform volume.
* **Category Management**: Create new equipment categories, monitor category equipment counts, and safely delete categories without orphaning equipment.
* **User Moderation**: View all registered accounts and activate or deactivate (ban) accounts.
* **Listing Moderation**: Inspect the global equipment catalog and remove inappropriate or reported listings.
* **Safety & Reports Queue**: Review member reports filed against equipment or users and resolve issues.
* **Scheduled Task Automation**: One-click execution of automated maintenance routines (return reminders and request expiration) directly from the admin panel.

---

## 3. Technology Stack & Architecture

| Layer | Technology | Details |
|---|---|---|
| **Frontend Framework** | **Vue.js 3** (Composition API, `<script setup>`) | Modular Single-Page Application (SPA) |
| **Frontend Tooling** | **Vite 5** | Hot Module Replacement (HMR) & production bundler |
| **State Management** | **Pinia 2** | Reactive auth store, token persistence, and notification counters |
| **Client Routing** | **Vue Router 4** | Protected routes, guest redirects, and role-based guards |
| **HTTP Client** | **Axios** | Authenticated REST requests with `Authentication-Token` interceptors |
| **Backend API** | **Flask 3.0** | RESTful modular Blueprints architecture |
| **ORM & Database** | **SQLAlchemy 3.1** / **SQLite** | Relational data models with foreign key constraints |
| **Authentication** | **Flask-Security-Too 5.5** | Secure token generation, PBKDF2-SHA512 password hashing, role management |
| **Reverse Proxy** | **Vite Proxy** | Proxies `/api` to backend `http://127.0.0.1:5000` (eliminates CORS and IPv6 issues) |
| **Background Automation** | **Celery 5.4 + Redis** | Scheduled return reminders and reservation expiration |

---

## 4. Application Walkthrough & Key Pages

### 🏠 Home Page (`/`)
* Hero banner with instant keyword search bar.
* Popular category chips with live equipment counters.
* Step-by-step visual workflow guide ("How EquipShare Works").
* Featured available equipment grid with condition badges, locations, and daily rates.
* Call-to-action banner for gear owners.

### 🔍 Equipment Catalog (`/equipment`)
* Real-time debounced keyword search across title, description, and city.
* Filters for Category, Condition, Availability status (`Available`, `All`, `Rented`), and Sort (`Newest`, `Price: Low to High`, `Price: High to Low`, `Name`).
* Responsive grid of equipment cards with rating badges, owner handles, location tags, and direct booking links.

### 📦 Equipment Details & Booking (`/equipment/:id`)
* Comprehensive specifications, condition indicator, and owner details.
* **Interactive Booking Calendar**: Pick start date and end date with live rental day calculations and total price estimation in ₹.
* Optional message box for pickup coordination.
* Direct protection against self-renting (owners receive a management shortcut instead).
* Verified community review list with star distributions.
* "Report Listing" modal for community safety.

### ➕ Add Equipment (`/add-equipment`)
* Clean form with category dropdown, title, condition selector, daily rate in ₹, pickup location, and description.
* Input validation and redirection to the newly created listing.

### 📋 My Equipment Listings (`/my-equipment`)
* Inventory overview showing active items, daily rates, and pending request alerts.
* Interactive modal to edit titles, daily rates, conditions, locations, and status (`Available`, `Unavailable`, `Rented`, `Maintenance`).
* Confirmation dialog for listing deletion.

### 📬 Rental Requests Inbox (`/rental-requests`)
* **Received Requests Tab**: Review incoming inquiries for your equipment, view renter profile, requested dates, calculated earnings, note, and click **Approve & Reserve** or **Decline**.
* **Sent Inquiries Tab**: Track status of your booking requests (`PENDING`, `APPROVED`, `REJECTED`, `CANCELLED`) with option to cancel pending requests.

### 🤝 My Rentals (`/my-rentals`)
* **Active Rentals Tab**: View gear currently in your possession or lent out, dates, and click **Mark as Returned**.
* **Past & Returned Tab**: View finished rental history. Renters can click **Write Review** to open the 5-star rating modal with comments.

### 🔔 Notifications Center (`/notifications`)
* Real-time notification feed for booking approvals, new requests, returns, reviews, and due date reminders.
* Visual unread highlights, "Mark All as Read" button, and individual delete controls.

### 👤 Profile & Security (`/profile`)
* Profile overview with member statistics (items listed, rentals taken, rentals lent).
* Credential settings to update username or change password.

### 🛡️ Admin Dashboard (`/admin`)
* Accessible only to users with the `ADMIN` role.
* Statistics metrics: registered users, total listings, active rentals, total volume.
* **Categories Management**: Add new categories, inspect equipment counts, delete categories.
* **User Moderation**: Toggle active status (activate/deactivate users).
* **Equipment Moderation**: Delete inappropriate listings.
* **Safety Reports**: Review and resolve user-submitted flags.
* **Maintenance Automation**: Trigger scheduled reminder and expiration tasks on demand.

---

## 5. Database Design & Entities

EquipShare uses 10 normalized relational tables in SQLite (`equipshare.db`):

```text
User ────────┬───────< roles_users >─────── Role
             │
             ├───────< Equipment >───────── Category
             │            │
             │            ├───< RentalRequest
             │            │          │
             │            │          └───< Rental ───< Review
             │            │                  │
             ├────────────┴──────────────────┤
             │                               │
             ├───────< Notification          │
             │                               │
             └───────< Report >──────────────┘
```

1. **`user`**: `id`, `email`, `username`, `password`, `active`, `fs_uniquifier`, `created_at`
2. **`role`**: `id`, `name` (`USER`, `ADMIN`), `description`
3. **`category`**: `id`, `name`, `description`, `created_at`
4. **`equipment`**: `id`, `owner_id`, `category_id`, `name`, `description`, `condition`, `price_per_day`, `location`, `availability_status`, `created_at`
5. **`rental_request`**: `id`, `equipment_id`, `renter_id`, `start_date`, `end_date`, `message`, `status` (`PENDING`, `APPROVED`, `REJECTED`, `CANCELLED`, `EXPIRED`), `created_at`
6. **`rental`**: `id`, `request_id`, `equipment_id`, `owner_id`, `renter_id`, `start_date`, `end_date`, `total_amount`, `status` (`ACTIVE`, `RETURNED`), `returned_at`
7. **`review`**: `id`, `rental_id`, `reviewer_id`, `rating` (1–5), `comment`, `created_at`
8. **`notification`**: `id`, `user_id`, `message`, `read`, `created_at`
9. **`report`**: `id`, `reporter_id`, `reported_user_id`, `equipment_id`, `reason`, `status` (`OPEN`, `RESOLVED`), `created_at`
10. **`roles_users`**: association table connecting `user.id` and `role.id`

---

## 6. REST API Reference

All API routes are served under the `/api` prefix:

### 🔐 Authentication (`/api/auth`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register` | Register new user; returns auth token & user object | No |
| `POST` | `/api/auth/login` | Log in with email & password; returns token | No |
| `POST` | `/api/auth/logout` | Log out session | Yes |
| `GET` | `/api/auth/me` | Get current authenticated user profile & stats | Yes |
| `PUT` | `/api/auth/profile` | Update username or change password | Yes |

### 📷 Equipment (`/api/equipment`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/equipment` | Search & filter catalog (`search`, `category_id`, `condition`, `status`, `sort`) | No |
| `GET` | `/api/equipment/my` | Get current user's owned equipment with request counts | Yes |
| `GET` | `/api/equipment/<id>` | Full equipment details, owner info, reviews, average rating | No |
| `POST` | `/api/equipment` | List new equipment | Yes |
| `PUT` | `/api/equipment/<id>` | Update equipment listing (owner or admin) | Yes |
| `DELETE` | `/api/equipment/<id>` | Delete listing (owner or admin) | Yes |

### 📂 Categories (`/api/categories`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/categories` | List all categories with equipment count | No |
| `POST` | `/api/categories` | Create new category (Admin only) | Admin |
| `DELETE` | `/api/categories/<id>` | Delete category and uncategorize its items (Admin only) | Admin |

### 🤝 Rentals & Inquiries (`/api/rentals`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/rentals/request` | Submit booking request for date range | Yes |
| `GET` | `/api/rentals/my-requests` | View requests sent by the logged-in user | Yes |
| `PUT` | `/api/rentals/requests/<id>/cancel` | Cancel a pending booking request | Yes |
| `GET` | `/api/rentals/received` | View incoming booking requests for user's gear | Yes |
| `PUT` | `/api/rentals/<id>/approve` | Approve request: sets equipment to `rented`, creates `ACTIVE` rental | Yes |
| `PUT` | `/api/rentals/<id>/reject` | Decline request: sets status to `REJECTED` | Yes |
| `GET` | `/api/rentals/my-rentals` | Get active and past rentals where user is renter or owner | Yes |
| `PUT` | `/api/rentals/<id>/return` | Mark rental as `RETURNED`, restores gear to `available` | Yes |

### ⭐ Reviews (`/api/equipment/<id>/reviews`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/equipment/<id>/reviews` | List all verified reviews for an equipment item | No |
| `POST` | `/api/equipment/<id>/reviews` | Submit 1–5 star rating and comment for completed rental | Yes |

### 🔔 Notifications (`/api/notifications`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/notifications` | Get user notifications and unread counter | Yes |
| `PUT` | `/api/notifications/<id>/read` | Mark individual notification as read | Yes |
| `PUT` | `/api/notifications/read-all` | Mark all notifications as read | Yes |
| `DELETE` | `/api/notifications/<id>` | Delete notification | Yes |

### 🛡️ Admin & Reports (`/api/admin`, `/api/reports`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/admin/stats` | Platform metrics (users, listings, rentals, volume) | Admin |
| `GET` | `/api/admin/users` | List user accounts with active status | Admin |
| `PUT` | `/api/admin/users/<id>/toggle-status` | Activate or deactivate user | Admin |
| `GET` | `/api/admin/equipment` | List all equipment for moderation | Admin |
| `DELETE` | `/api/admin/equipment/<id>` | Moderation removal of equipment listing | Admin |
| `POST` | `/api/reports` | Submit community safety report | Yes |
| `GET` | `/api/admin/reports` | List all safety reports | Admin |
| `PUT` | `/api/admin/reports/<id>/resolve` | Mark safety report as resolved | Admin |
| `POST` | `/api/admin/run-scheduled-tasks` | Manually run return reminders & request expiry | Admin |

---

## 7. How to Run the Application Locally

### Prerequisites
* **Python**: 3.10, 3.11, or 3.12
* **Node.js**: v18 or higher (with npm)
* **Git**

---

### Step 1: Set Up and Start Backend

1. Navigate to the `backend` directory:
   ```powershell
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```powershell
   # Windows PowerShell:
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required Python packages:
   ```powershell
   pip install -r requirements.txt
   ```

4. Populate the database with default categories, demo users, sample gear, and reviews:
   ```powershell
   python seed.py
   ```

5. Start the Flask backend server:
   ```powershell
   python run.py
   ```
   > The backend API will start on **`http://127.0.0.1:5000`** (Health check: `http://127.0.0.1:5000/health`).

---

### Step 2: Set Up and Start Frontend

1. Open a new terminal and navigate to the `frontend` directory:
   ```powershell
   cd frontend
   ```

2. Install npm dependencies:
   ```powershell
   npm install
   ```

3. Start the Vite development server:
   ```powershell
   npm run dev
   ```
   > The web app will launch at **`http://localhost:5173`**.

---

### Step 3: Access the Application

Open **[http://localhost:5173](http://localhost:5173)** in any browser.

The frontend is configured with a built-in reverse proxy in `vite.config.js` that automatically routes all `/api` calls to `http://127.0.0.1:5000`, preventing any CORS or network resolution issues.

---

## 8. Default Demo Accounts

You can log in with any of these pre-seeded accounts using the one-click demo buttons on the [Login Page](http://localhost:5173/login):

| Role | Email | Password | What You Can Test |
|---|---|---|---|
| **Platform Admin** | `admin@equipshare.test` | `admin123` | System metrics, category manager, user moderation, reports, manual background tasks |
| **Member (Owner)** | `yuvraj@equipshare.test` | `user123` | Listed camera, drill kit, tent, projector; approve incoming rental inquiries |
| **Member (Renter)** | `ananya@equipshare.test` | `user123` | Request equipment, track rentals, confirm return, submit 5-star reviews |
| **Member (Creator)** | `rohit@equipshare.test` | `user123` | Listed DJI gimbal, JBL speaker, oscilloscope; manage rentals |

*(You can also register brand-new accounts at any time via the Sign Up page).*

---

## 9. Background Tasks & Celery Automation

EquipShare includes automated background routines for platform maintenance:

1. **Return Reminders** (`send_return_reminders`):
   - Scans active rentals ending tomorrow.
   - Automatically generates reminders in notifications for renters.
2. **Request Expiry** (`expire_pending_requests`):
   - Finds rental requests in `PENDING` status older than 3 days.
   - Automatically updates their status to `EXPIRED` and notifies the renter.

### Running with Celery + Redis (Production / Optional):
If Redis is installed and running locally:
```powershell
celery -A app.celery worker --loglevel=info
```

### In-App Execution (Development):
You can trigger these maintenance tasks at any time from the **Admin Dashboard** (`🛡️ Admin -> ⚡ Run Maintenance Tasks`) or via HTTP:
```http
POST /api/admin/run-scheduled-tasks
Header: Authentication-Token: <admin_token>
```

---

## 10. Verification & Test Suite

An automated end-to-end integration test suite is included in `backend/test_suite.py`:

```powershell
cd backend
.\venv\Scripts\python.exe test_suite.py
```

### What the test suite verifies:
* `test_01_login_and_token`: Validates token generation and admin role verification.
* `test_02_categories`: Validates category retrieval and item counting.
* `test_03_equipment_listing_and_search`: Tests text search, availability filtering, and catalog listings.
* `test_04_auth_me_with_token`: Tests token authentication headers and user profile statistics.
* `test_05_rental_workflow`: Full end-to-end booking lifecycle (Request submission -> Owner approval -> Equipment availability toggle -> Return confirmation -> Review submission).
* `test_06_admin_stats_and_tasks`: Tests metrics calculation and scheduled maintenance task execution.

### Production Frontend Build Check:
```powershell
cd frontend
npm run build
```
Builds 100% cleanly into `frontend/dist` with zero linting or bundle errors.

---

## 11. Project Structure

```text
EquipShare/
├── README.md                      # Complete project documentation
├── DEVELOPMENT.md                 # Developer reference guide
├── equipshare.db                  # SQLite database file
│
├── backend/                       # Flask REST API
│   ├── run.py                     # Server entrypoint (0.0.0.0:5000)
│   ├── seed.py                    # Database seeding script (demo users & gear)
│   ├── test_suite.py              # Automated API integration tests
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment variables (salt, secret, db url)
│   │
│   └── app/
│       ├── __init__.py            # Flask app factory, CORS, token auth hook
│       ├── config.py              # Application settings
│       ├── extensions.py          # SQLAlchemy, Migrate, CORS, Security, Celery
│       ├── models.py              # 10 relational data models
│       │
│       ├── api/                   # REST API Blueprints
│       │   ├── __init__.py        # Blueprint router
│       │   ├── auth.py            # Login, register, profile, tokens
│       │   ├── equipment.py       # Catalog, search, listings, CRUD
│       │   ├── categories.py      # Category management
│       │   ├── rentals.py         # Requests, approvals, returns, active rentals
│       │   ├── reviews.py         # Rating and review submissions
│       │   ├── notifications.py   # User notification inbox
│       │   ├── reports.py         # User & equipment reporting
│       │   └── admin.py           # Admin stats, moderation, scheduled tasks
│       │
│       └── tasks/
│           └── reminders.py       # Celery background tasks
│
└── frontend/                      # Vue 3 SPA
    ├── index.html                 # App shell
    ├── vite.config.js             # Vite configuration with /api reverse proxy
    ├── package.json               # Node dependencies
    │
    └── src/
        ├── main.js                # App entrypoint (Pinia, Vue Router)
        ├── App.vue                # Main layout, sticky navbar, footer
        ├── api/
        │   └── client.js          # Axios client with token interceptor
        ├── store/
        │   └── auth.js            # Pinia auth store
        ├── router/
        │   └── index.js           # Vue Router with navigation guards
        │
        └── views/                 # Application Views
            ├── Home.vue           # Hero search & featured listings
            ├── EquipmentList.vue  # Catalog with search & filters
            ├── EquipmentDetails.vue # Booking form, specs, reviews, reports
            ├── AddEquipment.vue   # Item listing form
            ├── MyEquipment.vue    # User inventory & edit modal
            ├── RentalRequests.vue # Received & sent request management
            ├── MyRentals.vue      # Active rentals & review submission modal
            ├── Notifications.vue  # Notification center
            ├── Profile.vue        # User profile & password settings
            ├── AdminDashboard.vue # Metrics, category, user & report moderation
            ├── Login.vue          # Sign in with quick-demo buttons
            └── Register.vue       # Sign up with auto-login
```

---

## 12. License

This project is licensed under the MIT License — feel free to use, modify, and extend for your community or educational purposes.
