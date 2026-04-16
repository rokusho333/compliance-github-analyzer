# DEV_WEB Test Fixture

This branch fixture contains an intentionally insecure front-end project for testing the Compliance GitHub Analyzer.

## Folder
- `dummy-web-client/`

## Seeded issues
- hardcoded secret-like value
- sensitive data logged to console
- token stored in localStorage
- PII stored in localStorage
- client-side-only authorization
- unsafe innerHTML usage
- token in query string
- dangerous eval usage
- missing validation / sanitization
- missing CSP
