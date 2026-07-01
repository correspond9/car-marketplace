# Known Issues

## Bugs

None reported yet — greenfield scaffold.

## Limitations

| Item | Description | Planned fix |
|------|-------------|-------------|
| Image upload | Presigned URL flow not wired end-to-end | Phase 0 sprint 2 |
| OTP in dev | Fixed mock OTP `123456` only | Replace with MSG91 in prod |
| Search scale | PostgreSQL FTS only | Meilisearch in Phase 2 |
| Mobile apps | Scaffold only, no API integration | Phase 1 |
| Hindi UI | English only | Phase 2 |

## Technical debt

| Item | Priority | Notes |
|------|----------|-------|
| Offset pagination | Low | Migrate to cursor-based at scale |
| Refresh token storage | Medium | Currently Redis; consider rotation family |
| Registration number encryption | High | Field exists masked; encryption at rest pending |

## Future improvements

- Fraud signal detection (duplicate images, price anomalies)
- Webhook system for future payments
- Feature flags service for gradual rollouts
