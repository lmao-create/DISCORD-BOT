import os
import json
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import schedule
import threading
import time
from io import StringIO, BytesIO

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuration
DATA_FILE = 'applications_data.json'
CONFIG_FILE = 'applications_config.json'

# Store for scheduler
pending_reminders = {}


def load_applications():
    """Load applications from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_applications(data):
    """Save applications to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_config():
    """Load configuration from JSON file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/applications', methods=['GET'])
def get_applications():
    """Get all applications with optional filtering"""
    applications = load_applications()
    status_filter = request.args.get('status', 'all')

    apps_list = list(applications.values())

    # Filter by status
    if status_filter != 'all':
        apps_list = [app for app in apps_list if app.get('status') == status_filter]

    # Sort by submission date (newest first)
    apps_list.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)

    return jsonify({
        'success': True,
        'data': apps_list,
        'total': len(applications),
        'filtered': len(apps_list)
    })


@app.route('/api/applications/<app_id>', methods=['GET'])
def get_application(app_id):
    """Get a specific application"""
    applications = load_applications()

    if app_id not in applications:
        return jsonify({'success': False, 'error': 'Application not found'}), 404

    return jsonify({
        'success': True,
        'data': applications[app_id]
    })


@app.route('/api/applications/<app_id>/review', methods=['POST'])
def review_application(app_id):
    """Review and approve/reject an application"""
    applications = load_applications()

    if app_id not in applications:
        return jsonify({'success': False, 'error': 'Application not found'}), 404

    data = request.get_json()
    decision = data.get('decision', '').lower()
    notes = data.get('notes', '')
    reviewer = data.get('reviewer', 'Admin')

    if decision not in ['approved', 'rejected']:
        return jsonify({'success': False, 'error': 'Invalid decision'}), 400

    app = applications[app_id]
    app['status'] = decision
    app['reviewed_at'] = datetime.now().isoformat()
    app['reviewer_id'] = reviewer
    app['review_notes'] = notes

    save_applications(applications)

    return jsonify({
        'success': True,
        'message': f'Application {decision}',
        'data': app
    })


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get application statistics"""
    applications = load_applications()

    if not applications:
        return jsonify({
            'success': True,
            'total': 0,
            'pending': 0,
            'approved': 0,
            'rejected': 0,
            'approval_rate': 0,
            'avg_review_time': 0
        })

    apps = list(applications.values())

    total = len(apps)
    pending = len([a for a in apps if a.get('status') == 'pending'])
    approved = len([a for a in apps if a.get('status') == 'approved'])
    rejected = len([a for a in apps if a.get('status') == 'rejected'])

    reviewed = approved + rejected
    approval_rate = (approved / reviewed * 100) if reviewed > 0 else 0

    # Calculate average review time
    review_times = []
    for app in apps:
        if app.get('reviewed_at') and app.get('submitted_at'):
            try:
                submitted = datetime.fromisoformat(app['submitted_at'])
                reviewed = datetime.fromisoformat(app['reviewed_at'])
                review_times.append((reviewed - submitted).total_seconds() / 3600)
            except:
                pass

    avg_review_time = sum(review_times) / len(review_times) if review_times else 0

    return jsonify({
        'success': True,
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'approval_rate': round(approval_rate, 2),
        'avg_review_time': round(avg_review_time, 2)
    })


@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export applications to CSV"""
    applications = load_applications()

    if not applications:
        return jsonify({'success': False, 'error': 'No applications to export'}), 400

    apps = list(applications.values())

    # Create DataFrame
    df = pd.DataFrame([{
        'ID': app['id'],
        'Full Name': app['full_name'],
        'Email': app['email'],
        'Username': app['username'],
        'Reason': app['reason'],
        'Experience': app['experience'],
        'Status': app['status'],
        'Submitted At': app['submitted_at'],
        'Reviewed At': app.get('reviewed_at', 'N/A'),
        'Reviewer': app.get('reviewer_id', 'N/A'),
        'Review Notes': app.get('review_notes', 'N/A')
    } for app in apps])

    # Create CSV in memory
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    # Convert to BytesIO for sending
    bytes_output = BytesIO(output.getvalue().encode('utf-8'))
    bytes_output.seek(0)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'applications_{timestamp}.csv'

    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    """Export applications to Excel"""
    applications = load_applications()

    if not applications:
        return jsonify({'success': False, 'error': 'No applications to export'}), 400

    apps = list(applications.values())

    # Create DataFrame
    df = pd.DataFrame([{
        'ID': app['id'],
        'Full Name': app['full_name'],
        'Email': app['email'],
        'Username': app['username'],
        'Reason': app['reason'],
        'Experience': app['experience'],
        'Status': app['status'],
        'Submitted At': app['submitted_at'],
        'Reviewed At': app.get('reviewed_at', 'N/A'),
        'Reviewer': app.get('reviewer_id', 'N/A'),
        'Review Notes': app.get('review_notes', 'N/A')
    } for app in apps])

    # Create Excel in memory
    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'applications_{timestamp}.xlsx'

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    """Get pending reminders"""
    applications = load_applications()

    pending_apps = [app for app in applications.values() if app.get('status') == 'pending']
    pending_apps.sort(key=lambda x: x.get('submitted_at', ''))

    reminders = []
    for app in pending_apps:
        try:
            submitted = datetime.fromisoformat(app['submitted_at'])
            hours_pending = (datetime.now() - submitted).total_seconds() / 3600
            reminders.append({
                'id': app['id'],
                'applicant': app['full_name'],
                'email': app['email'],
                'hours_pending': round(hours_pending, 1),
                'submitted_at': app['submitted_at']
            })
        except:
            pass

    return jsonify({
        'success': True,
        'reminders': reminders,
        'count': len(reminders)
    })


@app.route('/api/reminders/schedule', methods=['POST'])
def schedule_reminder():
    """Schedule a reminder for pending reviews"""
    data = request.get_json()
    hours = data.get('hours', 24)

    def check_pending():
        applications = load_applications()
        pending_apps = [app for app in applications.values() if app.get('status') == 'pending']

        if pending_apps:
            print(f"⏰ REMINDER: {len(pending_apps)} applications pending review")
            for app in pending_apps:
                try:
                    submitted = datetime.fromisoformat(app['submitted_at'])
                    hours_pending = (datetime.now() - submitted).total_seconds() / 3600
                    print(f"  - {app['full_name']} ({app['email']}) - Pending for {hours_pending:.1f} hours")
                except:
                    pass

    # Schedule the job
    schedule.every(hours).hours.do(check_pending)

    return jsonify({
        'success': True,
        'message': f'Reminder scheduled every {hours} hours',
        'next_check': datetime.now().timestamp()
    })


def run_scheduler():
    """Run scheduler in background thread"""
    while True:
        schedule.run_pending()
        time.sleep(60)


# Start scheduler thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()


if __name__ == '__main__':
    print("Starting Application Dashboard on http://localhost:5000")
    app.run(debug=True, port=5000)
