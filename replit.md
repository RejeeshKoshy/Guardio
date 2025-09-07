# Overview

Guardio is a privacy-focused web application that provides end-to-end encrypted cloud storage and password management. Built with Flask, it implements a zero-knowledge architecture where user data is encrypted client-side before storage, ensuring that even the server cannot access user content. The application features a unique blockchain-inspired audit trail system that provides tamper-evident logging of all user actions using cryptographic hashing and proof-of-work validation.

Key features include encrypted file storage with AI-powered analysis, secure password management, multi-factor authentication using TOTP, role-based access control, and comprehensive admin tools for system monitoring and user management.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The application uses a traditional server-rendered architecture with Flask templates and custom CSS styling. The frontend is built with semantic HTML, progressive enhancement principles, and a clean, modern design system inspired by privacy-focused services like Proton. JavaScript is used minimally for enhanced user interactions like form validation and dynamic content updates.

## Backend Architecture
Built on Flask with SQLAlchemy ORM for database operations and Flask-Login for session management. The application follows a modular monolithic architecture with clear separation between authentication, file management, password storage, and audit logging components. All business logic is contained within the main application file with helper functions for encryption, hashing, and blockchain operations.

## Data Storage Solutions
Uses SQLite as the primary database for development with support for PostgreSQL in production environments. All sensitive user data (files, passwords, personal information) is encrypted using Fernet (AES-128) before database storage, implementing a zero-knowledge architecture where encryption keys are derived from user credentials.

## Authentication and Authorization
Implements multi-factor authentication using TOTP (Time-based One-Time Passwords) with QR code generation for authenticator app setup. Password hashing uses bcrypt with salt. Role-based access control distinguishes between regular users and administrators, with administrators having access to system monitoring and user management features.

## Blockchain-Inspired Audit System
Features a unique tamper-evident audit trail that creates immutable blocks for every user action. Each audit block contains SHA-256 hashes linking to previous blocks, creating a chain that can detect tampering. Includes a simple proof-of-work mining system that adds computational cost to tampering attempts, making the audit trail cryptographically secure.

## File Management System
Supports hierarchical folder organization with encrypted file storage. Files are encrypted before storage and decrypted on-demand during download. Includes AI-powered file analysis capabilities for generating content summaries and insights using Google's Gemini API.

# External Dependencies

## AI Services
- **Google Gemini API**: Used for AI-powered file analysis and content summarization. The service is optional and the application gracefully degrades when not configured.

## Authentication Libraries
- **PyOTP**: Generates and validates TOTP tokens for multi-factor authentication
- **QRCode with Pillow**: Creates QR codes for MFA setup in authenticator apps

## Encryption and Security
- **Cryptography (Fernet)**: Provides AES-128 encryption for all user data
- **Flask-Bcrypt**: Handles secure password hashing with salt
- **Flask-Login**: Manages user sessions and authentication state

## Web Framework and Database
- **Flask**: Core web framework with SQLAlchemy ORM for database operations
- **SQLite**: Default database for development (easily configurable for PostgreSQL)

## Environment and Configuration
- **Python-dotenv**: Manages environment variables and configuration
- **Secrets module**: Generates cryptographically secure random keys when environment variables are not set