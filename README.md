# psychic-waddle
Student tracking app


## ✅ WHAT HAS BEEN DONE

### 🎯 Core Flask App (app.py)

* Complete Flask app built with:

  * `/` route for student-facing UI
  * `/admin` route for admin dashboard
* Integrated period time lookup using a dictionary of start/end times
* Dynamic current period detection with `get_current_period()`
* JSON logging in the structure:

```
{
  "period_number": {
    "student_id": [
      {"Date", "DayOfWeek", "CheckoutTime", "CheckinTime", "TotalPassTime"}
    ]
  }
}
```

* Period keys and student IDs stored as strings to avoid JSON numeric key issues
* Complete check-in/check-out flow:

  * Valid ID check
  * Period validation based on current time
  * Updates pass status and log
* Built active passes tracker and weekly summary for admin
* Flask runs on `0.0.0.0` for LAN access
* Displays current period number on student page

### 🎯 Student Landing Page (index.html)

* Displays:

  * Current period number
  * Status of Pass 1 and Pass 2 (open/in use with time)
  * ID input form
  * Message feedback

### 🎯 Admin Page (admin.html)

* Displays:

  * Active passes table
  * Weekly summary table (period, student ID, name, total passes, total time)

### 🎯 Sample Data

* Generated `masterlist.csv` matching custom period numbers
* Generated `passlog.json` following updated JSON structure
* Explained JSON schema and meaning

## 📝 WHAT STILL NEEDS TO BE DONE

### 🖥️ 1. Styling/UX

* Add CSS styling to index.html and admin.html
* Visually differentiate open vs occupied passes
* Optional: mobile-friendly/responsive design

### 🔐 2. Admin Controls

* Add password protection or authentication for `/admin`
* Add button controls to manually override/reset passes from admin page
* Option to clear logs or export CSV from admin dashboard

### 📝 3. Code Improvements

* Currently passes are stored in-memory → add save/load mechanism to persist across server restarts
* Handle overlapping period times (4.5, 5.6, etc.) → clarify which takes priority if overlapping
* Optional: log failed check-out attempts for audit

### 🏗️ 4. Deployment Considerations

* Disable debug mode for production (`debug=False`)
* Optional deployment on Raspberry Pi, local server, or other LAN appliance

### 🧪 5. Testing

* Test across devices to verify:

  * LAN access
  * Period detection accuracy
  * Concurrent usage
* Test edge cases:

  * ID outside valid period
  * Double check-in/out
  * Invalid ID entry

## 🎉 OPTIONAL FUTURE FEATURES

* QR code scanning for ID input
* Countdown timer showing time left for pass
* Daily/weekly auto-reset of passes
* Integration with school login/database


👉 **Next priorities:**

1. Add CSS styling
2. Decide on admin control buttons
3. Add pass state persistence or auto-reset
4. (Optional) Authentication for admin

