# Security Review Guidelines

This document provides comprehensive guidelines for conducting security reviews of code and architecture using LLM assistance.

## Security Review Process

### Planning the Review

1. **Define Scope**: Clearly define what components, systems, or code will be reviewed
2. **Identify Critical Areas**: Prioritize security-sensitive components like:
   - Authentication systems
   - Authorization mechanisms
   - Data processing pipelines
   - Input/output handling
   - Payment processing
   - User data management
3. **Gather Context**: Collect relevant documentation, architecture diagrams, and threat models
4. **Review History**: Check previous security issues or vulnerabilities

### Conducting the Review

1. **Automated Scanning**: Run automated security scanners
2. **Manual Code Review**: Perform detailed review of critical paths
3. **Architecture Analysis**: Evaluate system design for security weaknesses
4. **Dependency Analysis**: Review external dependencies for known vulnerabilities
5. **Threat Modeling**: Identify potential threats and attack vectors

### Documenting Findings

1. **Severity Classification**: Rate issues by severity (Critical, High, Medium, Low)
2. **Clear Description**: Document each issue with clear reproduction steps
3. **Impact Assessment**: Explain the potential impact of each vulnerability
4. **Remediation Guidance**: Provide specific remediation recommendations
5. **Verification Plan**: Define how fixes will be verified

## OWASP Top 10 Vulnerabilities Checklist

### 1. Broken Access Control

- [ ] Proper authorization checks before accessing resources
- [ ] Secure direct object references (prevent insecure direct object reference attacks)
- [ ] Enforce principle of least privilege
- [ ] Implement proper access control on API endpoints
- [ ] No sensitive operations accessible by unauthorized users
- [ ] Session management properly implemented

### 2. Cryptographic Failures

- [ ] Sensitive data encrypted in transit (HTTPS everywhere)
- [ ] Sensitive data encrypted at rest
- [ ] Strong, up-to-date encryption algorithms used
- [ ] No hardcoded secrets or encryption keys
- [ ] Proper key management procedures
- [ ] Secure random number generation for security purposes

### 3. Injection

- [ ] SQL queries use parameterized statements or ORMs
- [ ] NoSQL queries sanitize and validate input
- [ ] OS commands validated and sanitized
- [ ] LDAP inputs properly escaped
- [ ] XML parsers configured to prevent XXE attacks
- [ ] Template engines used safely to prevent template injection

### 4. Insecure Design

- [ ] Security requirements defined during design phase
- [ ] Secure by design principles followed
- [ ] Threat modeling performed during architecture planning
- [ ] Principle of defense in depth implemented
- [ ] Failure states designed to be secure
- [ ] Rate limiting implemented where appropriate

### 5. Security Misconfiguration

- [ ] Development/debug features disabled in production
- [ ] Default accounts and passwords removed
- [ ] Error handling doesn't expose sensitive information
- [ ] Security headers properly configured
- [ ] Security directives in place (Content-Security-Policy, etc.)
- [ ] Up-to-date security patches and software versions

### 6. Vulnerable and Outdated Components

- [ ] Inventory of all components and dependencies
- [ ] Regular scanning for vulnerabilities in dependencies
- [ ] Process for updating components when vulnerabilities discovered
- [ ] Removal of unnecessary features, components, and dependencies
- [ ] Verification of component compatibility after security updates

### 7. Identification and Authentication Failures

- [ ] Strong password policies enforced
- [ ] Multi-factor authentication available for sensitive operations
- [ ] Secure credential storage (hashing with appropriate algorithms)
- [ ] Protection against automated attacks (rate limiting, CAPTCHA)
- [ ] Secure session management implementation
- [ ] Secure password reset mechanisms

### 8. Software and Data Integrity Failures

- [ ] Integrity checks on software updates and patches
- [ ] Secure CI/CD pipeline with proper validation
- [ ] Unsigned data not trusted without validation
- [ ] Deserialization of user data properly secured
- [ ] Software supply chain security measures in place

### 9. Security Logging and Monitoring Failures

- [ ] Security-relevant events logged (login attempts, access control failures, etc.)
- [ ] Logs contain sufficient context but no sensitive data
- [ ] Logs protected from tampering and unauthorized access
- [ ] Log monitoring and alerting for suspicious activities
- [ ] Incident response plan in place

### 10. Server-Side Request Forgery (SSRF)

- [ ] Validation of all client-supplied URLs
- [ ] Firewall policies restricting outbound traffic
- [ ] URL whitelisting for external requests
- [ ] Disallow requests to private networks or metadata services
- [ ] Minimal privileges for application components making requests

## Authentication and Authorization Checks

### Authentication

- [ ] Strong password requirements enforced
- [ ] Account lockout after failed attempts
- [ ] Secure session handling
- [ ] Session timeout implemented
- [ ] Secure cookie attributes (Secure, HttpOnly, SameSite)
- [ ] CSRF protection implemented
- [ ] Multi-factor authentication available
- [ ] Remember-me functionality implemented securely
- [ ] Secure credential storage

### Authorization

- [ ] Role-based access control implemented
- [ ] Attribute-based access control for fine-grained permissions
- [ ] Principle of least privilege followed
- [ ] Authorization checks on all sensitive operations
- [ ] Front-end and back-end authorization consistency
- [ ] No privilege escalation paths
- [ ] API endpoints protected appropriately

## Data Validation and Sanitization

### Input Validation

- [ ] All user inputs validated for:
  - Type
  - Length
  - Format
  - Range
- [ ] Validation occurs server-side
- [ ] Strict whitelist validation where possible
- [ ] Validated data not bypassing security controls

### Output Encoding

- [ ] Context-aware output encoding to prevent XSS
- [ ] HTML encoding for HTML contexts
- [ ] JavaScript encoding for JavaScript contexts
- [ ] CSS encoding for CSS contexts
- [ ] URL encoding for URL parameters

### Data Processing

- [ ] Safe handling of file uploads
- [ ] Proper MIME type validation
- [ ] File size restrictions
- [ ] File content validation
- [ ] Secure file storage locations

## Secure Coding Practices

### Error Handling

- [ ] Generic error messages to users
- [ ] Detailed errors logged securely
- [ ] No sensitive information in error messages
- [ ] Proper exception handling
- [ ] Fail securely (errors default to secure state)

### Concurrency

- [ ] Race conditions addressed
- [ ] Proper locking mechanisms
- [ ] Atomic operations for critical sections
- [ ] Time-of-check to time-of-use (TOCTOU) vulnerabilities prevented

### Memory Management

- [ ] Buffer overflow protections
- [ ] Proper resource cleanup
- [ ] Protection against memory leaks
- [ ] Safe handling of pointers (in applicable languages)

## Dependency Vulnerability Management

### Dependency Analysis

- [ ] Complete inventory of all dependencies
- [ ] Regular scanning for vulnerabilities
- [ ] Update plan for vulnerable components
- [ ] Verification process after updates

### Supply Chain Security

- [ ] Trusted sources for dependencies
- [ ] Integrity verification of packages
- [ ] Minimal dependencies principle
- [ ] Vendor security assessment for critical dependencies

## Compliance Requirements

### General Compliance

- [ ] GDPR considerations (if processing EU citizens' data)
- [ ] CCPA considerations (if dealing with California residents)
- [ ] HIPAA requirements (if handling health information)
- [ ] PCI DSS compliance (if processing payment cards)
- [ ] Industry-specific regulations addressed

### Security Standards

- [ ] OWASP ASVS (Application Security Verification Standard) alignment
- [ ] NIST Cybersecurity Framework consideration
- [ ] CIS Benchmarks for infrastructure components

## Security Review Report Template

```markdown
# Security Review Report: [Project/Component Name]

## Executive Summary

[Brief overview of the review, key findings, and overall security posture]

## Scope

[Description of what was reviewed and what was out of scope]

## Methodology

[Description of the review process and techniques used]

## Findings

### Critical Issues

#### [Issue Title]

- **Description**: [Detailed description]
- **Location**: [Where the issue was found]
- **Impact**: [Potential consequences]
- **Recommendation**: [How to fix it]
- **References**: [Any relevant security standards or articles]

### High Issues

[Same format as above]

### Medium Issues

[Same format as above]

### Low Issues

[Same format as above]

## Positive Findings

[Security measures that were implemented well]

## Recommendations

### Short-term

[Immediate actions to address critical and high issues]

### Medium-term

[Actions to address medium issues and improve security posture]

### Long-term

[Strategic security improvements]

## Conclusion

[Overall assessment and next steps]

```

## LLM-Assisted Security Review Guidelines

### Effective Prompting

1. **Context-rich prompts**: Provide the LLM with sufficient context about the codebase and architecture
2. **Focused queries**: Ask about specific security concerns rather than general "find all issues"
3. **Incremental review**: Review code in manageable chunks rather than all at once
4. **Guided exploration**: Direct the LLM to focus on high-risk areas first

### Verification

1. **Verify findings**: Manually verify all LLM-identified issues before acting
2. **False positive assessment**: Critically evaluate warnings that may be false positives
3. **Missed vulnerabilities**: Use security checklists to identify issues the LLM might miss
4. **Domain-specific checks**: Supplement with domain-specific security knowledge

### Best Practices

1. **Multiple perspectives**: Use different prompt approaches to find different issues
2. **Pattern recognition**: Ask the LLM to identify patterns across multiple findings
3. **Code evolution**: Review security implications of code changes over time
4. **Knowledge updates**: Be aware of the LLM's knowledge cutoff and supplement with newer information