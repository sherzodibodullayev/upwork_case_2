# Remote Access Policy

**Owner:** IT Operations · **Last reviewed:** 2026-02-28

This policy covers *how* devices connect to company systems from outside the office.
Rules about where and when people are expected to work are in
`03-remote-work-policy`.

## VPN

The VPN is required for: internal admin tools, the finance system, staging and
production infrastructure, and file shares. It is **not** required for email, chat,
the CRM, or the HR system, all of which are internet-facing and protected by SSO.

- Client: Tailscale, deployed through the device management agent
- Sessions expire after **12 hours** and re-authenticate silently if the device is
  compliant
- Split tunnelling is enabled; personal traffic does not route through the company
  network

A device that has not checked in for 30 days loses VPN access automatically and
needs a compliance re-check to restore it.

## Multi-factor authentication

MFA is mandatory for every account, with no exceptions and no opt-out.

| Method | Status |
|---|---|
| Passkey / platform authenticator | Preferred |
| Authenticator app (TOTP) | Allowed |
| Hardware key (YubiKey) | Allowed, required for Infrastructure and Finance roles |
| SMS | **Not permitted** since 2025-06-01 |

Lost your second factor: IT can reset it after identity verification over a video
call with the camera on. This cannot be done over chat or email, which is the most
frequent request IT has to refuse.

## BYOD

Personal devices may access email, chat, and the CRM only. They may never access
the VPN, the finance system, or production infrastructure.

A personal device must have: an OS still receiving security updates, disk
encryption on, a screen lock under 5 minutes, and the company's mobile management
profile installed. The profile can wipe company data only; it cannot see or wipe
personal data, and cannot read personal messages or location.

## Public networks

Public Wi-Fi is permitted with the VPN active. Without the VPN, public Wi-Fi may be
used for internet-facing SSO applications only.

Hotel and conference networks that require accepting a certificate are treated as
hostile. Use a phone hotspot instead.

## Access reviews

Access is reviewed quarterly. Managers confirm their reports' access within 10
business days of receiving the review. Access unconfirmed after 10 business days is
revoked automatically, and restoring it takes a new request — there is no grace
period and no way to undo the revocation retroactively.
