# Data Classification and Retention

**Owner:** Legal with IT Operations · **Last reviewed:** 2026-01-31

## Classification

| Class | Meaning | Examples | Where it may live |
|---|---|---|---|
| **Public** | Already published | Marketing site, job posts | Anywhere |
| **Internal** | Ordinary business information | Team plans, meeting notes, this handbook | Company storage, approved tools |
| **Confidential** | Damaging if disclosed | Contracts, salaries, roadmaps, unreleased results | Company storage, access-controlled |
| **Restricted** | Customer personal data, credentials, health or payment data | CRM exports, support attachments, access keys | Named systems only, never in chat or email |

When a document mixes classes, it takes the highest class present. A team plan
containing one customer's name is Restricted, not Internal.

## Handling rules by class

Restricted data may not be: pasted into chat, attached to email, stored on a local
desktop, copied to a personal device, or put into any AI tool that is not on the
approved list in `07-software-and-procurement`.

Confidential and Restricted data may not be shared through public links. Sharing
links must be limited to named recipients and expire within 90 days.

Screenshots of Restricted data are themselves Restricted. This catches people out
in support tickets more than anywhere else — redact before attaching.

## Retention

| Data | Kept for | Then |
|---|---|---|
| Customer records, active | Life of the contract | Move to the post-contract rule |
| Customer records, after contract end | 7 years | Deleted |
| Support tickets | 3 years | Deleted |
| Chat messages | 12 months | Deleted automatically |
| Email | 5 years | Deleted automatically |
| Access and audit logs | 13 months | Deleted |
| Recruitment records, unsuccessful | 12 months | Deleted |
| Payroll and tax | 7 years | Deleted |

Deletion is automatic and cannot be paused per person or per team. The single
exception is a **legal hold**, which only Legal can place, which suspends all
deletion for the data it names, and which cannot be lifted by anyone else —
including the person whose data it covers.

## Deletion requests from customers

A customer asking for their data to be deleted is a formal request with a **30
calendar day** deadline. Route it to Legal the same day it arrives. Do not confirm
to the customer that anything has been deleted, and do not begin deleting — Legal
determines what must be kept for tax or contractual reasons before anything is
removed.

Acting on a deletion request without Legal is worse than delaying it: deleted data
cannot be restored if it turns out to have been under a retention obligation.

## Backups

Company storage is backed up continuously with **35 days** of point-in-time
recovery. Local machine storage is not backed up at all. A file that exists only on
a laptop desktop is one hardware failure away from being gone, and IT cannot
recover it — this is stated again here because it is the most frequent cause of
permanent data loss in support tickets.
