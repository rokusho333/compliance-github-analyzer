# Dummy Fullstack App (Intentionally Insecure)

This project is intentionally insecure and non-compliant. It exists only as a test fixture for the
Compliance GitHub Analyzer project.

## Structure
- `frontend/` — simple browser client
- `backend/` — Flask API

## Purpose
Use this code to verify that your analyzer can detect:
- hardcoded secrets
- weak authentication and authorization
- insecure token and PII handling
- XSS and unsafe DOM injection
- SQL injection
- unsafe file upload handling
- insecure logging
- missing validation
- stack trace leakage
- overly permissive CORS
- debug mode in production

## Do not deploy
This code is intentionally unsafe and should only be used in a local test/demo branch.
