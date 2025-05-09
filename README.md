# 📝 Hall Pass Tracker

A **Flask-based web app** to track student hall passes in real-time, with admin controls, reporting, and analytics.

## 🚀 Features

✅ **Student Interface**

- View current period number
- See live pass availability
- Check out / check in using Student ID
- Simple, responsive UI for students

✅ **Admin Dashboard**

- Password-protected login
- View all active passes (real-time updates)
- Manually check-in passes
- Add notes to active passes
- Create special “Admin Pass”
- Weekly summary table with:
  - Total passes
  - Total time out
  - Average pass duration
  - Passes over 5 minutes
- View last 5 audit log events (invalid attempts)
- Change admin password
- Download weekly report as CSV

✅ **Data Logging**

- Pass activity saved to `passlog.json`
- Audit events saved to `auditlog.json`
- Admin password stored in `config.json`

✅ **Reports**

- Generate a detailed weekly report by student
- Export reports in HTML and CSV formats
- Per-day total pass time breakdown

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
