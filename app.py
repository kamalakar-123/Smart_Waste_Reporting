import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, init_db, close_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'change-this-secret-for-production'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.context_processor
def inject_now():
    # Provides `now()` in templates for current year / timestamps
    return {'now': datetime.utcnow}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Some Flask versions may not have `before_first_request` available in the same way.
# Initialize the database immediately within the app context so tables are present.
with app.app_context():
    init_db()

# Ensure DB connections are closed after each request
app.teardown_appcontext(close_connection)


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def role_required(role):
    from functools import wraps

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session.get('role') != role:
                flash('Unauthorized access.', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def get_user_counts(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT COUNT(*) FROM complaints WHERE user_id=?', (user_id,))
    total = cur.fetchone()[0]
    # Count in-progress (accepted/in progress) separately from pending submissions
    cur.execute("SELECT COUNT(*) FROM complaints WHERE user_id=? AND status IN ('Accepted','In Progress')", (user_id,))
    in_progress = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM complaints WHERE user_id=? AND status='Completed'", (user_id,))
    completed = cur.fetchone()[0]
    return total, in_progress, completed


def get_worker_counts(worker_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM complaints WHERE status IN ('Pending','Accepted','In Progress')")
    open_count = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM complaints WHERE worker_id=? AND status="Completed"', (worker_id,))
    completed = cur.fetchone()[0]
    return open_count, completed


@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'worker':
            return redirect(url_for('worker_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')

        if not (username and email and password and role):
            flash('Please fill all required fields.', 'warning')
            return render_template('register.html')

        if password != confirm_password:
            flash('Password and confirm password do not match.', 'warning')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute('INSERT INTO users (username, email, phone, password_hash, role, created_at) VALUES (?,?,?,?,?,?)',
                        (username, email, phone, password_hash, role, datetime.utcnow()))
            db.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM users WHERE email=?', (email,))
        user = cur.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/user/dashboard')
@login_required
@role_required('user')
def user_dashboard():
    user_id = session['user_id']
    total, in_progress, completed = get_user_counts(user_id)
    return render_template('user_dashboard.html', total=total, in_progress=in_progress, completed=completed)


@app.route('/complaints/new')
@login_required
@role_required('user')
def new_complaint():
    return render_template('complaint_form.html')


@app.route('/complaints/create', methods=['POST'])
@login_required
@role_required('user')
def create_complaint():
    description = request.form.get('description')
    latitude = request.form.get('latitude') or None
    longitude = request.form.get('longitude') or None
    # The before image was made optional. If provided, save it; otherwise use empty string.
    file = request.files.get('image_before')
    if not description:
        flash('Description is required.', 'warning')
        return redirect(url_for('new_complaint'))

    rel_path = ''
    if file and file.filename != '':
        if allowed_file(file.filename):
            filename = secure_filename(f"before_{int(datetime.utcnow().timestamp())}_{file.filename}")
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            # Use POSIX-style path for URLs (works cross-platform)
            rel_path = f"static/uploads/{filename}"
        else:
            flash('Invalid image file.', 'danger')
            return redirect(url_for('new_complaint'))
        db = get_db()
        cur = db.cursor()
        cur.execute('INSERT INTO complaints (user_id, description, image_before_path, latitude, longitude, status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)',
                (session['user_id'], description, rel_path, latitude, longitude, 'Pending', datetime.utcnow(), datetime.utcnow()))
        db.commit()
        flash('Complaint submitted successfully.', 'success')
        return redirect(url_for('my_complaints'))
    else:
        flash('Invalid image file.', 'danger')
        return redirect(url_for('new_complaint'))


@app.route('/complaints/my')
@login_required
@role_required('user')
def my_complaints():
    db = get_db()
    cur = db.cursor()
    # Optional status filter: ?status=Pending|Accepted|In Progress|Completed
    status = request.args.get('status')
    if status:
        # Treat 'Pending' filter as open statuses (Pending, Accepted, In Progress)
        s = status.strip().lower()
        if s == 'pending' or s == 'open':
            cur.execute("SELECT * FROM complaints WHERE user_id=? AND status IN ('Pending','Accepted','In Progress') ORDER BY created_at DESC", (session['user_id'],))
        else:
            cur.execute('SELECT * FROM complaints WHERE user_id=? AND status=? ORDER BY created_at DESC', (session['user_id'], status))
    else:
        cur.execute('SELECT * FROM complaints WHERE user_id=? ORDER BY created_at DESC', (session['user_id'],))
    complaints = cur.fetchall()
    return render_template('my_complaints.html', complaints=complaints)


@app.route('/complaints/<int:cid>')
@login_required
def complaint_detail(cid):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT c.*, u.username as reporter FROM complaints c JOIN users u ON c.user_id=u.id WHERE c.id=?', (cid,))
    complaint = cur.fetchone()
    if complaint is None:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('index'))

    # Allow any logged-in user (owner or not) to view complaint details so users
    # can see each other's reports from the public page.
    return render_template('complaint_detail.html', complaint=complaint)


@app.route('/reports/public')
def public_reports():
    db = get_db()
    cur = db.cursor()
    # Show all reports publicly; optional ?status=Completed to filter
    status = request.args.get('status')
    if status:
        cur.execute("SELECT c.*, u.username as reporter FROM complaints c JOIN users u ON c.user_id=u.id WHERE c.status=? ORDER BY c.created_at DESC", (status,))
    else:
        cur.execute("SELECT c.*, u.username as reporter FROM complaints c JOIN users u ON c.user_id=u.id ORDER BY c.created_at DESC")
    reports = cur.fetchall()
    return render_template('public_reports.html', reports=reports)


@app.route('/worker/dashboard')
@login_required
@role_required('worker')
def worker_dashboard():
    worker_id = session['user_id']
    open_count, completed = get_worker_counts(worker_id)
    return render_template('worker_dashboard.html', open_count=open_count, completed=completed)


@app.route('/profile')
@login_required
def profile():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id, username, email, phone, role, created_at FROM users WHERE id=?', (session['user_id'],))
    user = cur.fetchone()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('index'))
    return render_template('profile.html', user=user)


@app.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    current = request.form.get('current_password')
    newpw = request.form.get('new_password')
    if not current or not newpw:
        flash('Please provide both current and new passwords.', 'warning')
        return redirect(url_for('profile'))
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT password_hash FROM users WHERE id=?', (session['user_id'],))
    row = cur.fetchone()
    if not row or not check_password_hash(row['password_hash'], current):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('profile'))
    new_hash = generate_password_hash(newpw)
    cur.execute('UPDATE users SET password_hash=? WHERE id=?', (new_hash, session['user_id']))
    db.commit()
    flash('Password updated successfully.', 'success')
    return redirect(url_for('profile'))


def _remove_file_if_exists(path):
    try:
        # path stored as 'static/uploads/filename'
        if path:
            fp = os.path.join(BASE_DIR, path.replace('/', os.sep))
            if os.path.exists(fp):
                os.remove(fp)
    except Exception:
        pass


@app.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    user_id = session['user_id']
    db = get_db()
    cur = db.cursor()
    # Delete related complaint images from disk
    cur.execute('SELECT image_before_path, image_after_path FROM complaints WHERE user_id=?', (user_id,))
    rows = cur.fetchall()
    for r in rows:
        if r['image_before_path']:
            _remove_file_if_exists(r['image_before_path'])
        if r['image_after_path']:
            _remove_file_if_exists(r['image_after_path'])
    # Delete complaints
    cur.execute('DELETE FROM complaints WHERE user_id=?', (user_id,))
    # Delete user
    cur.execute('DELETE FROM users WHERE id=?', (user_id,))
    db.commit()
    session.clear()
    flash('Your account and related complaints have been deleted.', 'info')
    return redirect(url_for('login'))


@app.route('/worker/complaints/open')
@login_required
@role_required('worker')
def worker_open_complaints():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT c.*, u.username as reporter FROM complaints c JOIN users u ON c.user_id=u.id WHERE c.status IN ('Pending','Accepted','In Progress') ORDER BY c.created_at ASC")
    complaints = cur.fetchall()
    return render_template('worker_open_complaints.html', complaints=complaints)


@app.route('/worker/complaints/completed')
@login_required
@role_required('worker')
def worker_completed_complaints():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT c.*, u.username as reporter FROM complaints c JOIN users u ON c.user_id=u.id WHERE c.status='Completed' AND c.worker_id=? ORDER BY c.updated_at DESC", (session['user_id'],))
    complaints = cur.fetchall()
    return render_template('worker_completed_complaints.html', complaints=complaints)


@app.route('/worker/complaints/<int:cid>', methods=['GET'])
@login_required
@role_required('worker')
def worker_complaint_view(cid):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT c.*, u.username as reporter FROM complaints c JOIN users u ON c.user_id=u.id WHERE c.id=?', (cid,))
    complaint = cur.fetchone()
    if complaint is None:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('worker_open_complaints'))
    return render_template('worker_complaint_detail.html', complaint=complaint)


@app.route('/worker/complaints/<int:cid>/update', methods=['POST'])
@login_required
@role_required('worker')
def worker_update(cid):
    new_status = request.form.get('status')
    after_file = request.files.get('image_after')
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM complaints WHERE id=?', (cid,))
    complaint = cur.fetchone()
    if complaint is None:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('worker_open_complaints'))

    # Assign worker for accepted/in-progress/completed
    worker_id = session['user_id']

    if new_status == 'Completed':
        if not after_file or after_file.filename == '':
            flash('Please upload after-cleaning image when marking Completed.', 'warning')
            return redirect(url_for('worker_complaint_view', cid=cid))
        if after_file and allowed_file(after_file.filename):
            filename = secure_filename(f"after_{int(datetime.utcnow().timestamp())}_{after_file.filename}")
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            after_file.save(save_path)
            rel_path = f"static/uploads/{filename}"
            cur.execute('UPDATE complaints SET status=?, image_after_path=?, worker_id=?, updated_at=? WHERE id=?',
                        (new_status, rel_path, worker_id, datetime.utcnow(), cid))
            db.commit()
            flash('Complaint marked as Completed.', 'success')
            return redirect(url_for('worker_open_complaints'))
        else:
            flash('Invalid after image file.', 'danger')
            return redirect(url_for('worker_complaint_view', cid=cid))
    else:
        # Update status and set worker if accepting
        cur.execute('UPDATE complaints SET status=?, worker_id=?, updated_at=? WHERE id=?',
                    (new_status, worker_id, datetime.utcnow(), cid))
        db.commit()
        flash('Status updated.', 'success')
        return redirect(url_for('worker_open_complaints'))


if __name__ == '__main__':
    # Close DB connection after each request
    app.teardown_appcontext(close_connection)
    app.run(debug=True)
