# Guardio: Your Private, End-to-End Encrypted Cloud

![Guardio Landing Page](https://placehold.co/1200x600/6D5BDE/FFFFFF?text=Guardio)

**Guardio is a full-stack, security-first web application that gives you total control over your digital life. It combines an encrypted file manager, secure password vault, and blockchain-inspired tamper-evident audit trail, all protected by robust Multi-Factor Authentication (MFA).**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Enterprise--Grade-red.svg)](README.md#security-features)

---

## ✨ Features

Guardio is built on the principle of zero-knowledge privacy. We can't see your data, and no one else can either.

* 🔐 **Multi-Factor Authentication (MFA):** Secure your account beyond just a password. Guardio integrates with standard authenticator apps (like Google Authenticator or Authy) to provide time-based one-time password (TOTP) verification at login.

* 📂 **Encrypted File Manager:**
    * **Upload & Organize:** Upload your sensitive documents, photos, and files. Organize them with a simple and intuitive folder structure.
    * **End-to-End Encryption:** Every file is encrypted on the server with the powerful Fernet (AES-128) symmetric encryption before it's ever written to disk. Your files are stored as unreadable ciphertext.
    * **Secure Downloads:** Files are decrypted in memory only when you request them for download, ensuring your plain data is never exposed on the server.

* 🔑 **Encrypted Password Manager:**
    * **Secure Vault:** Store your website logins, passwords, and usernames in a centralized, secure vault.
    * **Zero-Knowledge:** Just like your files, your passwords are encrypted before being saved. The "Reveal" function decrypts them on-the-fly, only for you.

* 🛡️ **Admin Oversight (RBAC):**
    * The first user to register automatically becomes the **Admin**.
    * Comprehensive admin dashboard with system analytics, user management, and security monitoring.
    * Advanced admin panel provides detailed insights into user activity while respecting privacy.
    * System settings management, backup controls, and real-time monitoring.

* ⛓️ **Blockchain-Inspired Audit Trail:**
    * **Tamper-Evident Logging:** Every critical action creates an immutable audit block using cryptographic hashing.
    * **Chain Integrity:** Blocks are cryptographically linked, making any tampering immediately detectable.
    * **Proof-of-Work:** Simple mining system makes tampering computationally expensive.
    * **Complete Transparency:** Full audit trail of all user actions (file operations, password changes, logins).
    * **Forensic Security:** Even administrators cannot secretly modify audit records without detection.

---

## 🚀 Tech Stack

Guardio is built with a focus on security, reliability, and modern development practices.

| Category      | Technology                               | Purpose                                          |
|---------------|------------------------------------------|--------------------------------------------------|
| **Backend** | Python, Flask                            | Core application logic and routing.              |
| **Database** | SQLite via Flask-SQLAlchemy              | Data persistence for users, files, passwords, and audit blocks.|
| **Security** | Flask-Bcrypt, `cryptography`, `pyotp`    | Password hashing, data encryption, and MFA.      |
| **Blockchain** | SHA-256, Proof-of-Work                   | Tamper-evident audit trail and chain validation. |
| **AI Analysis** | Google Gemini API                        | Intelligent file analysis and threat detection.  |
| **Frontend** | HTML, CSS, JavaScript (Jinja2)           | Modern responsive user interface.                |

---

## ⚙️ Getting Started

Follow these steps to set up and run a local instance of Guardio.

### 1. Prerequisites
* Python 3.8+
* A virtual environment tool (`venv`)

### 2. Quick Setup (Recommended)

**Option A: Automated Setup**
```bash
git clone https://github.com/yourusername/guardio.git
cd guardio
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
python setup.py
```

The setup script will:
- Install all dependencies
- Generate encryption keys
- Create configuration files
- Initialize the database
- Test blockchain functionality

### 3. Manual Setup

**Option B: Manual Configuration**

1.  **Clone & Enter:**
    ```bash
    git clone https://github.com/yourusername/guardio.git
    cd guardio
    ```

2.  **Activate Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    * Create a `.env` file in the root directory.
    * Generate a secure encryption key:
        ```bash
        python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
        ```
    * Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
    * Add your keys to the `.env` file:
        ```
        SECRET_KEY='a_strong_random_string_for_flask_sessions'
        ENCRYPTION_KEY='your_generated_key_from_the_command_above'
        GEMINI_API_KEY='your_gemini_api_key_here'
        ```

5.  **Initialize the Database:**
    * This creates the `mfa_app.db` file with all necessary tables. **Run this only once.**
    ```bash
    python -c "from app import app, db; app.app_context().push(); db.create_all()"
    ```

6.  **Run the App:**
    ```bash
    flask run
    ```
    Guardio is now running at `http://127.0.0.1:5000`. The first account you create will be the admin.

7.  **Test the Blockchain Audit Trail (Optional):**
    ```bash
    python test_blockchain.py
    ```
    This demonstrates the tamper-evident audit trail functionality.

---

## 🔐 Security Features

Guardio implements enterprise-grade security measures:

### **Encryption & Privacy**
- **End-to-End Encryption**: All user data encrypted with Fernet (AES-128)
- **Zero-Knowledge Architecture**: Server cannot read user data
- **Secure Key Management**: Encryption keys stored separately from data
- **Password Hashing**: Bcrypt with salt for secure password storage

### **Authentication & Access Control**
- **Multi-Factor Authentication**: TOTP-based 2FA integration
- **Role-Based Access Control**: Admin and user roles with appropriate permissions
- **Session Management**: Secure Flask-Login session handling
- **Input Validation**: Comprehensive form validation and sanitization

### **Audit & Compliance**
- **Blockchain-Inspired Audit Trail**: Immutable, tamper-evident logging
- **Cryptographic Integrity**: SHA-256 hashing for chain validation
- **Proof-of-Work**: Computational cost for tampering attempts
- **Complete Transparency**: Full audit trail of all system actions
- **Forensic Capability**: Detailed investigation and compliance support

---

## 📊 Admin Features

### **System Dashboard**
- **Real-Time Analytics**: User statistics, storage usage, and activity metrics
- **System Health Monitoring**: Database status, encryption status, AI availability
- **User Management**: Role management, user statistics, and activity tracking
- **Security Overview**: Chain validation status and tamper detection

### **Audit Trail Management**
- **Blockchain Visualization**: Visual representation of user audit chains
- **Tamper Detection**: Real-time monitoring of chain integrity
- **Chain Validation**: Comprehensive integrity verification
- **Export Capabilities**: Audit data export for compliance

### **System Administration**
- **Settings Management**: Security settings, file limits, AI configuration
- **Backup & Recovery**: System backup and restoration capabilities
- **Log Management**: System logs with filtering and search
- **User Oversight**: Detailed user activity monitoring (privacy-preserving)

---

## 🧪 Testing

### **Blockchain Audit Trail Test**
```bash
python test_blockchain.py
```
This script demonstrates:
- Audit block creation and mining
- Chain validation and integrity checking
- Tamper detection capabilities
- Cryptographic hash verification

### **Manual Testing**
1. **User Registration**: Create accounts and verify MFA setup
2. **File Operations**: Upload, download, and delete files
3. **Password Management**: Add, view, and delete password entries
4. **Admin Functions**: Test admin dashboard and user management
5. **Audit Trail**: Verify audit blocks are created for all actions

---

## 📁 Project Structure

```
Guardio-main/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── test_blockchain.py             # Blockchain audit trail demo
├── .env.example                   # Environment variables template
├── static/
│   ├── style.css                  # Main stylesheet
│   └── ff_qr.png                  # QR code assets
├── templates/
│   ├── base.html                  # Base template
│   ├── landing.html               # Landing page
│   ├── login.html                 # Login page
│   ├── signup.html                # Registration page
│   ├── dashboard.html             # User dashboard
│   ├── password_manager.html      # Password management
│   ├── admin_dashboard.html       # Admin overview
│   ├── admin_settings.html        # System settings
│   ├── admin_logs.html            # System logs
│   ├── admin_audit_trail.html     # Audit trail dashboard
│   ├── user_audit_chain.html      # Individual chain view
│   └── user_details.html          # User details page
└── instance/
    └── mfa_app.db                 # SQLite database
```

---

## 🤝 Contributing

We welcome contributions to Guardio! Please follow these guidelines:

### **Development Setup**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### **Code Standards**
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Test all new features thoroughly
- Update documentation as needed

### **Security Considerations**
- Never commit sensitive data (API keys, passwords)
- Test security features thoroughly
- Follow secure coding practices
- Validate all user inputs

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### **Documentation**
- Check the [Issues](https://github.com/yourusername/guardio/issues) page for common problems
- Review the code comments for implementation details
- Test the blockchain demo for audit trail understanding

### **Security Issues**
For security-related issues, please email security@guardio.app instead of creating a public issue.

### **Feature Requests**
We welcome feature requests! Please create an issue with the "enhancement" label.

---

## 🎯 Roadmap

### **Planned Features**
- [ ] Multi-user file sharing with encryption
- [ ] Advanced AI threat detection
- [ ] Mobile application
- [ ] API for third-party integrations
- [ ] Advanced backup and sync options
- [ ] Enhanced blockchain features (consensus mechanisms)

### **Security Enhancements**
- [ ] Hardware security key support
- [ ] Advanced threat detection
- [ ] Compliance reporting tools
- [ ] Enhanced audit trail features

---

## 🙏 Acknowledgments

- **Flask** - Web framework
- **SQLAlchemy** - Database ORM
- **Cryptography** - Encryption library
- **Google Gemini** - AI analysis
- **PyOTP** - MFA implementation
- **QRCode** - QR code generation

---

**Guardio** - Your data, your control, your security. 🔐⛓️

