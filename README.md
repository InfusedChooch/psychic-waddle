# Check-In/Out App - README

This app is a Flask-based web application to track student hall passes, including an admin panel for reporting and pass management.

---

## ✅ CURRENT FEATURES

### 🎯 Flask App Core (`app.py`)

* Uses **config.json** to configure:

  * Admin username and password
  * Period schedule
  * Theme color and school name
  * Logo URL
  * Reporting thresholds (5 min / 10 min pass time)
  * Number of passes
* `/` route: student landing page
* `/check`: handles student check-in/check-out
* `/passes`: returns JSON status of passes
* `/admin_login`: admin login with username & password from config
* `/admin`: admin dashboard showing:

  * Active passes
  * Weekly summary
  * Audit log
* `/admin_passes`: returns JSON list of active passes (admin view)
* `/admin_checkin/<pass_id>`: allows admin manual check-in
* `/admin_create_pass`: allows admin to assign admin pass 3
* `/admin_report`: view weekly summary by student
* `/admin_report_csv`: export weekly report to CSV

### 🎨 Student Page (`index.html`)

* Displays current period number
* Displays status of Pass 1 and Pass 2 (Pass 3 hidden from students)
* Shows logo in tab (favicon) using `logo_url` from config
* Shows school name dynamically from config
* Color theme uses `theme_color` from config

### 🛠️ Admin Page (`admin.html`)

* Admin login requires **username + password** from config
* Displays:

  * Active passes (with live updating timers)
  * Weekly summary table
  * Audit log
* Shows `session.admin_username` to indicate logged-in admin
* Shows favicon from `logo_url`

### 📈 Reporting Page (`admin_report.html`)

* Weekly report per student:

  * Total pass time
  * Total passes
  * Passes over 5 minutes / 10 minutes
* Download CSV export
* Shows favicon from `logo_url`

### 📁 Static Assets

* Favicon/logo stored in `/static/images/`
* Logo displayed in browser tab using `<link rel="icon">`

---

## 📝 WHAT STILL NEEDS TO BE DONE

### 1️⃣ Styling / UX

* Add more CSS styling (current is minimal)
* Add mobile-friendly/responsive layout

### 2️⃣ Admin Controls

* Optional: Add IP filtering using `allowed_ips` config
* Optional: Add session timeout enforcement from `session_timeout_minutes`
* Optional: Add data retention enforcement from `data_retention_days`

### 3️⃣ Code Enhancements

* Move `auditlog` and `passlog` to a database (currently JSON file storage)
* Add automated log cleanup using `data_retention_days`
* Add multi-admin support (currently supports single admin\_username)

### 4️⃣ Deployment

* Disable debug mode in production (`debug_mode` = false)
* Deploy behind HTTPS reverse proxy if public-facing

### 5️⃣ Testing

* Verify login rejection with wrong credentials
* Verify period detection accuracy
* Verify admin actions across devices

---

## 📦 CONFIG.JSON SAMPLE

```json
{
  "admin_username": "admin",
  "admin_password": "pass123",
  "theme_color": "#4a90e2",
  "school_name": "Jefferson Middle School",
  "logo_url": "/static/images/school_logo.png",
  "passes_available": 3,
  "period_schedule": { ... },
  "report_time_thresholds": { "over_5": 300, "over_10": 600 },
  "debug_mode": true
}
```

👉 **To update settings, edit `config.json` and restart the server.**

---

## 🎉 NEXT STEPS

* Add more user interface polish
* Improve security (IP filtering, session timeout)
* Explore database integration for logs

---

For any issues or feature requests, contact the app developer or submit updates via your project repo.
