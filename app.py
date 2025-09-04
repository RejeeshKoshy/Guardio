import os
import base64
import io
import hashlib
import json
from datetime import datetime
from dotenv import load_dotenv
from functools import wraps

from flask import Flask, render_template, redirect, url_for, request, flash, send_file, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from cryptography.fernet import Fernet
import google.generativeai as genai

import pyotp
import qrcode

load_dotenv()

# --- App Initialization and Configuration ---

app = Flask(__name__)

# Load keys from environment variables
SECRET_KEY = os.getenv('SECRET_KEY')
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not all([SECRET_KEY, ENCRYPTION_KEY, GEMINI_API_KEY]):
    raise ValueError("One or more required environment variables are not set.")

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mfa_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_timeout': 30}


# --- AI and Encryption Setup ---
fernet = Fernet(ENCRYPTION_KEY.encode())
genai.configure(api_key=GEMINI_API_KEY)

# --- Extensions Initialization ---
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- RBAC Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def analyze_file_with_ai(file_data, filename):
    """Sends file content to Gemini for analysis."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        content_preview = file_data.decode('utf-8', errors='ignore')
        prompt = f"Analyze the following file content from a file named '{filename}'. Provide a one-sentence summary and state if it appears safe or potentially malicious. Content preview: {content_preview[:2000]}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AI analysis failed: {e}")
        return "AI analysis could not be performed due to an error."

# --- Blockchain-Inspired Audit Trail Functions ---

def create_audit_block(user_id, action, details):
    """Create a new audit block and add it to the chain"""
    try:
        # Get the last block for this user
        last_block = AuditBlock.query.filter_by(user_id=user_id).order_by(AuditBlock.id.desc()).first()
        
        # If this is the first block for this user, create a genesis block first
        if not last_block:
            # Create genesis block
            genesis_block = AuditBlock(user_id, "genesis_block", "Initial block in the audit chain", None)
            genesis_block.mine_block(difficulty=2)
            db.session.add(genesis_block)
            db.session.commit()
            
            # Update last_block to the genesis block
            last_block = genesis_block
        
        # Create new block
        new_block = AuditBlock(user_id, action, details, last_block)
        
        # Mine the block (simple proof-of-work)
        new_block.mine_block(difficulty=2)  # Reduced difficulty for demo
        
        # Save to database
        db.session.add(new_block)
        db.session.commit()
        
        return new_block
    except Exception as e:
        print(f"Error creating audit block: {e}")
        return None

def validate_audit_chain(user_id):
    """Validate the entire audit chain for a user"""
    blocks = AuditBlock.query.filter_by(user_id=user_id).order_by(AuditBlock.id.asc()).all()
    
    if not blocks:
        return False, "No audit blocks found - chain not initialized", []
    
    validation_results = []
    previous_block = None
    
    for i, block in enumerate(blocks):
        # For genesis block, previous_block should be None
        if block.action == "genesis_block":
            is_valid, message = block.is_valid(None)
        else:
            is_valid, message = block.is_valid(previous_block)
            
        validation_results.append({
            'block_id': block.id,
            'is_valid': is_valid,
            'message': message,
            'block_hash': block.block_hash[:16] + "...",  # Truncated for display
            'action': block.action,
            'timestamp': block.timestamp.isoformat()
        })
        
        if not is_valid:
            return False, f"Chain validation failed at block {block.id}: {message}", validation_results
        
        previous_block = block
    
    return True, "Chain is valid", validation_results

def get_audit_chain_summary(user_id):
    """Get a summary of the audit chain for a user"""
    blocks = AuditBlock.query.filter_by(user_id=user_id).order_by(AuditBlock.id.desc()).limit(10).all()
    total_blocks = AuditBlock.query.filter_by(user_id=user_id).count()
    
    summary = {
        'total_blocks': total_blocks,
        'chain_valid': False,
        'recent_blocks': []
    }
    
    # If no blocks exist, chain is not initialized
    if total_blocks == 0:
        summary['chain_valid'] = False
        summary['validation_message'] = "No audit blocks found - chain not initialized"
        return summary
    
    # Validate chain
    try:
        is_valid, message, _ = validate_audit_chain(user_id)
        summary['chain_valid'] = is_valid
        summary['validation_message'] = message
    except Exception as e:
        summary['chain_valid'] = False
        summary['validation_message'] = f"Validation error: {str(e)}"
    
    # Get recent blocks (excluding genesis block from display)
    for block in blocks:
        # Skip genesis block from recent actions display
        if block.action == "genesis_block":
            continue
            
        try:
            details = json.loads(block.details) if block.details.startswith('{') else block.details
        except:
            details = block.details
            
        summary['recent_blocks'].append({
            'id': block.id,
            'action': block.action,
            'timestamp': block.timestamp.isoformat(),
            'hash_preview': block.block_hash[:16] + "...",
            'details': details
        })
    
    return summary

def detect_tampering():
    """Check all user chains for tampering"""
    users = User.query.all()
    tampering_report = {
        'total_users': len(users),
        'tampered_chains': [],
        'valid_chains': [],
        'overall_status': 'SECURE'
    }
    
    for user in users:
        try:
            is_valid, message, _ = validate_audit_chain(user.id)
            user_report = {
                'user_id': user.id,
                'username': user.username,
                'is_valid': is_valid,
                'message': message
            }
            
            if is_valid:
                tampering_report['valid_chains'].append(user_report)
            else:
                tampering_report['tampered_chains'].append(user_report)
                tampering_report['overall_status'] = 'TAMPERED'
        except Exception as e:
            # Handle any errors in validation
            user_report = {
                'user_id': user.id,
                'username': user.username,
                'is_valid': False,
                'message': f"Validation error: {str(e)}"
            }
            tampering_report['tampered_chains'].append(user_report)
            tampering_report['overall_status'] = 'TAMPERED'
    
    return tampering_report
# --- Database Models ---

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    otp_secret = db.Column(db.String(16), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    files = db.relationship('File', backref='owner', lazy=True, cascade="all, delete-orphan")
    folders = db.relationship('Folder', backref='owner', lazy=True, cascade="all, delete-orphan")
    password_entries = db.relationship('PasswordEntry', backref='owner', lazy=True, cascade="all, delete-orphan")

class Folder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    parent = db.relationship('Folder', remote_side=[id], backref='subfolders')
    files = db.relationship('File', backref='folder', lazy='dynamic', cascade="all, delete-orphan")

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ai_summary = db.Column(db.Text, nullable=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True)

class PasswordEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    encrypted_password = db.Column(db.LargeBinary, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class AuditBlock(db.Model):
    """Blockchain-inspired audit trail block"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    block_hash = db.Column(db.String(64), unique=True, nullable=False)  # SHA-256 hash
    previous_hash = db.Column(db.String(64), nullable=True)  # Hash of previous block
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    action = db.Column(db.String(100), nullable=False)  # e.g., 'file_upload', 'file_delete', 'password_add'
    details = db.Column(db.Text, nullable=False)  # JSON string with action details
    nonce = db.Column(db.Integer, default=0)  # For proof-of-work (simplified)
    
    # Relationships
    user = db.relationship('User', backref='audit_blocks')
    
    def __init__(self, user_id, action, details, previous_block=None):
        self.user_id = user_id
        self.action = action
        self.details = json.dumps(details) if isinstance(details, dict) else str(details)
        self.previous_hash = previous_block.block_hash if previous_block else None
        self.timestamp = datetime.utcnow()
        self.nonce = 0  # Initialize nonce to 0
        self.block_hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Calculate SHA-256 hash of the block"""
        block_string = f"{self.user_id}{self.previous_hash}{self.timestamp.isoformat()}{self.action}{self.details}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty=4):
        """Simple proof-of-work mining (find hash starting with zeros)"""
        target = "0" * difficulty
        while self.block_hash[:difficulty] != target:
            self.nonce += 1
            self.block_hash = self.calculate_hash()
    
    def is_valid(self, previous_block=None):
        """Validate the block's integrity"""
        # Check if hash is correct
        if self.block_hash != self.calculate_hash():
            return False, "Invalid block hash"
        
        # Check if previous hash matches (for chaining)
        if previous_block and self.previous_hash != previous_block.block_hash:
            return False, "Previous hash mismatch"
        
        # Check if this is the genesis block
        if not previous_block and self.previous_hash is not None:
            return False, "Genesis block should have null previous hash"
        
        return True, "Valid block"
    
    def to_dict(self):
        """Convert block to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'block_hash': self.block_hash,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp.isoformat(),
            'action': self.action,
            'details': json.loads(self.details) if self.details.startswith('{') else self.details,
            'nonce': self.nonce
        }


# --- Flask-Login User Loader ---

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Standard Routes (Login, Signup, etc.) ---

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # FIX: Separate checks for username and email to handle blank emails correctly
        user_by_username = User.query.filter_by(username=username).first()
        if user_by_username:
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('signup'))

        # Only check for email uniqueness if an email is provided
        if email:
            user_by_email = User.query.filter_by(email=email).first()
            if user_by_email:
                flash('Email already exists. Please choose another.', 'danger')
                return redirect(url_for('signup'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        otp_secret = pyotp.random_base32()
        
        role = 'admin' if User.query.count() == 0 else 'user'

        new_user = User(
            username=username, 
            password_hash=hashed_password, 
            email=email, 
            otp_secret=otp_secret,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        # Create genesis audit block for new user
        audit_details = {
            'username': username,
            'email': email,
            'role': role,
            'mfa_enabled': True
        }
        create_audit_block(new_user.id, 'user_registration', audit_details)

        flash(f'Account created successfully! Your role is: {role}. Please set up MFA.', 'success')

        provisioning_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(name=username, issuer_name='FlaskMFAApp')
        qr_img = qrcode.make(provisioning_uri)
        buffered = io.BytesIO()
        qr_img.save(buffered, format="PNG")
        qr_code_img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return render_template('show_qr.html', qr_code_img=qr_code_img_str)
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        otp = request.form.get('otp')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            totp = pyotp.TOTP(user.otp_secret)
            if totp.verify(otp):
                login_user(user)
                
                # Create audit block for successful login
                audit_details = {
                    'login_method': 'password_mfa',
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', 'Unknown')[:100]
                }
                create_audit_block(user.id, 'user_login', audit_details)
                
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid 2FA token. Please try again.', 'danger')
        else:
            flash('Invalid username or password. Please try again.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

# --- File Manager Routes ---

@app.route('/dashboard', defaults={'folder_id': None}, methods=['GET', 'POST'])
@app.route('/dashboard/folder/<int:folder_id>', methods=['GET', 'POST'])
@login_required
def dashboard(folder_id):
    current_folder = None
    if folder_id:
        current_folder = Folder.query.get_or_404(folder_id)
        if current_folder.user_id != current_user.id:
            abort(403)

    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        analyze = request.form.get('analyze_file')

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file:
            file_data = file.read()
            encrypted_data = fernet.encrypt(file_data)
            
            ai_summary = None
            if analyze:
                try:
                    decrypted_data_for_ai = fernet.decrypt(encrypted_data)
                    ai_summary = analyze_file_with_ai(decrypted_data_for_ai, file.filename)
                except Exception as e:
                    ai_summary = f"Could not perform AI analysis. Error: {e}"

            new_file = File(
                filename=file.filename,
                data=encrypted_data,
                owner=current_user,
                ai_summary=ai_summary,
                folder_id=folder_id
            )
            db.session.add(new_file)
            db.session.commit()
            
            # Create audit block for file upload
            audit_details = {
                'filename': file.filename,
                'file_size': len(file_data),
                'folder_id': folder_id,
                'ai_analyzed': bool(analyze),
                'ai_summary': ai_summary[:100] + "..." if ai_summary and len(ai_summary) > 100 else ai_summary
            }
            create_audit_block(current_user.id, 'file_upload', audit_details)
            
            flash('File uploaded successfully!', 'success')
        
        return redirect(url_for('dashboard', folder_id=folder_id))

    if current_folder:
        folders = current_folder.subfolders
        files = current_folder.files
    else: 
        folders = Folder.query.filter_by(user_id=current_user.id, parent_id=None).all()
        files = File.query.filter_by(user_id=current_user.id, folder_id=None).all()

    return render_template('dashboard.html', files=files, folders=folders, current_folder=current_folder)



@app.route('/create-folder', methods=['POST'])
@login_required
def create_folder():
    """Creates a new folder."""
    folder_name = request.form.get('folder_name')
    parent_folder_id = request.form.get('parent_id')
    
    if not folder_name:
        flash('Folder name cannot be empty.', 'danger')
    else:
        parent_id = int(parent_folder_id) if parent_folder_id else None
        
        new_folder = Folder(
            name=folder_name,
            owner=current_user,
            parent_id=parent_id
        )
        db.session.add(new_folder)
        db.session.commit()
        flash(f'Folder "{folder_name}" created successfully.', 'success')

    if parent_folder_id:
        return redirect(url_for('dashboard', folder_id=parent_folder_id))
    else:
        return redirect(url_for('dashboard'))

@app.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    """Handles file decryption and download."""
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        abort(403)
    try:
        decrypted_data = fernet.decrypt(file.data)
        return send_file(io.BytesIO(decrypted_data), as_attachment=True, download_name=file.filename)
    except Exception:
        flash('Could not decrypt or download the file.', 'danger')
        return redirect(url_for('dashboard', folder_id=file.folder_id))

@app.route('/delete/file/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    file_to_delete = File.query.get_or_404(file_id)
    if file_to_delete.user_id != current_user.id:
        abort(403)
    
    # Create audit block for file deletion
    audit_details = {
        'filename': file_to_delete.filename,
        'file_size': len(file_to_delete.data),
        'folder_id': file_to_delete.folder_id,
        'ai_summary': file_to_delete.ai_summary[:100] + "..." if file_to_delete.ai_summary and len(file_to_delete.ai_summary) > 100 else file_to_delete.ai_summary
    }
    create_audit_block(current_user.id, 'file_delete', audit_details)
    
    parent_folder_id = file_to_delete.folder_id
    db.session.delete(file_to_delete)
    db.session.commit()
    flash('File deleted successfully.', 'success')
    return redirect(url_for('dashboard', folder_id=parent_folder_id))

@app.route('/delete/folder/<int:folder_id>', methods=['POST'])
@login_required
def delete_folder(folder_id):
    folder_to_delete = Folder.query.get_or_404(folder_id)
    if folder_to_delete.user_id != current_user.id:
        abort(403)
    if folder_to_delete.subfolders or folder_to_delete.files.first():
        flash('Cannot delete a non-empty folder.', 'danger')
        return redirect(url_for('dashboard', folder_id=folder_id))
    parent_folder_id = folder_to_delete.parent_id
    db.session.delete(folder_to_delete)
    db.session.commit()
    flash('Folder deleted successfully.', 'success')
    return redirect(url_for('dashboard', folder_id=parent_folder_id))

# --- Password Manager Routes ---

@app.route('/password-manager')
@login_required
def password_manager():
    """Displays the password manager page."""
    entries = PasswordEntry.query.filter_by(user_id=current_user.id).all()
    return render_template('password_manager.html', entries=entries)

@app.route('/add-password', methods=['POST'])
@login_required
def add_password():
    """Adds a new password entry."""
    website = request.form.get('website')
    username = request.form.get('username')
    password = request.form.get('password')

    if not all([website, username, password]):
        flash('All fields are required.', 'danger')
    else:
        encrypted_password = fernet.encrypt(password.encode())
        new_entry = PasswordEntry(
            website=website,
            username=username,
            encrypted_password=encrypted_password,
            owner=current_user
        )
        db.session.add(new_entry)
        db.session.commit()
        
        # Create audit block for password addition
        audit_details = {
            'website': website,
            'username': username,
            'password_length': len(password)
        }
        create_audit_block(current_user.id, 'password_add', audit_details)
        
        flash('Password entry added successfully!', 'success')
    
    return redirect(url_for('password_manager'))

@app.route('/reveal-password/<int:entry_id>')
@login_required
def reveal_password(entry_id):
    """Decrypts and returns a password."""
    entry = PasswordEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        abort(403)
    
    decrypted_password = fernet.decrypt(entry.encrypted_password).decode()
    return jsonify({'password': decrypted_password})

@app.route('/delete-password/<int:entry_id>', methods=['POST'])
@login_required
def delete_password(entry_id):
    """Deletes a password entry."""
    entry = PasswordEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        abort(403)
    
    # Create audit block for password deletion
    audit_details = {
        'website': entry.website,
        'username': entry.username,
        'password_length': len(entry.encrypted_password)
    }
    create_audit_block(current_user.id, 'password_delete', audit_details)
    
    db.session.delete(entry)
    db.session.commit()
    flash('Password entry deleted successfully.', 'success')
    return redirect(url_for('password_manager'))


# --- Admin Routes ---

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Displays the admin dashboard with comprehensive system analytics."""
    users = User.query.all()
    
    # Calculate system statistics
    total_users = len(users)
    admin_users = len([u for u in users if u.role == 'admin'])
    regular_users = total_users - admin_users
    
    # File statistics
    total_files = File.query.count()
    total_folders = Folder.query.count()
    total_password_entries = PasswordEntry.query.count()
    
    # Storage statistics (approximate)
    total_storage_mb = 0
    for file in File.query.all():
        total_storage_mb += len(file.data) / (1024 * 1024)  # Convert bytes to MB
    
    # Recent activity (last 7 days would require timestamps, for now just show counts)
    recent_files = File.query.count()  # In a real app, you'd filter by date
    recent_passwords = PasswordEntry.query.count()
    
    # User activity (files per user)
    user_stats = []
    for user in users:
        file_count = len(user.files)
        folder_count = len(user.folders)
        password_count = len(user.password_entries)
        
        # Get audit chain status
        try:
            audit_summary = get_audit_chain_summary(user.id)
            audit_blocks = audit_summary['total_blocks']
            chain_valid = audit_summary['chain_valid']
        except Exception as e:
            # Handle case when audit system isn't fully set up
            audit_blocks = 0
            chain_valid = False
        
        user_stats.append({
            'user': user,
            'file_count': file_count,
            'folder_count': folder_count,
            'password_count': password_count,
            'audit_blocks': audit_blocks,
            'chain_valid': chain_valid
        })
    
    # Sort users by activity
    user_stats.sort(key=lambda x: x['file_count'] + x['password_count'], reverse=True)
    
    stats = {
        'total_users': total_users,
        'admin_users': admin_users,
        'regular_users': regular_users,
        'total_files': total_files,
        'total_folders': total_folders,
        'total_password_entries': total_password_entries,
        'total_storage_mb': round(total_storage_mb, 2),
        'recent_files': recent_files,
        'recent_passwords': recent_passwords,
        'user_stats': user_stats
    }
    
    return render_template('admin_dashboard.html', users=users, stats=stats)

@app.route('/admin/user/<int:user_id>')
@login_required
@admin_required
def user_details(user_id):
    """Displays the details of a specific user's stored items."""
    user = User.query.get_or_404(user_id)
    
    # Calculate user statistics
    file_count = len(user.files)
    folder_count = len(user.folders)
    password_count = len(user.password_entries)
    
    # Calculate storage usage
    storage_mb = 0
    for file in user.files:
        storage_mb += len(file.data) / (1024 * 1024)
    
    user_stats = {
        'file_count': file_count,
        'folder_count': folder_count,
        'password_count': password_count,
        'storage_mb': round(storage_mb, 2)
    }
    
    return render_template('user_details.html', user=user, user_stats=user_stats)

@app.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active/inactive status."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot modify your own account status.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # For now, we'll add an 'active' field to the User model
    # This would require a database migration in a real app
    flash(f'User status toggle functionality would be implemented here for {user.username}', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    """Change user role between admin and user."""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if user.id == current_user.id:
        flash('You cannot change your own role.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if new_role in ['admin', 'user']:
        user.role = new_role
        db.session.commit()
        flash(f'User {user.username} role changed to {new_role}.', 'success')
    else:
        flash('Invalid role specified.', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user and all their data."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User {username} and all their data have been deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/system-stats')
@login_required
@admin_required
def system_stats():
    """API endpoint for system statistics (for charts)."""
    stats = {
        'users_by_role': {
            'admin': User.query.filter_by(role='admin').count(),
            'user': User.query.filter_by(role='user').count()
        },
        'storage_by_type': {
            'files': File.query.count(),
            'passwords': PasswordEntry.query.count(),
            'folders': Folder.query.count()
        }
    }
    return jsonify(stats)

@app.route('/admin/settings')
@login_required
@admin_required
def admin_settings():
    """System settings management page."""
    # Get current system configuration
    settings = {
        'encryption_enabled': True,
        'ai_analysis_enabled': bool(GEMINI_API_KEY),
        'mfa_required': True,
        'max_file_size_mb': 10,  # This would be configurable
        'allowed_file_types': ['pdf', 'doc', 'docx', 'txt', 'jpg', 'png', 'gif'],
        'system_name': 'Guardio',
        'maintenance_mode': False
    }
    
    return render_template('admin_settings.html', settings=settings)

@app.route('/admin/settings/update', methods=['POST'])
@login_required
@admin_required
def update_system_settings():
    """Update system settings."""
    setting_type = request.form.get('setting_type')
    value = request.form.get('value')
    
    if setting_type == 'maintenance_mode':
        # In a real app, this would update a database setting
        flash(f'Maintenance mode would be {"enabled" if value == "true" else "disabled"}', 'info')
    elif setting_type == 'max_file_size':
        try:
            size_mb = int(value)
            if 1 <= size_mb <= 100:
                flash(f'Maximum file size updated to {size_mb}MB', 'success')
            else:
                flash('File size must be between 1 and 100 MB', 'danger')
        except ValueError:
            flash('Invalid file size value', 'danger')
    else:
        flash('Setting updated successfully', 'success')
    
    return redirect(url_for('admin_settings'))

@app.route('/admin/backup')
@login_required
@admin_required
def admin_backup():
    """Create system backup."""
    # In a real app, this would create a database backup
    flash('System backup functionality would be implemented here', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logs')
@login_required
@admin_required
def admin_logs():
    """View system logs."""
    # In a real application, this would query actual log files or a logging database
    # For now, we'll show a message that logs are not yet implemented
    logs = []
    
    return render_template('admin_logs.html', logs=logs)

@app.route('/admin/audit-trail')
@login_required
@admin_required
def admin_audit_trail():
    """View blockchain-inspired audit trails for all users"""
    try:
        # Get tampering report
        tampering_report = detect_tampering()
        
        # Get audit chain summaries for all users
        users = User.query.all()
        user_audit_summaries = []
        
        for user in users:
            try:
                summary = get_audit_chain_summary(user.id)
                user_audit_summaries.append({
                    'user': user,
                    'audit_summary': summary
                })
            except Exception as e:
                # Handle individual user errors
                user_audit_summaries.append({
                    'user': user,
                    'audit_summary': {
                        'total_blocks': 0,
                        'chain_valid': False,
                        'validation_message': f"Error: {str(e)}",
                        'recent_blocks': []
                    }
                })
        
        return render_template('admin_audit_trail.html', 
                             tampering_report=tampering_report,
                             user_audit_summaries=user_audit_summaries)
    except Exception as e:
        flash(f"Error loading audit trail: {str(e)}", "danger")
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/audit-trail/user/<int:user_id>')
@login_required
@admin_required
def user_audit_chain(user_id):
    """View detailed audit chain for a specific user"""
    user = User.query.get_or_404(user_id)
    
    try:
        # Get all blocks for this user
        blocks = AuditBlock.query.filter_by(user_id=user_id).order_by(AuditBlock.id.asc()).all()
        
        # Validate the chain
        is_valid, message, validation_results = validate_audit_chain(user_id)
        
        return render_template('user_audit_chain.html', 
                             user=user,
                             blocks=blocks,
                             chain_valid=is_valid,
                             validation_message=message,
                             validation_results=validation_results)
    except Exception as e:
        flash(f"Error loading user audit chain: {str(e)}", "danger")
        return redirect(url_for('admin_audit_trail'))

@app.route('/admin/audit-trail/validate-all')
@login_required
@admin_required
def validate_all_chains():
    """Validate all audit chains and return results"""
    try:
        tampering_report = detect_tampering()
        return jsonify(tampering_report)
    except Exception as e:
        return jsonify({
            'error': f"Validation failed: {str(e)}",
            'total_users': 0,
            'tampered_chains': [],
            'valid_chains': [],
            'overall_status': 'ERROR'
        }), 500

@app.route('/admin/audit-trail/block/<int:block_id>')
@login_required
@admin_required
def audit_block_details(block_id):
    """Get detailed information about a specific audit block"""
    block = AuditBlock.query.get_or_404(block_id)
    return jsonify(block.to_dict())


# --- General Routes ---

@app.route('/users')
@login_required
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True)
