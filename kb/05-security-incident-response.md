# Security Incident Response

**Owner:** Head of Infrastructure · **Last reviewed:** 2026-03-15

## What counts as an incident

Report immediately, before trying to fix it yourself:

- A phishing message that anyone actually clicked, entered credentials into, or
  replied to
- Malware warnings, ransomware notes, or files renamed or encrypted unexpectedly
- Customer data sent to the wrong recipient, or exposed in any way
- A lost or stolen device — see also `01-device-and-equipment-policy`
- Credentials found in a public place: a repository, a screenshot, a support ticket,
  a shared document
- A former employee or contractor who still has working access
- Any request to move money or change bank details that arrived by email or chat,
  regardless of who it appears to be from

A phishing email that was received and **not** acted on does not need a report.
Forward it to the reporting address and delete it.

## How to report

Primary: the `#security-incident` channel. Secondary: phone the on-call number in
the team handbook. Do not open a normal ticket, and do not email — both introduce
delay, and email may itself be compromised.

Reporting is **always** correct, including when you are unsure, including when you
caused it. No one has ever been disciplined for reporting an incident, including
incidents they caused. Concealment is the only conduct treated as misconduct.

## What happens next

| Time from report | Step |
|---|---|
| 15 minutes | Incident commander assigned, acknowledged to reporter |
| 1 hour | Containment decision — isolate device, revoke sessions, rotate credentials |
| 4 hours | Preliminary scope: what was reachable, what was actually reached |
| 24 hours | Written summary to Legal and the exec team |
| 72 hours | Regulator notification, if personal data is confirmed affected |
| 10 business days | Blameless post-incident review, published internally |

The 72-hour clock is a legal deadline under GDPR and starts at the moment the
company becomes aware, not at the moment the investigation finishes. This is why
containment and notification run in parallel rather than in sequence.

## During an incident

Do not power off a suspect machine — it destroys memory evidence. Disconnect it
from the network instead, by unplugging the cable or turning off Wi-Fi, and leave it
running.

Do not discuss the incident outside the incident channel, including with customers,
until Legal has cleared external communication.

## Credential exposure

Any credential that appears anywhere public is treated as compromised and is
rotated, even when it looks unused, even when the repository was private, and even
when it was removed within minutes. Rotation is not negotiable and is not delayed
for convenience.
