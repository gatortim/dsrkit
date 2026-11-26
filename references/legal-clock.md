# Legal clock, deadlines, penalties, exemptions

Verified against primary sources on 2026-11-23. Re-verify before quoting to a customer, a
complainant, or a regulator. Section numbers change; statute text does not lie.

## 1. California: CCPA/CPRA (right to delete)

| Item | Rule | Source |
|---|---|---|
| Right | Consumer may request deletion of PI the business collected | Civ. Code §1798.105(a) |
| Downstream duty | Delete from records, direct service providers/contractors to delete, notify third parties the PI was sold/shared to (unless impossible or disproportionate effort) | §1798.105(c)(1), (c)(3) |
| Suppression record | A confidential record of the request may be kept solely to stop re-sale, for legal compliance, and as otherwise permitted | §1798.105(c)(2) |
| Acknowledgment | 10 business days | 11 CCR §7021(a) |
| Substantive response | 45 calendar days from receipt; +45 days with notice | §1798.130(a)(2); 11 CCR §7021(b) |
| Methods of submission | Two or more designated methods, including a toll-free number and a webform; must be easy to find | 11 CCR §7020 |
| Verification | Proportionate to risk; may not require account creation solely to verify | 11 CCR §§7060–7062 |
| Authorized agents | Business may require signed permission from the consumer + identity verification; consumer may be required to confirm permission directly | 11 CCR §7063 |
| Admin fines | $2,500 per violation; $7,500 per intentional violation or one involving a minor | Civ. Code §1798.155 |
| Private right of action | **Breach only**: $100–$750 per consumer per incident | Civ. Code §1798.150 |

### The eight deletion exemptions (§1798.105(d), post-CPRA)

Paraphrase them for triage; quote them in a complaint. A cited exemption is lawful — record it and
stop.

1. (d)(1) complete the transaction, honor a warranty/recall, provide a requested good or service,
   or perform the contract
2. (d)(2) ensure security and integrity, where reasonably necessary and proportionate
3. (d)(3) debug to identify and repair errors
4. (d)(4) exercise free speech, or another consumer's free-speech right, or another legal right
5. (d)(5) comply with the California Electronic Communications Privacy Act (Penal Code Title 12,
   Part 2, Ch. 3.6)
6. (d)(6) public or peer-reviewed scientific/historical/statistical research, with informed consent
7. (d)(7) solely internal uses reasonably aligned with consumer expectations
8. (d)(8) comply with a legal obligation

Trap: many blogs and second-hand tables reproduce the pre-CPRA 2020 list (nine items, including
"detect security incidents" as (d)(2)). The current statute has eight. If a source shows nine, it is
stale.

## 2. California: Delete Act (SB 362) and DROP

| Item | Rule | Source |
|---|---|---|
| Data broker | Knowingly collects and sells to third parties the PI of consumers with whom it has no direct relationship | Civ. Code §1798.99.80(c) |
| Registration | Annual, each year after meeting the definition | §1798.99.80 et seq. |
| Registration fee | $6,000 + processing fee (2026) | privacy.ca.gov/data-brokers |
| DROP duty begins | 2026-08-01: access DROP at least every 45 days, download lists, delete, upload status | §1798.99.86; CalPrivacy |
| Cycle | 45 days → **30 days from 2027-01-01** (AB 883, Ch. __, signed 2026-09-27). AB 883 shortens **four** clocks, not one: how often a broker must access DROP, how long it has to process and delete after receipt, how long it has to convert an unverifiable request into an opt-out, and how often it must re-delete after the first deletion | AB 883 (2026); §1798.99.86 |
| Officials and judges | From 2027-07-01, designated bodies must tell elected officials and judges about DROP; the AG, a county counsel, or a city attorney may sue a broker that fails to delete for them (§1798.99.86.5) | AB 883 (2026) |
| Consumer status lag | up to 90 days for brokers to report status | privacy.ca.gov/drop/how-drop-works |
| Failure to delete | **$200 per deletion request per day** — administrative fine | §1798.99.86 |
| Failure to register | $200 per day + fees + recovery | §1798.99.82 |
| Denials | Broker must report denial, count, and the specific exemption relied on | CalPrivacy / DROP regs |
| Ongoing duty | Re-check and delete newly acquired matching PI each cycle; may not sell/share new PI of a requester | Delete Act |

### What DROP is not

- Not a general erasure right: covers registered data brokers only, not controllers you have an
  account with, not public records, not data covered by other exemptions.
- Not a private claim: the money is the state's. A consumer's lever is a complaint with evidence.
- Not one-and-done: it is a subscription to recurring deletion, forever.
- Not chargeable: CalPrivacy states DROP is free and will never charge consumers. Paid lookalikes
  trade on confusion and will get you the wrong kind of attention.

## 3. EU/UK: GDPR Art. 17 and Art. 12

| Item | Rule |
|---|---|
| Response | One month from receipt; +2 months for complex/multiple requests, with notice inside the first month |
| Erasure grounds | Art. 17(1)(a)–(f): no longer necessary, consent withdrawn, successful objection, unlawful processing, legal obligation, child's data |
| Erasure exceptions | Art. 17(3)(a)–(e): expression, legal obligation/public interest, public health, archiving/research/statistics, legal claims |
| Recipients | Controller must notify each recipient of the erasure and tell the subject who they are on request | Art. 19 |
| Fees | Free unless manifestly unfounded or excessive | Art. 12(5) |
| Supervisory authority | Complaint to any supervisory authority | Art. 77 |
| Fines | Up to €20m or 4% of global turnover, whichever is higher | Art. 83(5) |

UK GDPR mirrors this with the ICO; the one-month clock and Art. 17 grounds are unchanged.

## 4. US state laws (2023–2026 wave)

The modal pattern is **45 days + 45-day extension**, with a 30-day cure period in some statutes and
none in others. Do not quote a state deadline you have not read. Verify at the state AG site or the
statute itself, and record the citation in the ledger note when you file.

**Twenty-one states** had comprehensive consumer privacy laws in force as of 2026-11 per LiveRamp's
own rights portal: Alabama, California, Colorado, Connecticut, Delaware, Indiana, Iowa, Kentucky,
Louisiana, Maryland, Minnesota, Montana, Nebraska, New Hampshire, New Jersey, Oklahoma, Oregon,
Rhode Island, Tennessee, Texas, Utah, Virginia. Treat that list as a starting point to verify, not
as an authority — it is a vendor's enumeration, and it will lag the next legislative session.

| State | Law | Response | Notes |
|---|---|---|---|
| California | CCPA/CPRA | 45 + 45 | See above; DROP is separate. See §6 for the 2027 expansion |
| Colorado | CPA | 45 + 45 | Universal opt-out required |
| Virginia | VCDPA | 45 + 45 | No universal opt-out mandate |
| Connecticut | CTDPA | 45 + 45 | Universal opt-out required; Public Act 26-64 adds a **data broker** law, so broker obligations are no longer California-only |
| Utah | UCPA | 45 + 45 | Narrower thresholds |
| Texas | TDPSA | 45 + 45 | AG enforcement only |
| Oregon | OCPA | 45 + 45 | Broad "sale" definition |
| Montana | MTDPA | 45 + 45 | Universal opt-out required |
| Kentucky | KPPA | 45 + 45 | 2026 effective |
| Delaware | DPDPA | 45 + 45 | 2025 effective |

If the subject is outside California, the DROP half of this harness does not apply. Use the
controller and processor paths only, and cite the subject's own state statute.

Four states now regulate data brokers specifically (California first and broadest). Connecticut's is
the newest. Only California has a universal deletion mechanism (DROP).

## 5. Adjacent duties that change what you can demand

- **Do Not Sell/Share + GPC**: opt-out, not deletion. Deleting data does not opt you out of future
  collection; do both.
- **Retention disclosure**: businesses must state retention periods. If the policy says "we keep it
  for 7 years", that is a fact to record, not a deletion failure.
- **Service providers** may refuse a deletion request sent directly to them when they hold the data
  solely as a processor (§1798.105(c) final paragraph). File with the controller instead.
- **Backups**: deletion obligations generally do not require instantaneous backup rewriting; the
  honest evidence is the vendor's stated backup expiry. Record it as a residual, not a failure.

## 6. What changed on 2026-09-27, and why it matters more than DROP

Two bills signed the same day, both effective **2027-01-01**. Together they are the strongest
argument in this file for doing the work now and re-running it in January.

### SB 923 (Expanding Privacy Rights Act, Ch. 482, Statutes of 2026)

Amends the right to delete (§1798.105) and the request-method duty (§1798.130). Sponsored by
CalPrivacy. The change that matters:

- Today: you may demand deletion of PI a business collected **"from"** you. Appended, inferred,
  purchased and identity-resolved data sits outside that wording, which is exactly the data brokers
  and ad-tech sell.
- From 2027-01-01: **"from or about"** you. Appended contact info, demographics, marketing segments,
  identity-resolution output and enrichment data become deletable, subject to the same §1798.105(d)
  exemptions.
- CalPrivacy frames the companion mechanism as a **suppression list**: a business may keep a record
  so deleted information is not reintroduced when it next acquires third-party data.

Harness consequences:

1. Requests filed before 2027-01-01 should be **re-filed or amended after that date**, not treated as
   complete. A 2026 deletion did not reach the enriched layer.
2. Ask for the suppression list explicitly in the request body; do not assume it.
3. Expect more "we cannot identify you in appended data" friction — the verification burden grows
   with the scope.

SB 923 does **not** import DROP's hashed-list matching or status reporting into the ordinary CCPA
process. Two different machines; keep them in separate parts of the ledger.

### Enforcement is no longer theoretical

| Action | Date | Amount | Why it matters here |
|---|---|---|---|
| LocateSmarter LLC | 2026-08-11 | $116,490 | First CalPrivacy action under **both** CCPA and the Delete Act: late broker registration plus requiring partial SSNs before honoring opt-outs (data minimization, 11 CCR §7002). |
| General Motors (with AG + 4 DAs) | 2026-05 | $12.75M | Connected-vehicle data sharing |
| PlayOn Sports | 2026-03 | $1.10M | Ticketing/analytics data |
| Background Alert | 2025-02 | shutdown or fine | Broker shut down over "scary amounts of information" marketing |

Use these as *enforcement exists* evidence in a pitch. Do not use them as a template for a consumer
payday — none of that money goes to a consumer.
