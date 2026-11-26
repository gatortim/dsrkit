---
name: dsrkit
description: "File, clock, and verify US data-deletion requests."
version: 0.1.0
license: Apache-2.0
metadata:
  hermes:
    tags: [privacy, ccpa, cpra, colorado, dsr, deletion, compliance, verification, drop]
    related_skills: [blocked-page-recovery, grounded-citations]
---

# dsrkit

Exercise a data subject's right to delete: enumerate every endpoint required to accept a deletion
request, file one request per target, track each statutory clock, poll for processing, verify
removal independently, and produce an evidence pack that survives an auditor or a regulator.

Two facts drive the design:

1. **Only California has a shared mechanism** (DROP: one free filing covers 625 registered brokers).
   The other ~20 states with comprehensive laws give you the right and leave the enumeration to you.
2. **The law is about dates, receipts, and re-observation** — not about sending an email. A request
   without a receipt, a receipt without a deadline, and a deadline without a second observation are
   worth nothing.

## When to use

- "Delete my data from the data brokers" / "file DSRs" / "purge this account's footprint"
- Enumerating privacy or retention endpoints for a company, product, or domain
- Auditing whether a deletion actually happened and packaging the proof
- Building a DSR pipeline or an SLA monitor

Not for: breach response (different statute, different clock), legal advice, or deleting data you
do not own. Attestation is mandatory.

## Workflow

**Phase 0 — scope.** Name the subject, the basis (`self` / written authorization / contractual for a
machine identity), and the jurisdiction. Jurisdiction picks the path: `CA` → DROP is available;
anything else → no DROP, enumerate with the three seeds in `references/non-california-states.md`.
Rights attach to **residence**, never to an IP address.

**Phase 0b — cut the join keys before you spend anything on deletion.** Hashed email, device
advertising ID, cookies. Deleting a broker row while a global hashed-email key survives buys one
clean quarter, not a clean record. `references/tracking-scrub.md`.

**Phase 1 — enumerate.** Four classes: `broker`, `controller`, `processor`, `machine`.

```bash
python3 scripts/enumerate.py --input domains.txt --gpc --out enumerated.json
python3 scripts/erasure.py init --subject "self" --jurisdiction CO --state ~/privacy/ledger.json
python3 scripts/erasure.py targets import --csv registry.csv --state ~/privacy/ledger.json
```

**Phase 2 — file.** Dry run by default; `--execute --attest self --receipt <id>` records it. Capture
the receipt verbatim, the timestamp, the exact identifier set, and a screenshot.

**Phase 3 — poll.** Record every status read, including "no change". Use the platform's own words.

**Phase 4 — verify.** Three tiers; only independent re-observation is proof. A receipt is not a
deletion, and an exemption the target cites is lawful — record it and stop.

**Phase 5 — escalate.** `report` produces the packet. Comply on evidence: overdue + a recorded poll
+ no substantive response is a complaint. Nothing else is.

## Pitfalls

1. Filing before attesting — a request for someone else is a data-integrity attack.
2. Treating DROP as complete coverage — it covers registered brokers only.
3. One identifier — name + DOB + ZIP minimum; thin identifiers produce unfalsifiable "no record".
4. Losing the receipt — no receipt means no clock, no complaint, no proof.
5. Quoting penalties as consumer money — the $200/day DROP fine is a state fine. There is no private
   right of action for a missed deletion in any of these statutes.
6. Assuming deletion is permanent — brokers re-acquire; schedule re-observation.
7. Scraping broker sites at scale — use the registry and the official portals.
8. Citing dead tooling — the NAI discontinued its opt-out tools on 2025-09-15, and Chrome reversed
   its third-party-cookie plan. Verify an endpoint responds before building on it.

## Files

- `scripts/erasure.py` — ledger CLI (init, targets, file, poll, clock, verify, report, selftest)
- `scripts/enumerate.py` — intake discovery for states with no registry
- `references/legal-clock.md`, `endpoint-catalog.md`, `non-california-states.md`,
  `tracking-scrub.md`, `verification-playbook.md`, `escalation-and-templates.md`, `model-layer.md`
- `templates/request-email.md`, `templates/authorization-letter.md`
