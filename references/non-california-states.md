# The no-DROP path: any US state that is not California

DROP is California-only. If the subject is a Colorado resident (or any non-CA state), there is **no
DROP ID, no universal filing, and no shared enumeration of endpoints**. The work does not get worse
— it gets *different*, and the enumeration becomes the whole job.

## 1. Rights attach to residence, not to an IP address

This matters because "delete by IP" is the intuitive model and it is not how the law is written.

| Claim | Reality |
|---|---|
| "A company must delete data tied to my IP on request" | No. The right belongs to a **consumer** who is a **resident** of a state with a law. An IP is evidence a business may use to *infer* where you are, and a handle for *finding* records — it is not the basis of the claim. |
| "So I can file as an IP" | You can *ask*, and they can decline as unverifiable. Colorado's CPA lets a controller refuse a request it cannot authenticate "with commercially reasonable effort" (§6-1-1306(1)). An IP-only request is exactly that case. |
| "IP-scoped deletion must be honored" | Tested where it matters: LiveRamp's own privacy page says it "does not maintain aggregate household data that we can link back to a single household" and directs anyone wanting a household/IP-wide request to submit a separate opt-out for **every email address** in the household. That is a no, with a redirect. |
| What IP actually buys you | Opt-outs, not deletion. Cookie- and device-scoped opt-outs are how the ad-tech layer honors a signal, and **GPC** is the one mechanism with a legal mandate behind it in Colorado. Use it; do not mistake it for erasure. |

So the honest framing: you are a Colorado consumer exercising a Colorado right, and your IP is a
search aid you can hand them alongside your identifiers. Lead with residence and identity, never
with the IP.

## 2. Colorado: what you actually have (verified 2026-11-23)

| Item | Rule | Source |
|---|---|---|
| Law | Colorado Privacy Act, C.R.S. §6-1-1301 et seq.; effective 2023-07-01 | SB 21-190 |
| Right to delete | Yes, as one of the §6-1-1306 consumer rights | §6-1-1306(1) |
| Response | 45 days from receipt; one extension of 45 more, with reasons given inside the first 45 | §6-1-1306(2)(a) |
| Denial | Must state reasons **and** the appeal path within 45 days | §6-1-1306(2)(b) |
| Appeal | Controller must run a real internal appeal; answer within 45 days, extendable 60 | §6-1-1306(3) |
| After appeal | Controller must tell you that you can contact the Attorney General | coag.gov CPA guidance |
| Universal opt-out | Since **2024-07-01**, controllers that sell data or run targeted ads must honor a UOOM meeting AG specs | §6-1-1306(1)(a)(IV)(B); §6-1-1313 |
| Which UOOM counts | **GPC is currently the only mechanism on the AG's list** | 4 CCR 904-3 Rule 5.07; coag.gov/uoom/ |
| GPC gotcha | The mechanism may **not** be a default setting shipped with a browser or OS — it must be the user's affirmative choice | 4 CCR 904-3 Rule 5.04 |
| Enforcement | AG and district attorneys only. **No private right of action.** | coag.gov CPA FAQ |
| Penalties | CPA violations are deceptive trade practices: up to $20,000 per violation | §6-1-112 |
| Cure period | **Expired 2025-01-01** (60-day cure until then); a narrow minors'-data cure runs to 2026-12-31 | §6-1-1311 |
| Complaint route | https://coag.gov/file-a-complaint/data-privacy-data-breach/ | coag.gov |
| Enforcement history | First CPA settlement: GM, announced 2026-10-29, $220M across 36 states / ~$7.18M to Colorado, effective 2026-11-30. Sep 2025: joined the CA/CT GPC investigative sweep. | coag.gov press release; consent judgment |

No private right of action is the single most important line here. Your leverage is a **clean
packet plus an AG complaint**, and the complaint has to show a missed statutory clock, not annoyance.

The narrow minors' cure expiring 2026-12-31 is worth knowing: after that, a Colorado violation is
fully cure-less, which makes a dated packet more useful to the AG, not less.

## 3. The enumeration problem, and the three seeds that solve it

There is no Colorado registry, no Colorado DROP, and no industry-wide list of request endpoints.
Three seeds cover what matters, in this order.

### Seed A — your own accounts (highest yield, zero discovery cost)

Start from what you actually use: bank, telco, insurer, employer, cloud, marketplace, grocery, gym,
airline, streaming, the apps on your phone. That is where the identity-linked data lives, and it is
where a deletion request produces a durable result. Export the account list from your password
manager rather than remembering it.

### Seed B — the CA broker registry as a national endpoint catalog

Counter-intuitive and effective: California publishes the only usable list of **broker** rights URLs,
and those portals accept requests from residents of other states with comprehensive laws. Evidence
that this works, from LiveRamp's own page: opt-out requests are "available to everyone in the US,
regardless of state of residence," and access/correction/**deletion** requests are offered to
residents of 21 named states — Colorado among them.

So: import the registry once, treat it as an address book, and file per broker. You lose the
one-shot convenience of DROP; you keep the coverage.

```bash
curl -sSL https://cppa.ca.gov/data_broker_registry/registry.csv -o registry.csv   # 625 brokers
python3 scripts/erasure.py targets import --csv registry.csv --state ./ledger.json
```

Expect friction DROP removed: per-broker forms, per-broker verification, and some portals that only
implement California. A refusal that cites "we only honor CCPA" is a fact to record, not a defeat —
it is the kind of gap DROP was built to close, and it is the argument for the product in §6.

### Seed C — discovery, which is now a script

```bash
python3 scripts/enumerate.py --input domains.txt --out enumerated.json --gpc
python3 scripts/enumerate.py spokeo.com whitepages.com --commands   # paste-ready targets add
```

What it does per domain: probes the eleven standard policy paths, fingerprints the DSR vendor
(OneTrust, Transcend, Ketch, TrustArc, DataGrail, Ethyca, MineOS, Osano, ...), extracts candidate
intake links and prefers a request form over a policy page, strips analytics junk from the URL, and
grades the result `STRONG / WEAK / NO-RIGHTS / NO-POLICY`. It also flags whether the policy even
mentions **Colorado** — a policy that names California, Connecticut, and Virginia but not Colorado
has not been updated, and will usually argue about the clock.

Limits, stated plainly: a 403 means a bot wall (use a real browser; see the `blocked-page-recovery`
skill), absence of a link is not proof of absence of a process, and one GET per path is the design —
this is not a crawler. Do not point it at a domain you have no relationship with at scale.

## 4. Filing as a Colorado consumer

```bash
python3 scripts/erasure.py init --subject "self" --jurisdiction CO --state ./ledger.json
python3 scripts/erasure.py identifiers --names "..." --dob ... --zips 80xxx --emails ... --phones ... --state ./ledger.json
python3 scripts/erasure.py targets add --id acme --name "Acme" --class controller --portal https://acme.example/privacy/request --state ./ledger.json
python3 scripts/erasure.py file --target acme --method portal --execute --attest self --receipt "TICKET-1234" --state ./ledger.json
python3 scripts/erasure.py clock --state ./ledger.json
```

The clock is right for controllers by default (45 + 45). What is missing is the appeal track: CO
gives you a second 45-day clock (plus 60) once you appeal a denial, and the harness does not model
that yet — when a denial arrives, file it as a **new request** with `--notes "appeal of <receipt>"`
and record the appeal deadline by hand in the note, or extend `request_deadlines` to carry an
`appeal_due` field.

Request body additions that a Colorado filing needs and a California one does not:

- cite **C.R.S. §6-1-1306(1)** (right) and **§6-1-1306(2)(a)** (45 days, one 45-day extension)
- demand the appeal instructions **in the denial itself**, per §6-1-1306(2)(b)
- cite the GPC/UOOM duty separately: **§6-1-1306(1)(a)(IV)(B)** + 4 CCR 904-3 Part 5. Opt-out and
deletion are two requests; send both.

## 5. Escalating in Colorado

1. Denial or silence past the deadline → appeal to the controller (their own process, conspicuously
   available, no harder than filing).
2. Appeal answered badly or not at all → AG complaint at
   https://coag.gov/file-a-complaint/data-privacy-data-breach/ with: the request, the receipt, the
   dates, the statutory cite, and what you asked for.
3. Send the whole evidence pack, not a narrative. The AG's office runs on documents.
4. Questions about the law (not a complaint): coprivacy@coag.gov.

Do not threaten a lawsuit under the CPA. There is no private right of action, and saying otherwise
marks the sender as unserious.

## 6. What this means for the business (the asymmetry nobody prices)

DROP made broker removal free and instant **in California only**. In Colorado — and in the other
~20 states with comprehensive laws — there is no universal mechanism, no shared enumeration, and no
free path. The consumer value proposition that died in California on 2026-08-01 is intact everywhere
else, and the cost driver there is exactly the thing that is worth paying for: discovery plus
verification labor.

Three consequences:

1. **Do not generalize the CA conclusion.** "The consumer market is dead" is a California statement.
2. **A non-CA resident is the honest case study.** Building the enumeration for yourself in Colorado
   exercises the hard part of the product, which California residents never see.
3. **Per-state differences are the moat and the cost.** Same machinery, different cites, different
   clocks, different appeal tracks. That is why a per-state service is defensible and a generic
   "delete me" subscription is not.

## 7. Order of operations for a Colorado subject

```
1  GPC on (user-selected, all browsers)        <- legally mandated in CO since 2024-07-01
2  Delete ad IDs, per-service email aliases    <- references/tracking-scrub.md
3  Seed A: your own accounts, file those first <- 45-day clock starts
4  Seed C: enumerate unknown domains, triage   <- STRONG/WEAK/NO-RIGHTS
5  Seed B: broker registry, file per broker    <- slow, high coverage
6  Poll on the clock; appeal denials; then AG  <- only with a dated packet
```
