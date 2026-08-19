# Support Tiers and Service Levels

**Owner:** IT Operations · **Last reviewed:** 2026-02-14

## Severity definitions

Severity is set by the effect on work, not by how urgent the requester feels it is.
IT may reclassify a ticket; the requester is notified when that happens.

| Severity | Meaning | Example |
|---|---|---|
| **S1 — Critical** | A whole team or a customer-facing system is stopped | Payments API down, office network out, all logins failing |
| **S2 — High** | One person cannot do their core job, no workaround | Laptop will not boot, mailbox inaccessible |
| **S3 — Normal** | Degraded but workable | Slow machine, printer offline, one app misbehaving |
| **S4 — Low** | Request, not a fault | New software, access change, spare cable |

## Response and resolution targets

Response means a human has read the ticket and replied. Resolution means the
reported problem is gone or a permanent workaround is in place.

| Severity | First response | Target resolution | Hours covered |
|---|---|---|---|
| S1 | 15 minutes | 4 hours | 24/7 |
| S2 | 1 business hour | 1 business day | 07:00–19:00 local, Mon–Fri |
| S3 | 4 business hours | 3 business days | 07:00–19:00 local, Mon–Fri |
| S4 | 1 business day | 10 business days | 07:00–19:00 local, Mon–Fri |

S1 is the only severity carrying out-of-hours coverage. An S2 raised at 18:30 on a
Friday has its first response due by 08:00 on Monday.

## Escalation

A ticket escalates automatically when it passes 150% of its resolution target. It
also escalates on request — ask in the ticket, no justification needed.

Escalation path: Support Engineer → IT Operations Lead → Head of Infrastructure.
Anything involving customer data loss, suspected breach, or legal exposure skips
the path entirely and goes straight to the Head of Infrastructure and Legal, as
set out in `05-security-incident-response`.

## What IT does not cover

- Personal devices, except under the BYOD terms in `04-remote-access-policy`
- Software the company has not licensed, including personal subscriptions
- Home internet faults beyond first-line advice; the stipend in
  `03-remote-work-policy` exists to cover this
- Data recovery from any location that is not synced company storage. Files kept
  only on a local desktop are not recoverable. This is the single most common
  cause of unrecoverable loss.

## Satisfaction

Every resolved ticket sends a one-question survey. Results are reviewed monthly.
The team's standing target is 90% satisfied or better; the figure for Q4 2025 was
93%.
