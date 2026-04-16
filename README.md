# DEV_SERVER Test Fixture

This branch fixture contains an intentionally insecure backend project for testing the Compliance GitHub Analyzer.

## Folder
- `dummy-backend-api/`

## Seeded issues
- hardcoded secrets
- plaintext password storage
- permissive CORS
- missing authentication / authorization
- sensitive data in logs
- SQL injection
- sensitive data exposure in responses
- unsafe file upload path handling
- missing validation
- stack trace leakage
- debug mode enabled
