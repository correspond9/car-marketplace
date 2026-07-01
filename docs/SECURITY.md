# Security

## Principles

- HTTPS only in production
- Least privilege for DB users and IAM
- No secrets in source control
- Input validation on every endpoint
- Rate limiting on auth and search
- Audit log for moderator/admin actions

## Authentication

- Phone OTP with 6-digit code, 5-minute expiry, max 3 attempts
- JWT access tokens (15 min) signed with HS256 (or RS256 in multi-service future)
- Refresh tokens stored in Redis, rotated on use, revocable
- Passwords not used (OTP-only model)

## Authorization

Role hierarchy enforced server-side:

```
admin > moderator > dealer > user > guest
```

Never trust client-sent role claims without server verification.

## Data protection

| Data | Treatment |
|------|-----------|
| Phone numbers | Stored; masked in public profiles where applicable |
| Registration numbers | Masked in API responses; full value encrypted at rest (planned) |
| OTP codes | Hashed in Redis; never logged |
| JWT secrets | Environment variable only |
| PII in logs | Stripped via structured logging filters |

## OWASP mitigations

| Risk | Mitigation |
|------|------------|
| Injection | SQLAlchemy parameterized queries; Pydantic validation |
| Broken auth | Short-lived JWT; refresh rotation; OTP rate limits |
| XSS | Next.js auto-escaping; CSP headers on web |
| CSRF | SameSite cookies if cookie auth added; Bearer tokens for API |
| SSRF | Presigned URLs scoped to bucket/path |
| File upload | MIME validation, size limits, EXIF strip (planned) |

## Rate limits

Implemented via Redis sliding window:

- OTP request: 3 / 15 min per phone
- OTP verify: 5 / 15 min per phone
- Search: 60 / min per IP
- Authenticated: 120 / min per user

## DPDP Act 2023 alignment (India)

- Consent at signup (Terms + Privacy acceptance)
- Data minimization — collect only required fields
- Account deletion endpoint (`DELETE /auth/account`)
- Data export endpoint (planned)
- Grievance officer contact on website (pending legal)
- Audit trail for admin data access (planned)

## Incident response

1. Rotate `SECRET_KEY` and invalidate all refresh tokens
2. Review audit logs for suspicious moderator/admin actions
3. Notify affected users if PII breach confirmed
4. Document in post-incident report

## Security contacts

Configure `SECURITY_CONTACT` env var for responsible disclosure email.
