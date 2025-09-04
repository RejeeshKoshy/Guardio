# Contributing to Guardio

Thank you for your interest in contributing to Guardio! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic understanding of Flask, SQLAlchemy, and web security

### Development Setup
1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/guardio.git
   cd guardio
   ```
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
6. Initialize the database:
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

## 🔧 Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and single-purpose
- Use type hints where appropriate

### Security Considerations
- **Never commit sensitive data** (API keys, passwords, encryption keys)
- Test all security features thoroughly
- Validate all user inputs
- Follow secure coding practices
- Review security implications of any changes

### Testing
- Test all new features manually
- Run the blockchain test: `python test_blockchain.py`
- Verify admin functionality works correctly
- Test with different user roles
- Ensure audit trail is created for all actions

## 📝 Making Changes

### Branch Naming
Use descriptive branch names:
- `feature/audit-trail-enhancement`
- `bugfix/login-validation`
- `security/encryption-improvement`
- `docs/readme-update`

### Commit Messages
Use clear, descriptive commit messages:
```
feat: Add blockchain audit trail validation
fix: Resolve file upload encryption issue
docs: Update README with new features
security: Enhance password validation
```

### Pull Request Process
1. Create a feature branch from `main`
2. Make your changes with clear commits
3. Test thoroughly
4. Update documentation if needed
5. Create a pull request with:
   - Clear description of changes
   - Screenshots for UI changes
   - Testing instructions
   - Any breaking changes

## 🧪 Testing Guidelines

### Manual Testing Checklist
- [ ] User registration and MFA setup
- [ ] File upload, download, and deletion
- [ ] Password management operations
- [ ] Admin dashboard functionality
- [ ] Audit trail creation and validation
- [ ] Chain integrity verification
- [ ] Tamper detection
- [ ] System settings management

### Security Testing
- [ ] Test with invalid inputs
- [ ] Verify encryption/decryption works
- [ ] Check audit trail integrity
- [ ] Test admin privilege escalation
- [ ] Validate MFA functionality

## 🐛 Bug Reports

When reporting bugs, please include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots if applicable
- Error messages or logs

## 💡 Feature Requests

For feature requests, please:
- Check existing issues first
- Provide clear use case
- Explain the benefit to users
- Consider security implications
- Suggest implementation approach if possible

## 🔒 Security Issues

**Do not create public issues for security vulnerabilities.**

Instead, email security@guardio.app with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## 📚 Documentation

### Code Documentation
- Add docstrings to new functions
- Comment complex logic
- Update README for new features
- Include usage examples

### API Documentation
- Document new endpoints
- Include request/response examples
- Note authentication requirements
- Specify error conditions

## 🎯 Areas for Contribution

### High Priority
- Security enhancements
- Performance optimizations
- Bug fixes
- Documentation improvements

### Medium Priority
- UI/UX improvements
- Additional admin features
- Enhanced audit trail features
- Mobile responsiveness

### Low Priority
- Code refactoring
- Test coverage improvements
- Additional integrations
- Advanced blockchain features

## 📋 Code Review Process

### For Contributors
- Respond to review feedback promptly
- Make requested changes
- Ask questions if feedback is unclear
- Test changes after addressing feedback

### For Reviewers
- Be constructive and respectful
- Focus on code quality and security
- Test the changes if possible
- Provide clear feedback
- Approve when ready

## 🏆 Recognition

Contributors will be recognized in:
- README acknowledgments
- Release notes
- GitHub contributors list

## 📞 Getting Help

- Check existing issues and discussions
- Join our community discussions
- Contact maintainers for guidance
- Review code comments and documentation

## 📄 License

By contributing to Guardio, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Guardio! Your efforts help make secure, private cloud storage accessible to everyone. 🔐⛓️
