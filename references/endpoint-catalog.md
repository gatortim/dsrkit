# Endpoint catalog: where deletion requests actually go

A deletion request is only as good as the endpoint it hits. This file is the enumeration layer:
where to look, what to capture, and how to tell a real intake channel from a marketing page.

## 0. Enumeration order

1. **Legally mandated bulk channel** — DROP, if the subject is a California resident. One filing,
   ~600 brokers. Do this first; it defines the baseline.
2. **Controllers with a direct relationship** — every account, subscription, app, and employer
   system the subject touches. This is where most real PI lives.
3. **DSR processors** — the vendor running the controller's intake (you still file per controller,
   but knowing the vendor tells you what verification and response pattern to expect).
4. **Machine identities** — accounts, keys, telemetry you operate.

## 1. Bulk sources

California Data Broker Registry (public, CSV). Verified reachable 2026-11-23:

```
https://cppa.ca.gov/data_broker_registry/registry.csv      <- current year (2026), 626 rows = 1 header + 625 brokers, 78 cols
https://cppa.ca.gov/data_broker_registry/registry2025.csv  <- 2025 (verified 200, ~337 KB)
https://cppa.ca.gov/data_broker_registry/registry2024.csv
https://cppa.ca.gov/data_broker_registry/complete-reg-data-brokers.csv   <- 2020-2023, DOJ era
```

URL traps, all confirmed by request rather than by reading docs:

- `cppa.ca.gov/registry.csv` (the link the page's HTML advertises, without the path) **404s**; the
  real file is under `/data_broker_registry/`.
- `registry2026.csv` does **not** exist. The current year is served as the unversioned
  `registry.csv`, so pin the URL by date in your notes, not by year.
- The `www.` host is not the canonical one; use `cppa.ca.gov`.

All 625 current rows carry a stated rights/deletion URL and a contact email, so a full import is
100% actionable — verified by running `targets import` against the downloaded file.
Earlier-year files carry a preamble row before the header; the importer sniffs the header row, so
both shapes work.

DROP (consumer side):

| Item | Value |
|---|---|
| Start | https://consumer.drop.privacy.ca.gov/ |
| Status | https://consumer.drop.privacy.ca.gov/dropstatus |
| ID recovery | https://consumer.drop.privacy.ca.gov/id_recovery |
| ID format | 8 digits (CalPrivacy says 8; treat 8-10 as accepted) |
| Live since | 2026-01-01 (consumers could file); brokers must process from 2026-08-01 |
| Required fields | name, DOB, ZIP |
| Optional, higher match rate | email, phone, MAID, CTV ID, VIN, aliases/maiden names |
| Residency check | California Identity Gateway, via Socure and Login.gov |
| Cost | free, always |
| Terms effective | 2025-12-05 |

DROP reports **five** per-broker statuses. Use these words verbatim in `poll --status`, because a
complaint that paraphrases them is harder to process:

| DROP status | Meaning | Ledger status |
|---|---|---|
| `Pending` | broker has not processed the request yet | `pending` |
| `Deleted` | matched, non-exempt PI deleted | `deleted` |
| `Exempted` | matched, but lawfully retained under an exemption | `exempted` |
| `Opted-out` | no exact match; broker keeps the data but may not sell/share it | `opted_out` |
| `Record not found` | broker has no record, or could not locate you | `record_not_found` |

`Opted-out` is the one people misread. It is **not** deletion — it is the statutory fallback for an
unverifiable match. Add identifiers and re-check rather than treating it as done.

DROP terms of use, quoted because they constrain how anyone may help another person file:

- prohibited: "(b) impersonate any person or entity or misrepresent your affiliation";
  "(e) reproduce, duplicate, copy, sell, resell or otherwise exploit for any commercial purposes,
  any portion of, use of, or access to DROP"
- permitted: "You are only permitted to aid another consumer with their deletion request if that
  person has authorized you to do so and you meet the requirements described in section 7001(d) of
  Title 11" — and you must disclose "your full name, email address, and business name if applicable".
  §7001(d) defines "authorized agent" by reference to §7063.

DROP (broker side, for the B2B product):

| Item | Value |
|---|---|
| Production API | `https://api.drop.privacy.ca.gov` |
| Sandbox | `https://api.drop.privacy.ca.gov/sandbox` |
| Auth | `X-API-KEY: <key scoped to the broker's selected list(s)>` |
| Flow | download hashed list → hash own records → match → upload status CSV (deleted / opted out / exempted / not found) |
| Cycle | 45 days (30 from 2027-01-01) |
| Docs | cppa.ca.gov/orph/drop_tech_api_ref.pdf (+ OpenAPI YAML linked there) |

Hashing and matching details, status-file naming, and the exact CSV schema live in the CalPrivacy
tech reference, not here. Read it before writing an integration; it changes.

## 2. Finding a controller's intake channel

Fast path, in order:

```bash
for p in /privacy /legal/privacy /privacy-policy /legal/privacy-policy /privacy/request \
         /do-not-sell /your-privacy-choices; do
  printf '%s -> ' "$p"; curl -s -o /dev/null -w '%{http_code}\n' -L "https://TARGET$p"
done
curl -sL https://TARGET/privacy | grep -oiE 'https?://[^"'\''<> ]*(onetrust|transcend|ketch|trustarc|truste|datagrail|ethyca|osano|didomi|usercentrics|sourcepoint|cookiebot|iubenda|termly)[^"'\''<> ]*' | sort -u
```

Then read the policy for the legally required sentence — it names the method: "To submit a request
to delete, email privacy@… or use our webform at …". That sentence is the endpoint of record. If
the policy has no such sentence, the controller is likely out of compliance and the **absence is
itself evidence** — record the URL and date.

Capture per endpoint (this becomes the ledger note):

| Field | Why |
|---|---|
| intake URL / email / postal address | where the request goes |
| method named in the policy | proves the channel is designated |
| verification demanded | predicts friction and clock disputes |
| DSR vendor | predicts response shape and portal quirks |
| governing law / state | which clock applies |
| policy "last updated" date | versions matter when a target changes its story |
| retention statement | what "deleted" can even mean here |

## 3. DSR processor fingerprints (heuristics, verify before relying)

| Vendor | Hints in page source / network | Typical shape |
|---|---|---|
| OneTrust | `privacyportal.onetrust.com`, `app.onetrust.com`, `OptanonConsent`, `OptanonAlertBoxClosed`, `cdn.cookielaw.org` | hosted webform, email verification link |
| Transcend | `transcend.io`, `sombra.transcend.io`, `/v1/data-subject-request` on their API | portal + API, fast automated fulfilment |
| Ketch | `ketch.com`, `global.ketchcdn.com`, forwarder endpoints | portal + forwarding to downstream systems |
| TrustArc | `trustarc.com`, `consent.trustarc.com`, `truste.com` | older consent UI, form with long verification |
| DataGrail | `datagrail.io`, `integration.datagrail.io` | portal, strong identity verification |
| Ethyca / Fides | `ethyca.com`, `privacy.ethyca.com` | portal + open-source fulfilment |
| Osano / Didomi / Usercentrics / Sourcepoint / Cookiebot / iubenda / Termly | vendor domain in consent script tags | consent-first; DSR form may be separate |

A fingerprint tells you **what experience to expect and where the receipt comes from**. It does not
tell you who is legally responsible: the controller is. File with the controller, always, even when
the form is hosted by a processor.

## 4. Do Not Sell/Share and GPC (separate from deletion)

- Header: `Sec-GPC: 1`. JS: `navigator.globalPrivacyControl === true`.
- States requiring recognition as of 2026: California, Colorado, Connecticut, Montana (check the
  current list — it grows each legislative session, and CalPrivacy has proposed opt-out-signal rules).
- Test whether a site honors it: load the site with `Sec-GPC: 1`, then check for an opt-out cookie,
  a `sale_opt_out`-style flag, or suppressed ad tags. A 200 response proves nothing.
- Record opt-out and deletion as **separate** requests. Deleting data does not stop future
  collection, and opting out does not delete history.
- Industry opt-out tooling is decaying, so cite the live ones only: DAA WebChoices
  (https://optout.aboutads.info/) and AppChoices are current; **the NAI discontinued its cookie and
  email-identifier opt-out tools on 2025-09-15** — any playbook pointing there is stale.
  Identity-graph endpoints and device controls: `references/tracking-scrub.md`.

## 5. Machine identity inventory (no statute, so be exhaustive)

| Layer | What to enumerate | How deletion is verified |
|---|---|---|
| Identity | tenant/account ID, admin email, SSO subject | login returns 404/410; SSO login fails |
| Credentials | API keys, OAuth clients, service accounts, PATs, webhooks (store prefixes only) | key use → 401/403; webhook stops firing |
| Data | stored objects, indexes, embeddings, fine-tunes | authenticated read → 404 or empty |
| Telemetry | product analytics, logs, traces, error reports | no events after T0 for the subject ID |
| Vendors | subprocessors holding copies | written confirmation + stated expiry |
| Training | any model trained on the subject's data | written statement; retraining is not a deletion |
| Backups | snapshots, WAL, cold storage | stated expiry window, recorded as residual |

Agents: the machine's "personal information" is whatever the contract and the privacy policy say it
is. Quote the policy clause in the request; you have no statutory hook to fall back on.

## 6. Anti-patterns

- Filing through a "contact us" form with no privacy routing — no clock starts, no receipt exists.
- Filing with a processor who holds the data solely for a controller (§1798.105(c) lets them refuse).
- Scraping broker sites to "enumerate" — use the registry; scraping invites ToS and CFAA arguments.
- Building a paid DROP lookalike — CalPrivacy's free promise is the product's trust anchor.
