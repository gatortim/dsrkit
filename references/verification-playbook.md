# Verification playbook

Deletion is a claim. Verification is an observation. Keep them in separate columns forever.

## 1. Evidence record

One record per observation. JSON, append-only, never edited after the fact.

```json
{
  "request_id": "9fef0243",
  "target": "acme-data-co",
  "tier": 3,
  "observed_at": "2026-11-23T15:04:11-07:00",
  "probe": "people-search query for 'Tim Jacobs, 85701' returned 0 results",
  "probe_url_or_command": "https://example-people-search/?q=...",
  "result": "removed",
  "confidence": "high",
  "evidence_file": "~/evidence/acme-search-20261123.png",
  "evidence_sha256": "…",
  "caveats": "search index may lag; re-check at cycle+1",
  "operator": "tim"
}
```

Rules:

- Hash the evidence file. Screenshots get argued about; a hash ends the argument about whether the
  file changed.
- Record negative results too. "Still present on 2026-11-20" is what makes "removed on 2026-11-23"
  meaningful.
- Never backfill a timestamp. If you forgot to record it, say so.

## 2. Probe recipes by class

### Broker (after DROP)

1. DROP status for the DROP ID — pending / reported, per broker where shown.
2. Fresh people-search query from a clean browser profile, using the identifier set you filed.
3. A second query 7–14 days later (indexes lag; one clean read is weak).
4. For paid brokers: a trial lookup, not a purchase, to see whether the profile still resolves.

### Controller (account business)

1. Try to log in after account deletion: expect a clear "no such account", not a password error.
2. **File an access request after the deletion.** If the same controller returns data about you
   after confirming deletion, the deletion failed. This is the single strongest controller probe and
   the one most people skip.
3. Re-run the marketing-email check: new mail after T0 implies the record survived.
4. Re-read the public profile, review page, or comment history that the deletion should have removed.

### Processor

Processors usually answer only through the controller. Treat a processor's confirmation as Tier 1
until the controller repeats it, because the controller is who owes you the duty.

### Machine / agent

| Probe | Pass condition |
|---|---|
| Authenticated call with the old key | 401/403 |
| Login with the deleted account | 404/410, not 401 |
| Webhook replay / delivery log | no deliveries after T0 |
| Telemetry sink query for subject ID | zero events after T0 |
| Object storage listing under the old prefix | empty or 404 |
| SSO / directory lookup | subject absent |

Record the residual honestly: "backups expire 2027-02-01 per vendor policy" is a passing answer,
"we deleted everything instantly" from a vendor with 35-day snapshots is not.

## 3. False positives that make people file bad complaints

| Signal you think is failure | What it usually is | How to tell |
|---|---|---|
| Site still shows your name | Cache/CDN or a *different* broker | check the URL, check the registry entry |
| Broker still holds an email hash | suppression list, lawful under §1798.105(c)(2) | ask what is retained and why |
| Records reappear later | re-acquisition; the duty is recurring | re-file / wait for next DROP cycle |
| "We kept it for tax/legal reasons" | exemption (d)(8) / (d)(1) | ask for the specific provision, record it |
| Login says "wrong password" | account exists, deletion not done | escalate with the probe |
| Access request returns data after "deletion" | genuine failure | best evidence you can get |
| Search engine still indexes the page | index lag, not source data | check source; use search-engine removal separately |

## 4. Sampling and cost

Verification is the expensive half of any deletion product. Budget it explicitly:

- Full Tier 3 on every target is unaffordable at broker scale. Tier 3 on a **random sample per
  cycle** plus Tier 3 on **every target that claims completion** is defensible.
- Tier 1 is free (parse the email/status). Automate it.
- Tier 2 is cheap when the target has a read endpoint; expensive when it means a support ticket.
- Track cost per verified deletion. It is the unit economics of the entire business
  (see the DROP terms of use quoted in `references/endpoint-catalog.md` §1).

## 5. Reporting

`scripts/erasure.py report` produces the pack. A pack that persuades contains:

1. subject, basis, jurisdiction, identifier set, dates
2. per target: filing method, receipt, clock, polls, observations, exemption if any
3. the overdue list with statutory cites
4. one line per verification: what was observed, when, where the artifact is, its hash
5. a "what we did not verify" section. Every pack needs one; omitting it is how evidence becomes
   marketing.
