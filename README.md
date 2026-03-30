# 🍽️ CanteenQuick — Token Management System

A full-stack canteen ordering system with role-based login, instant token generation, and a live token dashboard.

---

## 📋 Prerequisites

Make sure the following are installed before you begin:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.9+ | https://python.org |
| Node.js | 16+ | https://nodejs.org |
| MySQL | 8.0+ | https://dev.mysql.com/downloads/ |
| mysql-connector-python | (installed via pip) | — |

---

## 🗄️ Step 1 — Database Setup

1. Open MySQL Workbench or any MySQL client and run:
   ```sql
   CREATE DATABASE canteen_db;
   ```

2. Open `d:\ctm\backend\database\database.py` and update the connection string with your MySQL credentials:
   ```python
   SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://YOUR_USER:YOUR_PASSWORD@localhost/canteen_db"
   ```
   > Default is `root:root`. Change it to match your MySQL username and password.

---

## 🐍 Step 2 — Backend Setup

Open a terminal and run the following from the **project root** (`d:\ctm`):

### Install Python dependencies
```bash
pip install fastapi uvicorn sqlalchemy mysql-connector-python python-jose passlib bcrypt python-multipart
```

### Create tables & seed data
```bash
python force_setup.py
```
> This creates all database tables and inserts 20+ menu items and the default admin user.

### Start the backend server
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

✅ Backend will be available at: **http://localhost:8000**  
✅ API docs (Swagger): **http://localhost:8000/docs**

---

## ⚛️ Step 3 — Frontend Setup

Open a **second terminal** and navigate to the frontend folder:

```bash
cd d:\ctm\frontend
```

### Install Node dependencies
```bash
npm install
```

### Start the frontend dev server
```bash
npm run dev -- --host --port 3000
```

✅ Frontend will be available at: **http://localhost:3000**

---

## 🔐 Login Credentials

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@canteen.com` | `admin` |
| **Customer** | Register any email | Any password |

---

## 🚀 How It Works

### Customer Flow
1. Go to **http://localhost:3000** → Login or Register
2. Browse the **Menu** → Add items to cart
3. Go to **Cart** → Click **"Proceed to Payment"**
4. Get your **Token Number** instantly
5. Track your order live at **http://localhost:3000/tokens**

### Admin Flow
1. Login with `admin@canteen.com` / `admin`
2. You are automatically redirected to the **Admin Dashboard**
3. View all orders and change their status to **Pending** or **Completed**
4. Completing an order updates the **Live Token Dashboard** in real time

---

## 📁 Project Structure

```
d:\ctm\
├── backend\
│   ├── main.py              # FastAPI app entry point
│   ├── models\models.py     # SQLAlchemy database models
│   ├── schemas\schemas.py   # Pydantic request/response schemas
│   ├── routers\
│   │   ├── auth.py          # Login & Register endpoints
│   │   ├── items.py         # Menu items endpoints
│   │   ├── orders.py        # Order placement & status update
│   │   ├── tokens.py        # Token generation & live tracking
│   │   └── analytics.py     # Dashboard stats
│   └── database\database.py # MySQL connection config
├── frontend\
│   ├── src\
│   │   ├── App.jsx          # Root component with routing & auth
│   │   ├── pages\
│   │   │   ├── Login.jsx         # Login & Register page
│   │   │   ├── Menu.jsx          # Food menu with categories
│   │   │   ├── CartPage.jsx      # Cart & checkout
│   │   │   ├── TokenDashboard.jsx # Live token board
│   │   │   └── AdminDashboard.jsx # Admin order management
│   │   └── styles\global.css    # Design system
│   └── index.html
├── force_setup.py           # DB seeding script (run once)
└── README.md
```

---

## ⚠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `Access denied for user` | Update MySQL credentials in `database.py` |
| `Port 8000 already in use` | Run `taskkill /F /IM uvicorn.exe` then restart |
| `Port 3000 already in use` | Run `taskkill /F /IM node.exe` then restart |
| `Module not found` | Run `pip install -r requirements.txt` again |
| Login fails for admin | Re-run `python force_setup.py` to reset admin account |
