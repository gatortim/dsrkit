# Tracking layer: scrubbing the ad-tech graph, not just the brokers

A DROP filing deletes rows in broker databases. It does not stop the same row being rebuilt next
month, because tracking does not need your name — it needs a **join key**. This file is the other
half of the job: cut the keys that let the graph re-identify you, and do it *before* spending money
on deletion.

## 1. The model: 3 join keys, 4 layers

You are re-identified by whichever key survives. Ranked by durability under deletion pressure:

| Join key | How it survives | What breaks it |
|---|---|---|
| **Hashed email / phone** (HEM, UID2, RampID) | Hashed, not encrypted — the hash is stable forever, and it is the key ad-tech matches on. Deleting the profile does nothing to the key. | One email per service (alias), so the key does not span your identity |
| **Device advertising ID** (MAID/IDFA/CTV ID) | Persists per device until reset/deleted | Delete the ID outright, not reset |
| **Cookie / first-party login** | Re-created on next visit; the logged-in account is the real join key | Container isolation, sign-out discipline, GPC |
| IP + fingerprint | Weakest, but re-links the above | Network-level filtering; do not bother with fingerprint spoofers |

Four layers must each be handled, because they have different owners:

```
L1 ad-tech identity graph  (LiveRamp, UID2, DAA members)   <- opt out, per identity key
L2 site tags & pixels      (your browser)                   <- GPC, blocking, isolation
L3 app SDKs & devices      (your phone, TV, car)            <- delete the advertising ID
L4 email & messaging       (your inbox)                     <- aliases, pixel blocking
```

## 2. Order of operations (this order, not another)

> Stop new collection -> break the join key -> delete history -> re-observe.

Deleting first and continuing to leak is how people pay for removal twice a year. Concretely:

1. **Turn on GPC** in every browser you use, and confirm the sites you care about honor it
   (section 4). This is a legal opt-out in CA/CO/CT/MT, not a preference.
2. **Delete the advertising IDs** on every device (section 3). A *reset* gives you a fresh key that
   immediately accumulates the same profile; a *delete* removes the key.
3. **Move high-value accounts to unique addresses** (section 5) so the HEM stops being a global
   join key. Start with the accounts that matter: bank, telco, employer, cloud, shopping.
4. **Then** file DROP + controller deletions (see `README.md` for the workflow), and add your MAID/CTV/VIN to the DROP
   profile — DROP accepts them and they are the only bridge from the broker world into the ad-tech
   world.
5. **Re-observe** on a schedule. Everything here decays: cookie opt-outs die when you clear
   cookies, a new phone ships with a new ID, and a new email address is a new key.

## 3. Device layer: verified controls

| Device | Control | What it does | Source |
|---|---|---|---|
| Android | Settings > Privacy > Ads > **Delete advertising ID** | Removes the ID; apps requesting it receive a string of zeros. (Reset only replaces it.) | Google Play services docs; Android Settings |
| Android (older, <=4.4) | Settings > Privacy > Advanced > Ads > Opt out of Ads Personalization | Older path, still opt-out only | Google Ads Help |
| Android TV / Google TV | Per-device Advertising ID reset/delete | Same semantics, separate ID per TV | Google My Ad Center help |
| iOS / iPadOS | Settings > Privacy & Security > Tracking > **Allow Apps to Request to Track = Off** | With this off, the device does **not have an IDFA at all** — there is no identifier to enter or leak. iOS does not expose the IDFA in the UI. | CalPrivacy, DROP unique-identifiers page |
| Smart TV | TV settings > advertising / ACR (automated content recognition) | Disables view-level tracking; ACR is the highest-value TV data and is usually a separate toggle from "ads" | CalPrivacy, DROP unique-identifiers page |
| Car | Connected-services / data-sharing settings in the vehicle or app | Connected-vehicle telematics is a live enforcement area (CA AG + CalPrivacy, GM, $12.75M, 2026) | CalPrivacy enforcement releases |

Enter the values you find into the DROP profile (`identifiers --maid`, `--ctv`, `--vin`). DROP
does not require them; they materially raise match rate.

## 4. Browser layer

**Do not wait for the browser to solve this.** As of 2026-11, Chrome still allows third-party
cookies by default: Google abandoned deprecation in July 2024, confirmed in April 2025 that there
would be no replacement consent prompt, and retired several Privacy Sandbox APIs on 2025-10-17.
Safari and Firefox have blocked third-party cookies for years. Browser choice is therefore a real
control, not a preference.

| Control | Effect | Caveat |
|---|---|---|
| **GPC signal** (`Sec-GPC: 1` header, `navigator.globalPrivacyControl === true`) | Legally binding opt-out of sale/share in CA, CO, CT, MT (list grows) | Only works if the site honors it — test it, don't assume |
| uBlock Origin (or equivalent network-level blocking) | Stops most tag loading before it fires | Does not stop server-side tagging; does not opt you out |
| Firefox Total Cookie Protection / per-site containers | Kills the cross-site cookie join | Logged-in accounts still link you |
| Clearing cookies | Removes cookie-based opt-outs too — you must redo L1 opt-outs after | Net negative if done casually |
| Fingerprint-randomizing extensions | Usually **increases** entropy (a rare configuration is a fingerprint) | Skip |

Test GPC honoring rather than trusting a badge:

```bash
# Does the site set an opt-out cookie / suppress ad tags when GPC is present?
curl -sSI -H 'Sec-GPC: 1' https://TARGET/ | grep -iE 'set-cookie|vary|gpc'
curl -sSL -H 'Sec-GPC: 1' https://TARGET/ | grep -oiE 'usprivacy|gpc|ccpa|optout|opt-out' | sort -u
```

A 200 response proves nothing. Evidence of honoring is a consent-state cookie, a suppressed tag, or
an explicit statement in the policy. Record which one you saw, with the date.

## 5. The hashed-email key (the one people miss)

The identity graph does not need your name. It needs `sha256(normalize(email))` — the hashed email
(HEM), which is what RampID and UID2 are computed from. One address used everywhere is one key that
joins every profile about you, and it survives deletion because it is arithmetic, not a record.

**Fix:** one address per service, on a domain you control (`tim+<service>@` or subaddresses), so any
single address maps to one relationship. Then:

- a leaked address identifies *which* vendor leaked it;
- deleting the profile kills the key for that relationship only;
- an address that starts receiving unexpected mail is a re-acquisition signal.

Rules: do not paste your real address (or its hash) into random "check your exposure" sites — that
is a fresh data collection event. Keep the alias map in the ledger's notes, not in chat.

## 6. Ad-tech identity opt-outs (verified 2026-11-23)

| Entity | Endpoint | Notes |
|---|---|---|
| **LiveRamp** (RampID) | https://liveramp.com/privacy/my-privacy-choices -> opt-out form; mobile: https://optout.liveramp.com/device_opt_out; cookie: https://optout.liveramp.com/opt_out_cookies; phone (844) 678-0045, code 1 | LiveRamp's own page says opt-out is **more effective than deletion** for reducing personalized ads; 15-day response for opt-out vs 45 days for deletion. Requires name + email for a comprehensive opt-out; cookie-only opt-out is per browser and dies when cookies are cleared. Honors GPC. |
| **UID2** (The Trade Desk) | https://www.transparentadvertising.org/ | One email or phone per submission. Opt-out propagates to publishers, DSPs, advertisers, sharers via the operator service; there is a lag while tokens refresh. Deletion/access requests: privacy@thetradedesk.com |
| **DAA WebChoices** | https://optout.aboutads.info/ | Per-browser cookie opt-out across participating companies; re-do after clearing cookies |
| **DAA AppChoices** | AppChoices app (iOS/Android) | Mobile-device opt-out across participating SDKs |
| **Google** | https://myadcenter.google.com (Personalized ads -> Off) | Turning it off deletes saved ad preferences and stops Google personalizing on partner sites/apps; contextual ads continue |
| **NAI opt-out tool** | **DO NOT CITE — dead** | The NAI ceased operation of its cookie/probabilistic IBA opt-out tool and its email-based identifier control tool on **2025-09-15**. Any playbook or checklist pointing at it is stale. |

For the ad-tech *deletion* (not opt-out) requests, these are `controller` targets in the ledger and
governed by the state statute, not by the DAA.

## 7. Verification: what is provable, and what is not

| Claim | Provable? | Probe |
|---|---|---|
| Broker deleted your row | Yes, per target | DROP status = Deleted; or a public lookup returns nothing (tier 2/3) |
| LiveRamp no longer uses your key for targeting | Partly | Opt-out receipt + subsequent opt-out re-check; you cannot read their graph |
| Site honors GPC | Yes, weakly | Suppressed tag / consent cookie under `Sec-GPC: 1` |
| Android advertising ID gone | Yes | Settings shows no ID, or app-side read returns zeros |
| iOS device has no IDFA | Yes | ATT off; the OS exposes no IDFA to read |
| "Your privacy score is 87" | No | Composite scores are marketing. Refuse to accept them as evidence |

Honest position: the ad-tech graph is not auditable from outside. What you can prove is that the
inputs you control (IDs, keys, signals, opt-outs) are in the state you set, with dates and receipts.
That is what a paid engagement should deliver — not a score.

## 8. Anti-patterns

1. **Buying a VPN and calling it scrubbed.** A VPN changes your IP; it does nothing about a logged-in
   account or a hashed email. IP is the weakest key in the set.
2. **Resetting instead of deleting the ad ID.** A reset hands you a brand-new key that starts
   collecting the same profile immediately.
3. **Clearing cookies after doing the ad-tech opt-outs.** You just deleted the opt-out cookies.
   Order matters; re-do L1 opt-outs after any cookie clear.
4. **Using fingerprint spoofers.** Rare = identifiable. Standard browser + GPC + blocking beats
   exotic configuration.
5. **Staying signed into Google/Facebook in the browser you use for everything.** The account is the
   join key that outlives every cookie control.
6. **Deleting before you stop collecting.** Guarantees re-acquisition and a second fee.
7. **Trusting a checklist dated before 2025-09.** The NAI tool is gone and Chrome's cookie plan was
   reversed; older playbooks are confidently wrong.

## 9. One-page baseline (fill this in once, then re-run quarterly)

```
DATE:            ____
Browsers:        ____  GPC on? Y/N   tested honoring: ____
Android:         ad ID deleted? Y/N   (Settings > Privacy > Ads)
iOS:             ATT off? Y/N        -> no IDFA exists if off
Smart TV / car:  ACR / telematics off? Y/N
Email:           aliases per service? Y/N   count: ____
LiveRamp:        opt-out receipt: ____  date: ____
cookie opt-out:  receipt: ____  date: ____
UID2:            emails submitted: ____  date: ____
DAA WebChoices:  cookie opt-out done: ____  date: ____
DROP:            ID: ____  MAID/CTV/VIN added? Y/N
Next re-check:   +90 days  ->  ____
```

Store the completed copy next to the ledger (outside any repo), not in the harness directory.
