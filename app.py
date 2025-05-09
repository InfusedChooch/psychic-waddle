from flask import Flask, render_template, request
import pandas as pd
import json
import datetime
import os

app = Flask(__name__)

MASTERLIST_FILE = 'masterlist.csv'
PASSLOG_FILE = 'passlog.json'

masterlist_df = pd.read_csv(MASTERLIST_FILE)

# Correct period start and end times
PERIOD_SCHEDULE = {
    0: {'start': '08:25', 'end': '08:30'},
    1: {'start': '08:33', 'end': '09:15'},
    2: {'start': '09:18', 'end': '10:00'},
    3: {'start': '10:03', 'end': '10:45'},
    4.5: {'start': '10:48', 'end': '11:30'},
    5.6: {'start': '11:18', 'end': '12:00'},
    6.7: {'start': '11:33', 'end': '12:15'},
    7.8: {'start': '12:03', 'end': '12:45'},
    9: {'start': '12:48', 'end': '13:30'},
    10: {'start': '13:33', 'end': '14:15'},
    11: {'start': '14:18', 'end': '15:00'},
}

def get_current_period():
    now = datetime.datetime.now().time()
    for period, times in PERIOD_SCHEDULE.items():
        start = datetime.datetime.strptime(times['start'], '%H:%M').time()
        end = datetime.datetime.strptime(times['end'], '%H:%M').time()
        if start <= now <= end:
            return period
    return None

def load_passlog():
    if os.path.exists(PASSLOG_FILE):
        with open(PASSLOG_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    else:
        return {}

def save_passlog(data):
    with open(PASSLOG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

passlog = load_passlog()

passes = {
    '1': {'status': 'open', 'user': None, 'time_out': None},
    '2': {'status': 'open', 'user': None, 'time_out': None}
}

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    current_time = datetime.datetime.now().time()
    current_day = datetime.datetime.now().strftime('%A')
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_period_display = get_current_period()

    if request.method == 'POST':
        student_id = str(request.form['student_id']).strip()
        student_row = masterlist_df[masterlist_df['ID'] == int(student_id)]
        if student_row.empty:
            message = 'Invalid ID number.'
        else:
            student_period = float(student_row.iloc[0]['Period'])
            current_period = get_current_period()

            if current_period is None:
                message = 'No active period right now.'
            elif current_period != student_period:
                message = f'You cannot leave during this period (current: {current_period}).'
            else:
                for pass_id, pass_data in passes.items():
                    if pass_data['user'] == student_id and pass_data['status'] == 'in use':
                        checkin_time = datetime.datetime.now().strftime('%H:%M:%S')

                        # ✅ FIX: Use today’s date for both datetime objects
                        today_date = datetime.datetime.now().date()
                        time_out_dt = datetime.datetime.combine(
                            today_date,
                            datetime.datetime.strptime(pass_data['time_out'], '%H:%M:%S').time()
                        )
                        time_in_dt = datetime.datetime.now()

                        total_time = int((time_in_dt - time_out_dt).total_seconds())
                        if total_time < 0:
                            total_time = 0  # Prevent negative if date rollover (e.g. past midnight)

                        period_key = str(current_period)
                        student_key = str(student_id)

                        if period_key not in passlog:
                            passlog[period_key] = {}
                        if student_key not in passlog[period_key]:
                            passlog[period_key][student_key] = []

                        passlog[period_key][student_key].append({
                            'Date': current_date,
                            'DayOfWeek': current_day,
                            'CheckoutTime': pass_data['time_out'],
                            'CheckinTime': checkin_time,
                            'TotalPassTime': total_time
                        })
                        save_passlog(passlog)

                        passes[pass_id] = {'status': 'open', 'user': None, 'time_out': None}
                        message = 'Returned successfully.'
                        break
                else:
                    for pass_id, pass_data in passes.items():
                        if pass_data['status'] == 'open':
                            checkout_time = datetime.datetime.now().strftime('%H:%M:%S')
                            passes[pass_id] = {
                                'status': 'in use',
                                'user': student_id,
                                'time_out': checkout_time
                            }
                            message = f'Pass {pass_id} claimed at {checkout_time}.'
                            break
                    else:
                        message = 'No passes available right now.'

    return render_template('index.html', passes=passes, message=message, current_period=current_period_display)

@app.route('/admin')
def admin_view():
    active_passes = []
    for pass_id, pass_data in passes.items():
        if pass_data['status'] == 'in use':
            student_row = masterlist_df[masterlist_df['ID'] == int(pass_data['user'])]
            student_name = student_row.iloc[0]['Name'] if not student_row.empty else 'Unknown'
            active_passes.append({
                'pass_id': pass_id,
                'student_id': pass_data['user'],
                'student_name': student_name,
                'time_out': pass_data['time_out']
            })

    weekly_summary = []
    for period_key, students in passlog.items():
        for student_id, entries in students.items():
            student_row = masterlist_df[masterlist_df['ID'] == int(student_id)]
            student_name = student_row.iloc[0]['Name'] if not student_row.empty else 'Unknown'
            total_passes = len(entries)
            total_time = sum(entry['TotalPassTime'] for entry in entries)

            weekly_summary.append({
                'period': period_key,
                'student_id': student_id,
                'student_name': student_name,
                'total_passes': total_passes,
                'total_time': total_time
            })

    return render_template('admin.html', active_passes=active_passes, weekly_summary=weekly_summary)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
