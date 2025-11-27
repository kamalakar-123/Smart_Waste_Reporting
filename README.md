🌱 Smart Waste Reporting System

A full-stack project built using Flask, SQLite, HTML/CSS/JS, with Firebase Authentication, AOS animations, Boxicons, geolocation support, and image uploads.

This system enables users to report waste in their area and workers to manage, update, and complete these reports. A public dashboard displays verified completed waste cleanups.

🔥 **NEW: Firebase Authentication Integration!**
- Email/Password authentication
- Google Sign-In (one-click login)
- Secure token-based authentication
- Role-based access control
- See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for setup instructions

🚀 Features
👤 User (Public User)

Register / Login (Email/Password or Google)

Submit waste reports with:

Before image

Description

Auto-detected geolocation (latitude & longitude)

View:

Total reports

Pending reports

Completed reports

Full report details (with map link)

View public list of all completed reports

🧹 Worker (Municipal Staff)

Login (Email/Password or Google)

View:

Open complaints

Accepted

In Progress

Completed by worker

Update complaint status:

Pending → Accepted

Accepted → In Progress

In Progress → Completed

Upload after-cleaning image

🎨 UI Features

Clean modern eco-green theme

UI animations using AOS (Animate On Scroll)

Icons using Boxicons

Responsive HTML/CSS

Simple and lightweight vanilla JS

🛠️ Tech Stack
Frontend

HTML5, CSS3, JavaScript

AOS (Animate On Scroll)

Boxicons

Bootstrap (optional)

Backend

Python

Flask

SQLite3

Jinja2 Templates

Other

Image upload handling

Geolocation API

Session-based authentication

📂 Project Structure
c:/WasteReport/
│── app.py               # Flask entry point
│── db.py                # Database initialization & connection
│── waste_report.db      # Auto-created SQLite DB  
│  
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── main.js
│   └── uploads/         # Uploaded before/after images
│
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── user_dashboard.html
    ├── worker_dashboard.html
    ├── complaint_form.html
    ├── my_complaints.html
    ├── complaint_detail.html
    ├── public_reports.html
    └── worker_open_complaints.html

⚙️ Installation & Setup (Windows PowerShell)
1️⃣ Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

2️⃣ Install dependencies
pip install Flask


(If you want, create a requirements.txt with Flask==3.0.0)

3️⃣ Run the app
python app.py

4️⃣ Open in browser
http://127.0.0.1:5000

🗄️ Database Notes

SQLite database file waste_report.db is auto-created by db.py

No configuration needed

Image paths are stored in the DB

Physical files are saved in static/uploads/

🗺️ Location & Mapping

Browser geolocation used via navigator.geolocation

Each complaint stores latitude and longitude

Users/workers get one-click map navigation:

https://www.google.com/maps?q=<lat>,<lng>

🔐 Authentication

Session-based login

Passwords hashed using Werkzeug

Roles:

user

worker

🖼️ Screenshots (Add yours here)
![Dashboard](static/screenshots/dashboard.png)
![Report Form](static/screenshots/report_form.png)
![Public Reports](static/screenshots/public_reports.png)


(You can update these after running your project.)

🧪 Future Improvements

Admin role

Assign complaints to nearest worker automatically

Email/SMS alerts

Notifications center

Live map dashboard

REST API for mobile apps

🤝 Contributing

Pull requests are welcome!
For major changes, open an issue to discuss what you’d like to add.

🙌 Author

Kamalakara Marathi
Smart Waste Reporting System – Final Year Mini Project
