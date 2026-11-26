# dsrkit

**Track the statutory clock on your own data-deletion requests.** Enumerate the endpoints that
have to answer, file one request per endpoint, watch the 45-day deadlines, verify removal, and
produce an evidence pack that survives a regulator. Runs offline. Stdlib Python. No account, no
API key, no telemetry.

```
  21 states give you a right to delete. 1 state publishes a list of who to ask.
  Everyone else is left to enumerate the endpoints by hand.
```

## Why this exists

California has DROP: one free filing covers 625 registered data brokers. **No other state has
anything equivalent.** Colorado, Texas, Oregon and seventeen more give you the right, and leave the
enumeration — the actual hard part — to you. There is no shared list of request endpoints, and no
industry-wide intake standard.

This repo is that missing layer: a discovery tool, a ledger, a deadline calculator, and a
verification discipline. It does not sell anything and it does not phone home.

## What it does

| Tool | Job |
|---|---|
| `scripts/enumerate.py` | Finds a company's privacy-request intake with no registry: probes policy paths, fingerprints the DSR vendor, extracts the intake link, grades the result |
| `scripts/erasure.py` | The ledger: targets, filings, receipts, statutory deadlines, poll history, verification observations, evidence pack |

Both are stdlib-only Python 3.9+. No install step.

## Quickstart (Colorado example, ~10 minutes)

```bash
# 1. Find the intake channels for domains you care about
python3 scripts/enumerate.py --input domains.txt --gpc --out enumerated.json

# 2. Start a ledger — your identifiers, your keyboard
python3 scripts/erasure.py init --subject "self" --jurisdiction CO --state ~/privacy/ledger.json
python3 scripts/erasure.py identifiers --names "Legal Name" --dob 1980-01-01 \
    --zips 80202 --emails me@example.com --state ~/privacy/ledger.json
python3 scripts/erasure.py identifiers --show --state ~/privacy/ledger.json   # masked check

# 3. Add targets (paste the lines enumerate.py printed), then file and record the receipt
python3 scripts/erasure.py targets add --id acme --name "Acme" --class controller \
    --portal https://acme.example/privacy/request --state ~/privacy/ledger.json
python3 scripts/erasure.py file --target acme --method portal --state ~/privacy/ledger.json   # dry run
python3 scripts/erasure.py file --target acme --method portal --execute --attest self \
    --receipt "TICKET-1234" --state ~/privacy/ledger.json

# 4. Watch the clock; record what you observe
python3 scripts/erasure.py clock --state ~/privacy/ledger.json
python3 scripts/erasure.py poll --target acme --status in_progress --note "portal: processing" \
    --state ~/privacy/ledger.json

# 5. Verify, then package
python3 scripts/erasure.py verify --target acme --probe "public search: 0 results" \
    --result removed --independent --state ~/privacy/ledger.json
python3 scripts/erasure.py report --out evidence-pack.md --state ~/privacy/ledger.json
```

California residents get one extra step: file once at
<https://consumer.drop.privacy.ca.gov/>, keep the 8-digit DROP ID, and import the registry
(`curl -sSL https://cppa.ca.gov/data_broker_registry/registry.csv -o registry.csv`) as your broker
address book. Read `references/legal-clock.md` first — the DROP status vocabulary is not obvious,
and `Opted-out` does **not** mean deleted.

## What it will not do

- **It does not submit forms for you.** It prints the packet and records the receipt you come back
  with. Automated form-filling across third-party portals is a terms-of-service and CFAA problem,
  and DROP's own terms prohibit commercial exploitation of access.
- **It is not legal advice.** It cites statutes and does arithmetic. Read the cite before you quote it.
- **It does not file for anyone but you.** Requests for another person require their authorization
  (`templates/authorization-letter.md`); a request for a stranger is not a privacy request.
- **It does not promise money.** There is no private right of action for a missed deletion in any of
  these statutes. Your lever is a dated packet plus a regulator complaint.

## Design rules

1. **Dry run is the default.** Nothing is recorded as filed without `--execute --attest`.
2. **The ledger never holds secrets.** Identifiers only; API key prefixes only.
3. **No network in the ledger tool.** `erasure.py` makes zero network calls. `enumerate.py` makes
   exactly one GET per policy path, on domains you name, with a delay.
4. **A receipt is not a deletion.** Three verification tiers; only independent re-observation counts.
5. **The artifact is the product.** Dates, receipts, quotes, and URLs. Not a score.

## Privacy of the tool itself

Your ledger contains your name, date of birth, ZIP, email, phone in plain text. That is deliberate:
it is the minimum identifier set a controller needs, and it must not be encrypted behind something
you can lose. Keep it outside this repo — `.gitignore` excludes `ledger*.json`, `*.evidence/`, and
`enumerated.json` so an accidental `git add -A` cannot publish your identity.

## Status

`v0.1.0` — the ledger and deadline arithmetic are exercised end to end (10/10 self-test, full
file→poll→verify→report cycle run against a 625-broker registry). The enumerator has been run
against nine live domains and produces usable output, with the failures it should have: bot walls
return `NO-POLICY` rather than pretending.

**Known gaps, honestly:** Colorado's appeal clock (a second 45-day track) is not modelled yet; DSR
vendor fingerprints are heuristic; no state other than CA and CO has a worked request template;
there is no test suite beyond `python3 scripts/erasure.py selftest`.

## Contributing

Highest-value contributions, in order:

1. **Per-state request templates** — the statutory cites and the clock for one state, with a source
   URL. There are ~20 states without one.
2. **The appeal track** — a second deadline pair (`appeal_due`, `appeal_response_due`) in
   `request_deadlines()`, with the state's own numbers.
3. **DSR vendor fingerprints** — a real portal URL observed in the wild beats a guessed substring.
4. **Probe paths** — a country/industry variant that finds intakes the current eleven paths miss.

Please include the URL and the date you observed it. This repo prefers a dated fact to a plausible
one.

## Licence

Apache-2.0. See `LICENSE`.

## Files

- `scripts/erasure.py` — ledger, deadlines, verification, report
- `scripts/enumerate.py` — intake discovery for states with no registry
- `references/legal-clock.md` — statutes, clocks, penalties, exemptions, per-state table
- `references/endpoint-catalog.md` — discovery mechanics, DSR vendor fingerprints, DROP/Broker API
- `references/non-california-states.md` — the no-DROP path, Colorado worked example
- `references/tracking-scrub.md` — cut the join keys so deleted data is not re-acquired
- `references/verification-playbook.md` — evidence tiers, probe recipes, false positives
- `references/escalation-and-templates.md` — complaint routes and letter templates
- `references/model-layer.md` — the optional local-model seam, and why it is optional
- `templates/request-email.md`, `templates/authorization-letter.md`
