from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import pandas as pd
import json
import datetime
import os
import io
import csv

app = Flask(__name__)
app.secret_key = 'Duck_Goon_Slap00'

MASTERLIST_FILE = 'masterlist.csv'
PASSLOG_FILE = 'passlog.json'
AUDITLOG_FILE = 'auditlog.json'
CONFIG_FILE = 'config.json'

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

def load_json_file(filepath, default_value):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default_value
    return default_value

def save_json_file(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

config = load_json_file(CONFIG_FILE, {'admin_password': 'pass'})
passlog = load_json_file(PASSLOG_FILE, {})
auditlog = load_json_file(AUDITLOG_FILE, [])

def log_audit(student_id, reason):
    auditlog.append({
        'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'student_id': student_id,
        'reason': reason
    })
    save_json_file(AUDITLOG_FILE, auditlog)

passes = {
    '1': {'status': 'open', 'user': None, 'time_out': None},
    '2': {'status': 'open', 'user': None, 'time_out': None},
    '3': {'status': 'open', 'user': None, 'time_out': None}
}

@app.route('/')
def index():
    return render_template('index.html', passes=passes, current_period=get_current_period())

@app.route('/passes')
def get_passes():
    return jsonify(passes)

@app.route('/check', methods=['POST'])
def check():
    student_id = request.form.get('student_id', '').strip()
    current_period = get_current_period()
    current_day = datetime.datetime.now().strftime('%A')
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')

    try:
        student_row = masterlist_df[masterlist_df['ID'] == int(student_id)]
    except ValueError:
        log_audit(student_id, 'Invalid ID format')
        return jsonify({'message': 'Invalid ID format.'})

    if student_row.empty:
        log_audit(student_id, 'Invalid ID number')
        return jsonify({'message': 'Invalid ID number.'})

    student_period = float(student_row.iloc[0]['Period'])

    if current_period is None:
        log_audit(student_id, 'No active period')
        return jsonify({'message': 'No active period right now.'})

    if current_period != student_period:
        log_audit(student_id, f'Invalid period: tried {current_period}, expected {student_period}')
        return jsonify({'message': f'You cannot leave during this period (current: {current_period}).'})

    # Check-in or check-out logic
    for pass_id, pass_data in passes.items():
        if pass_data['user'] == student_id and pass_data['status'] == 'in use':
            checkin_time = datetime.datetime.now().strftime('%H:%M:%S')
            time_out_dt = datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.strptime(pass_data['time_out'], '%H:%M:%S').time())
            total_time = int((datetime.datetime.now() - time_out_dt).total_seconds())
            total_time = max(total_time, 0)
            passlog.setdefault(student_id, []).append({
                'Date': current_date,
                'DayOfWeek': current_day,
                'Period': str(current_period),
                'CheckoutTime': pass_data['time_out'],
                'CheckinTime': checkin_time,
                'TotalPassTime': total_time,
                'Note': pass_data.get('note', '')
            })
            save_json_file(PASSLOG_FILE, passlog)
            passes[pass_id] = {'status': 'open', 'user': None, 'time_out': None}
            return jsonify({'message': 'Returned successfully.'})

    for pass_id, pass_data in passes.items():
        if pass_data['status'] == 'open':
            checkout_time = datetime.datetime.now().strftime('%H:%M:%S')
            passes[pass_id] = {'status': 'in use', 'user': student_id, 'time_out': checkout_time}
            return jsonify({'message': f'Pass {pass_id} claimed at {checkout_time}.'})

    return jsonify({'message': 'No passes available right now.'})

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['password'] == config.get('admin_password'):
            session['logged_in'] = True
            return redirect(url_for('admin_view'))
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
        total_time = sum(r['TotalPassTime'] for r in records)
        total_passes = len(records)
        avg_time = total_time // total_passes if total_passes else 0
        passes_over_5_min = sum(1 for r in records if r['TotalPassTime'] > 300)
        summary = {
            'student_id': student_id,
            'student_name': student_name,
            'total_time': f"{total_time // 60}m {total_time % 60}s",
            'total_passes': total_passes,
            'avg_time': f"{avg_time // 60}m {avg_time % 60}s",
            'passes_over_5_min': passes_over_5_min
        }
        weekly_summary.append(summary)

    return render_template('admin.html', weekly_summary=weekly_summary, audit_log=auditlog)

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

@app.route('/admin_checkin/<pass_id>', methods=['POST'])
def admin_checkin(pass_id):
    if not session.get('logged_in'):
        return jsonify({'message': 'Unauthorized'}), 403
    if pass_id not in passes or passes[pass_id]['status'] != 'in use':
        return jsonify({'message': f'Pass {pass_id} is not currently out.'})
    student_id = passes[pass_id]['user']
    checkin_time = datetime.datetime.now().strftime('%H:%M:%S')
    time_out_dt = datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.strptime(passes[pass_id]['time_out'], '%H:%M:%S').time())
    total_time = int((datetime.datetime.now() - time_out_dt).total_seconds())
    total_time = max(total_time, 0)
    passlog.setdefault(student_id, []).append({
        'Date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'DayOfWeek': datetime.datetime.now().strftime('%A'),
        'Period': str(get_current_period()),
        'CheckoutTime': passes[pass_id]['time_out'],
        'CheckinTime': checkin_time,
        'TotalPassTime': total_time,
        'Note': passes[pass_id].get('note', '')
    })
    save_json_file(PASSLOG_FILE, passlog)
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
    passes['3'] = {'status': 'in use', 'user': student_id, 'time_out': datetime.datetime.now().strftime('%H:%M:%S')}
    return jsonify({'message': f'Admin Pass 3 created for Student ID {student_id}.'})

@app.route('/admin_change_password', methods=['POST'])
def admin_change_password():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    data = request.get_json()
    if data.get('current_password') != config.get('admin_password'):
        return jsonify({'success': False, 'message': 'Current password incorrect.'})
    if data.get('new_password') != data.get('confirm_password'):
        return jsonify({'success': False, 'message': 'New passwords do not match.'})
    config['admin_password'] = data.get('new_password')
    save_json_file(CONFIG_FILE, config)
    return jsonify({'success': True, 'message': 'Password changed successfully!'})

@app.route('/admin_add_note/<student_id>', methods=['POST'])
def admin_add_note(student_id):
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    note = data.get('note', '').strip()

    if not note:
        return jsonify({'success': False, 'message': 'Note cannot be empty.'})

    # ✅ Look for active pass for this student
    for pass_id, pass_data in passes.items():
        if pass_data['user'] == student_id and pass_data['status'] == 'in use':
            passes[pass_id]['note'] = note
            return jsonify({'success': True, 'message': f'Note saved to active Pass {pass_id}.'})

    return jsonify({'success': False, 'message': 'No active pass found for this student.'})


@app.route('/admin_report')
def admin_report():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 403
    report_data = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for student_id, records in passlog.items():
        student_row = masterlist_df[masterlist_df['ID'] == int(student_id)]
        student_name = student_row.iloc[0]['Name'] if not student_row.empty else 'Unknown'
        day_totals = {d: 0 for d in days}
        over_5 = sum(1 for r in records if r['TotalPassTime'] > 300)
        over_10 = sum(1 for r in records if r['TotalPassTime'] > 600)
        for r in records:
            if r['DayOfWeek'] in day_totals:
                day_totals[r['DayOfWeek']] += r['TotalPassTime']
        weekly = ' '.join(f"{d[0]}:{day_totals[d]//60}" for d in days)
        report_data.append({'student_name': student_name, 'student_id': student_id, 'weekly_report': weekly, 'passes_over_5_min': over_5, 'passes_over_10_min': over_10})
    return render_template('admin_report.html', report_data=report_data)

@app.route('/admin_report_csv')
def admin_report_csv():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Student Name', 'Student ID', 'Weekly Report', 'Passes Over 5 Min', 'Passes Over 10 Min'])
    for student_id, records in passlog.items():
        student_row = masterlist_df[masterlist_df['ID'] == int(student_id)]
        student_name = student_row.iloc[0]['Name'] if not student_row.empty else 'Unknown'
        day_totals = {d: 0 for d in days}
        over_5 = sum(1 for r in records if r['TotalPassTime'] > 300)
        over_10 = sum(1 for r in records if r['TotalPassTime'] > 600)
        for r in records:
            if r['DayOfWeek'] in day_totals:
                day_totals[r['DayOfWeek']] += r['TotalPassTime']
        weekly = ' '.join(f"{d[0]}:{day_totals[d]//60}" for d in days)
        writer.writerow([student_name, student_id, weekly, over_5, over_10])
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=weekly_report.csv"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
