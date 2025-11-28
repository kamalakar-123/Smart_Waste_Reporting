import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, init_db, close_connection
from admin_config import is_admin_email, get_user_role

# Import Firebase admin config (optional - will work without it)
try:
    from firebase_admin_config import verify_firebase_token
    FIREBASE_ENABLED = True
except Exception as e:
    print(f"Firebase Admin not available: {e}")
    FIREBASE_ENABLED = False
    def verify_firebase_token(token):
        return None

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


def get_admin_stats():
    db = get_db()
    cur = db.cursor()
    
    # Total complaints
    cur.execute('SELECT COUNT(*) FROM complaints')
    total_complaints = cur.fetchone()[0]
    
    # Total users (excluding workers and admins)
    cur.execute('SELECT COUNT(*) FROM users WHERE role="user"')
    total_users = cur.fetchone()[0]
    
    # Total workers
    cur.execute('SELECT COUNT(*) FROM users WHERE role="worker"')
    total_workers = cur.fetchone()[0]
    
    # Pending complaints
    cur.execute('SELECT COUNT(*) FROM complaints WHERE status="Pending"')
    pending = cur.fetchone()[0]
    
    # In Progress complaints
    cur.execute('SELECT COUNT(*) FROM complaints WHERE status IN ("Accepted", "In Progress")')
    in_progress = cur.fetchone()[0]
    
    # Completed complaints
    cur.execute('SELECT COUNT(*) FROM complaints WHERE status="Completed"')
    completed = cur.fetchone()[0]
    
    return {
        'total_complaints': total_complaints,
        'total_users': total_users,
        'total_workers': total_workers,
        'pending': pending,
        'in_progress': in_progress,
        'completed': completed
    }


@app.route('/admin/reports')
@login_required
@role_required('admin')
def admin_reports():
    db = get_db()
    cur = db.cursor()
    # filter param: pending | inprogress | completed | all
    f = (request.args.get('filter') or '').strip().lower()
    if f == 'pending':
        cur.execute("SELECT c.*, u.username as reporter FROM complaints c JOIN users u ON c.user_id=u.id WHERE c.status='Pending' ORDER BY c.created_at DESC")
    elif f == 'inprogress':
        cur.execute("SELECT c.*, u.username as reporter FROM complaints c JOIN users u ON c.user_id=u.id WHERE c.status IN ('Accepted','In Progress') ORDER BY c.created_at DESC")
    elif f == 'completed':
        cur.execute("SELECT c.*, u.username as reporter FROM complaints c JOIN users u ON c.user_id=u.id WHERE c.status='Completed' ORDER BY c.updated_at DESC")
    else:
        cur.execute("SELECT c.*, u.username as reporter FROM complaints c JOIN users u ON c.user_id=u.id ORDER BY c.created_at DESC")
    reports = cur.fetchall()
    return render_template('admin_reports.html', reports=reports, filter=f)


@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, username, email, phone, role, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    return render_template('admin_users.html', users=users)


@app.route('/admin/workers')
@login_required
@role_required('admin')
def admin_workers():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, username, email, phone, role, created_at FROM users WHERE role='worker' ORDER BY created_at DESC")
    workers = cur.fetchall()
    return render_template('admin_workers.html', workers=workers)


@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session.get('role') == 'worker':
            return redirect(url_for('worker_dashboard'))
        else:
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
        role = 'user'  # Default role for all new registrations

        if not (username and email and password):
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
        
        if not email or not password:
            flash('Please enter both email and password.', 'warning')
            return render_template('login.html')
        
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM users WHERE email=?', (email,))
        user = cur.fetchone()
        
        if not user:
            flash('Email not found. Please register first to create an account.', 'warning')
            return render_template('login.html')
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome back, {user["username"]}!', 'success')
            
            # Redirect based on user role
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'worker':
                return redirect(url_for('worker_dashboard'))
            else:  # Default to user dashboard
                return redirect(url_for('user_dashboard'))
        else:
            flash('Incorrect password. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))


# Firebase Authentication API Endpoints
@app.route('/api/firebase-register', methods=['POST'])
def firebase_register():
    """Handle Firebase user registration and sync with local database"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone', '')
        firebase_uid = data.get('firebase_uid')
        
        if not all([id_token, username, email, firebase_uid]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # Automatically determine role based on email
        role = get_user_role(email)
        
        # Verify Firebase token (optional in development)
        if FIREBASE_ENABLED:
            try:
                decoded_token = verify_firebase_token(id_token)
                if decoded_token and decoded_token.get('uid') != firebase_uid:
                    return jsonify({'success': False, 'message': 'Token UID mismatch'}), 401
            except Exception as e:
                print(f"Token verification warning (continuing anyway): {e}")
                # Continue without verification in development
        
        # Store user in local database
        db = get_db()
        cur = db.cursor()
        
        try:
            # Check if user already exists
            cur.execute('SELECT id FROM users WHERE email=?', (email,))
            existing_user = cur.fetchone()
            
            if existing_user:
                return jsonify({'success': False, 'message': 'Email already registered'}), 400
            
            # Insert new user with Firebase UID and auto-determined role
            cur.execute(
                'INSERT INTO users (username, email, phone, password_hash, role, created_at, firebase_uid) VALUES (?,?,?,?,?,?,?)',
                (username, email, phone, '', role, datetime.utcnow(), firebase_uid)
            )
            db.commit()
            
            success_message = 'Registration successful'
            if role == 'admin':
                success_message = 'Admin account created successfully'
            
            return jsonify({
                'success': True,
                'message': success_message,
                'redirect_url': '/login',
                'role': role
            }), 200
            
        except sqlite3.IntegrityError as e:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        except Exception as e:
            print(f"Database error: {e}")
            return jsonify({'success': False, 'message': 'Database error occurred'}), 500
            
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/legacy-login', methods=['POST'])
def legacy_login():
    """Handle login for users registered before Firebase integration"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'success': False, 'message': 'Missing email or password'}), 400
        
        # Check if user exists in database
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM users WHERE email=?', (email,))
        user = cur.fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Verify password using werkzeug
        from werkzeug.security import check_password_hash
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'success': False, 'message': 'Invalid password'}), 401
        
        # Check if user has firebase_uid (already migrated)
        if user.get('firebase_uid'):
            return jsonify({'success': False, 'message': 'This account has been migrated. Please use the regular login.'}), 400
        
        # Set session for legacy user
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        session['needs_migration'] = True  # Flag for migration warning
        
        # Determine redirect URL based on role
        if user['role'] == 'admin':
            redirect_url = url_for('admin_dashboard')
        elif user['role'] == 'worker':
            redirect_url = url_for('worker_dashboard')
        else:
            redirect_url = url_for('user_dashboard')
        
        return jsonify({
            'success': True,
            'message': 'Legacy login successful - migration recommended',
            'redirect_url': redirect_url,
            'needs_migration': True
        }), 200
        
    except Exception as e:
        print(f"Legacy login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/firebase-login', methods=['POST'])
def firebase_login():
    """Handle Firebase login and sync with local session"""
    try:
        data = request.get_json()
        id_token = data.get('idToken')
        email = data.get('email')
        is_google_auth = data.get('is_google_auth', False)
        username = data.get('username')
        firebase_uid = data.get('firebase_uid')
        
        if not all([id_token, email]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        # Verify Firebase token (optional in development)
        decoded_token = None
        if FIREBASE_ENABLED:
            try:
                decoded_token = verify_firebase_token(id_token)
            except Exception as e:
                print(f"Token verification warning (continuing anyway): {e}")
                # Continue without verification in development
        
        # Get or create user in local database
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM users WHERE email=?', (email,))
        user = cur.fetchone()
        
        # Determine the correct role based on email
        correct_role = get_user_role(email)
        
        # If user doesn't exist and it's Google auth, create the user
        if not user and is_google_auth:
            try:
                cur.execute(
                    'INSERT INTO users (username, email, phone, password_hash, role, created_at, firebase_uid) VALUES (?,?,?,?,?,?,?)',
                    (username or email.split('@')[0], email, '', '', correct_role, datetime.utcnow(), firebase_uid)
                )
                db.commit()
                
                # Fetch the newly created user
                cur.execute('SELECT * FROM users WHERE email=?', (email,))
                user = cur.fetchone()
            except Exception as e:
                print(f"Error creating Google user: {e}")
                return jsonify({'success': False, 'message': 'Failed to create user account'}), 500
        
        if not user:
            return jsonify({'success': False, 'message': 'Email not found. Please register first.'}), 404
        
        # Update role if it doesn't match the admin list
        if user['role'] != correct_role:
            try:
                cur.execute('UPDATE users SET role=? WHERE id=?', (correct_role, user['id']))
                db.commit()
                # Update the user dict
                user = dict(user)
                user['role'] = correct_role
            except Exception as e:
                print(f"Error updating user role: {e}")
        
        # Update Firebase UID if not set
        if firebase_uid and not user.get('firebase_uid'):
            try:
                cur.execute('UPDATE users SET firebase_uid=? WHERE id=?', (firebase_uid, user['id']))
                db.commit()
            except Exception as e:
                print(f"Error updating Firebase UID: {e}")
        
        # Set session with the correct role
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        
        # Determine redirect URL based on role
        if user['role'] == 'admin':
            redirect_url = url_for('admin_dashboard')
        elif user['role'] == 'worker':
            redirect_url = url_for('worker_dashboard')
        else:
            redirect_url = url_for('user_dashboard')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'redirect_url': redirect_url,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# Worker Management API Endpoints (Admin Only)
@app.route('/api/admin/add-worker', methods=['POST'])
@login_required
def add_worker():
    """Admin endpoint to create a new worker account"""
    # Verify admin role
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized. Admin access required.'}), 403
    
    try:
        data = request.get_json()
        worker_name = data.get('name')
        worker_email = data.get('email')
        worker_password = data.get('password')
        worker_phone = data.get('phone', '')
        
        if not all([worker_name, worker_email, worker_password]):
            return jsonify({'success': False, 'message': 'Name, email, and password are required'}), 400
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, worker_email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        # Check if email already exists
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT id FROM users WHERE email=?', (worker_email,))
        existing_user = cur.fetchone()
        
        if existing_user:
            return jsonify({'success': False, 'message': 'Email already exists in the system'}), 400
        
        # Hash password for local storage (backup)
        password_hash = generate_password_hash(worker_password)
        
        # Create worker in local database
        try:
            cur.execute(
                'INSERT INTO users (username, email, phone, password_hash, role, created_at) VALUES (?,?,?,?,?,?)',
                (worker_name, worker_email, worker_phone, password_hash, 'worker', datetime.utcnow())
            )
            db.commit()
            worker_id = cur.lastrowid
            
            return jsonify({
                'success': True,
                'message': f'Worker account created successfully for {worker_name}',
                'worker': {
                    'id': worker_id,
                    'name': worker_name,
                    'email': worker_email,
                    'phone': worker_phone
                }
            }), 200
            
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
            
    except Exception as e:
        print(f"Add worker error: {e}")
        return jsonify({'success': False, 'message': f'Error creating worker: {str(e)}'}), 500


@app.route('/api/admin/workers', methods=['GET'])
@login_required
def get_workers():
    """Admin endpoint to get list of all workers"""
    # Verify admin role
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized. Admin access required.'}), 403
    
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute('''
            SELECT u.id, u.username, u.email, u.phone, u.created_at,
                   COUNT(DISTINCT c.id) as total_completed
            FROM users u
            LEFT JOIN complaints c ON u.id = c.worker_id AND c.status = 'Completed'
            WHERE u.role = 'worker'
            GROUP BY u.id
            ORDER BY u.created_at DESC
        ''')
        workers = cur.fetchall()
        
        workers_list = []
        for worker in workers:
            workers_list.append({
                'id': worker['id'],
                'name': worker['username'],
                'email': worker['email'],
                'phone': worker['phone'] or 'N/A',
                'created_at': worker['created_at'],
                'completed_tasks': worker['total_completed']
            })
        
        return jsonify({
            'success': True,
            'workers': workers_list,
            'total': len(workers_list)
        }), 200
        
    except Exception as e:
        print(f"Get workers error: {e}")
        return jsonify({'success': False, 'message': f'Error fetching workers: {str(e)}'}), 500


@app.route('/api/admin/remove-worker/<int:worker_id>', methods=['DELETE'])
@login_required
def remove_worker(worker_id):
    """Admin endpoint to remove a worker account"""
    # Verify admin role
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized. Admin access required.'}), 403
    
    try:
        db = get_db()
        cur = db.cursor()
        
        # Check if worker exists and is actually a worker (without firebase_uid to avoid column error)
        cur.execute('SELECT id, username, email, role FROM users WHERE id=?', (worker_id,))
        worker = cur.fetchone()
        
        if not worker:
            return jsonify({'success': False, 'message': 'Worker not found'}), 404
        
        if worker['role'] != 'worker':
            return jsonify({'success': False, 'message': 'User is not a worker'}), 400
        
        # Check if worker has any assigned complaints
        try:
            cur.execute('SELECT COUNT(*) as count FROM complaints WHERE worker_id=? AND status != "Completed"', (worker_id,))
            result = cur.fetchone()
            active_complaints = result['count'] if result else 0
        except Exception as e:
            print(f"Error checking complaints: {e}")
            active_complaints = 0
        
        if active_complaints > 0:
            return jsonify({
                'success': False, 
                'message': f'Cannot remove worker. They have {active_complaints} active complaint(s). Please reassign or complete them first.'
            }), 400
        
        # Delete worker from database
        cur.execute('DELETE FROM users WHERE id=?', (worker_id,))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f'Worker {worker["username"]} has been removed successfully'
        }), 200
        
    except Exception as e:
        print(f"Remove worker error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error removing worker: {str(e)}'}), 500


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


@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    stats = get_admin_stats()
    return render_template('admin_dashboard.html', **stats)


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
