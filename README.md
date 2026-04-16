# Compliance GitHub Analyzer

A multi-agent workflow that reviews pull requests or code diffs to identify:

- security issues
- compliance violations
- engineering bad practices

It recommends fixes, can generate validation tests, and returns a final review decision.

## MVP
- Parse PR diff
- Detect risky patterns
- Map findings to compliance/security rules
- Suggest fixes
- Generate validation tests
- Return final recommendation

## Project idea
This project is inspired by AI-agent SDLC workflows such as PR review, security review,
test generation, and compliance validation.

## Planned agents
- Intake Agent
- Compliance Agent
- Security Agent
- Remediation Agent
- Report Agent

## Input
A pasted git diff or sample source file.

## Output
A structured review report with:
- issues found
- severity
- violated rule
- recommended fix
- optional tests
- final decision
