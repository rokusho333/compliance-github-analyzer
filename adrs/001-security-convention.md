# ADR-001: HIPAA-Compliant Data Protection

## Status
Accepted

## Context
The system processes Protected Health Information (PHI) and must comply with HIPAA Security and Privacy Rules.

## Decision
All PHI must be protected using strong security controls across storage, transmission, and access.

## Rules

### Encryption
- All PHI MUST be encrypted at rest (AES-256 or equivalent)
- All PHI MUST be encrypted in transit (TLS 1.2+)
- Secrets MUST NOT be hardcoded in source code

### Access Control
- Access MUST follow least privilege principle
- Authentication MUST be enforced for all services accessing PHI
- Role-based access control (RBAC) MUST be implemented

### Logging & Auditing
- All access to PHI MUST be logged
- Logs MUST include user identity, timestamp, and action
- Logs MUST be immutable and retained

### Data Handling
- Only minimum necessary PHI should be processed
- PHI MUST NOT be exposed in logs or error messages

### Infrastructure
- Production data MUST NOT be used in non-production environments
- Backup and recovery mechanisms MUST be in place

## Prohibited Patterns
- Storing PHI in plaintext
- Using HTTP instead of HTTPS
- Hardcoding credentials
- Logging sensitive patient data

## Rationale
These controls are required to comply with HIPAA Security Rule and to prevent unauthorized access, data breaches, and regulatory violations.

## Consequences
- Increased implementation complexity
- Additional monitoring and compliance overhead
- Improved security and regulatory compliance