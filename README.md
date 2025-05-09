# 📝 Hall Pass Tracker

A **Flask-based web app** to track student hall passes in real-time, with admin controls, reporting, and analytics.

## 🚀 Features

👉 **Student Interface**

* View current period number
* See live pass availability
* Check out / check in using Student ID
* Simple, responsive UI for students

👉 **Admin Dashboard**

* Password-protected login
* View all active passes (real-time updates)
* Manually check-in passes
* Add notes to active passes
* Create special “Admin Pass”
* Weekly summary table with:

  * Total passes
  * Total time out
  * Average pass duration
  * Passes over 5 minutes
* View last 5 audit log events (invalid attempts)
* Change admin password
* Download weekly report as CSV

👉 **Data Logging**

* Pass activity saved to `passlog.json`
* Audit events saved to `auditlog.json`
* Admin password stored in `config.json`

👉 **Reports**

* Generate a detailed weekly report by student
* Export reports in HTML and CSV formats
* Per-day total pass time breakdown

---

## 📂 File Structure

```bash
├── app.py               # Flask backend
├── templates/
│   ├── index.html       # Student-facing UI
│   ├── admin.html       # Admin dashboard UI
│   ├── admin_login.html # Admin login UI
│   ├── admin_report.html# Admin weekly report UI
├── static/              # (optional for extra CSS/JS)
├── masterlist.csv       # Student ID + Period list
├── passlog.json         # Pass logs
├── auditlog.json        # Audit logs
├── config.json          # Admin config (password)
├── README.md            # This file
```

---

## ⚙️ How It Works

* Students check in/out by entering their **Student ID**
* System verifies ID and whether it’s their scheduled period
* Passes automatically tracked:

  * Time out
  * Time in
  * Total elapsed time
* Admin panel shows real-time active passes
* Reports summarize weekly data for each student

---

## 🖥️ Running the App

1. **Install dependencies**:

```bash
pip install flask pandas
```

2. **Ensure `masterlist.csv` is populated**:

Sample `masterlist.csv`:

```csv
ID,Name,Period
12345,John Doe,1
23456,Jane Smith,2
```

3. **Start the server**:

```bash
python app.py
```

4. Open browser → [http://localhost:5000](http://localhost:5000)

Admin page → [http://localhost:5000/admin\_login](http://localhost:5000/admin_login)

Default admin password: `pass`

---

## 🔐 Admin Password

👉 First password is set in `config.json`:

```json
{
    "admin_password": "pass"
}
```

Admins can update this from the dashboard.

---

## 📊 Reports

* View reports online (`/admin_report`)
* Download CSV (`/admin_report_csv`)

Example CSV output:

| Student Name | Student ID | Weekly Report | Passes Over 5 Min | Passes Over 10 Min |
| ------------ | ---------- | ------------- | ----------------- | ------------------ |
| John Doe     | 12345      | M:5 T:0 W:2   | 1                 | 0                  |

### Example JSON log format (`passlog.json`):

```json
{
  "12345": [
    {
      "Date": "2025-05-09",
      "DayOfWeek": "Friday",
      "Period": "1",
      "CheckoutTime": "08:40:12",
      "CheckinTime": "08:55:20",
      "TotalPassTime": 900
    }
  ],
  "67890": [
    {
      "Date": "2025-05-09",
      "DayOfWeek": "Friday",
      "Period": "2",
      "CheckoutTime": "09:20:05",
      "CheckinTime": "09:40:15",
      "TotalPassTime": 1200
    }
  ]
}
```

### Example JSON audit log format (`auditlog.json`):

```json
[
  {
    "time": "2025-05-09 09:30:00",
    "student_id": "99999",
    "reason": "Invalid ID number"
  },
  {
    "time": "2025-05-09 09:35:00",
    "student_id": "12345",
    "reason": "Invalid period: tried 2, expected 1"
  }
]
```

---

## 💡 Next Steps

👉 Add database or file persistence for passes (currently in-memory)

👉 Mobile-friendly UI

👉 Optional: QR code check-in

👉 Optional: teacher override/clear buttons

---

## 📝 License

MIT License

---

## 👨‍💻 Contributions

Feel free to fork and submit pull requests! Suggestions and improvements are welcome.

---

## 🙌 Acknowledgments

Built for classroom use — inspired by the need to simplify hall pass tracking and logging.
