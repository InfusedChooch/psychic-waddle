from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import json
import datetime
import os

app = Flask(__name__)
app.secret_key = 'Duck_Goon_Slap00'  # 🔑 required for sessions
ADMIN_KEY = 'pass'  # set your admin password

MASTERLIST_FILE = 'masterlist.csv'
PASSLOG_FILE = 'passlog.json'

masterlist_df = pd.read_csv(MASTERLIST_FILE)

PERIOD_SCHEDULE = {
    0: {'start': '08:25', 'end': '08:30'},
    1: {'start': '08:33', 'end': '09:15'},
    2: {'start': '09:18', 'end': '10:00'},
    3: {'start': '10:03', 'end': '10:45'},
    4.5: {'start': '10:48', 'end': '11:30'},
   # 5.6: {'start': '11:18', 'end': '12:00'},
   # 6.7: {'start': '11:33', 'end': '12:15'},
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
    '2': {'status': 'open', 'user': None, 'time_out': None},
    '3': {'status': 'open', 'user': None, 'time_out': None}  # admin-only pass
}

@app.route('/')
def index():
    current_period_display = get_current_period()
    return render_template('index.html', passes=passes, current_period=current_period_display)

@app.route('/passes')
def get_passes():
    return jsonify(passes)

@app.route('/check', methods=['POST'])
def check():
    student_id = request.form.get('student_id').strip()
    message = ''
    current_time = datetime.datetime.now().time()
    current_day = datetime.datetime.now().strftime('%A')
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_period = get_current_period()

    try:
        student_row = masterlist_df[masterlist_df['ID'] == int(student_id)]
    except ValueError:
        return jsonify({'message': 'Invalid ID format.'})

    if student_row.empty:
        message = 'Invalid ID number.'
    else:
        student_period = float(student_row.iloc[0]['Period'])
        if current_period is None:
            message = 'No active period right now.'
        elif current_period != student_period:
            message = f'You cannot leave during this period (current: {current_period}).'
        else:
            for pass_id, pass_data in passes.items():
                if pass_data['user'] == student_id and pass_data['status'] == 'in use':
                    checkin_time = datetime.datetime.now().strftime('%H:%M:%S')
                    today_date = datetime.datetime.now().date()
                    time_out_dt = datetime.datetime.combine(
                        today_date,
                        datetime.datetime.strptime(pass_data['time_out'], '%H:%M:%S').time()
                    )
                    time_in_dt = datetime.datetime.now()
                    total_time = int((time_in_dt - time_out_dt).total_seconds())
                    if total_time < 0:
                        total_time = 0

                    student_key = str(student_id)
                    if student_key not in passlog:
                        passlog[student_key] = []
                    passlog[student_key].append({
                        'Date': current_date,
                        'DayOfWeek': current_day,
                        'Period': str(current_period),
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

    return jsonify({'message': message})

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['password'] == ADMIN_KEY:
            session['logged_in'] = True
            return redirect(url_for('admin_view'))
        else:
            return render_template('admin_login.html', error='Incorrect password.')
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_view():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    weekly_summary = []
    for student_id, records in passlog.items():
        student_row = masterlist_df[masterlist_df['ID'] == int(student_id)]
        student_name = student_row.iloc[0]['Name'] if not student_row.empty else 'Unknown'
        total_passes = len(records)
        total_time = sum(entry['TotalPassTime'] for entry in records)

        weekly_summary.append({
            'student_id': student_id,
            'student_name': student_name,
            'total_passes': total_passes,
            'total_time': total_time
        })

    return render_template('admin.html', weekly_summary=weekly_summary)

@app.route('/admin_passes')
def admin_passes():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 403

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

    return jsonify(active_passes)

@app.route('/admin_summary')
def admin_summary():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 403

    weekly_summary = []
    for student_id, records in passlog.items():
        student_row = masterlist_df[masterlist_df['ID'] == int(student_id)]
        student_name = student_row.iloc[0]['Name'] if not student_row.empty else 'Unknown'
        total_passes = len(records)
        total_time = sum(entry['TotalPassTime'] for entry in records)

        weekly_summary.append({
            'student_id': student_id,
            'student_name': student_name,
            'total_passes': total_passes,
            'total_time': total_time
        })

    return jsonify(weekly_summary)

@app.route('/admin_checkin/<pass_id>', methods=['POST'])
def admin_checkin(pass_id):
    if not session.get('logged_in'):
        return jsonify({'message': 'Unauthorized'}), 403

    if pass_id not in passes or passes[pass_id]['status'] != 'in use':
        return jsonify({'message': f'Pass {pass_id} is not currently out.'})

    student_id = passes[pass_id]['user']
    checkin_time = datetime.datetime.now().strftime('%H:%M:%S')
    today_date = datetime.datetime.now().date()
    time_out_dt = datetime.datetime.combine(
        today_date,
        datetime.datetime.strptime(passes[pass_id]['time_out'], '%H:%M:%S').time()
    )
    time_in_dt = datetime.datetime.now()
    total_time = int((time_in_dt - time_out_dt).total_seconds())
    if total_time < 0:
        total_time = 0

    current_period = get_current_period()

    student_key = str(student_id)
    if student_key not in passlog:
        passlog[student_key] = []
    passlog[student_key].append({
        'Date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'DayOfWeek': datetime.datetime.now().strftime('%A'),
        'Period': str(current_period),
        'CheckoutTime': passes[pass_id]['time_out'],
        'CheckinTime': checkin_time,
        'TotalPassTime': total_time
    })
    save_passlog(passlog)

    passes[pass_id] = {'status': 'open', 'user': None, 'time_out': None}

    return jsonify({'message': f'Pass {pass_id} manually checked in.'})

@app.route('/admin_create_pass', methods=['POST'])
def admin_create_pass():
    if not session.get('logged_in'):
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    student_id = data.get('student_id')

    try:
        student_row = masterlist_df[masterlist_df['ID'] == int(student_id)]
    except ValueError:
        return jsonify({'message': 'Invalid ID format.'})

    if student_row.empty:
        return jsonify({'message': 'Student ID not found.'})

    if passes['3']['status'] == 'in use':
        return jsonify({'message': 'Admin pass is already in use.'})

    checkout_time = datetime.datetime.now().strftime('%H:%M:%S')
    passes['3'] = {
        'status': 'in use',
        'user': student_id,
        'time_out': checkout_time
    }

    return jsonify({'message': f'Admin Pass 3 created for Student ID {student_id}.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
