#!/usr/bin/env python3
"""erasure.py - ledger for privacy deletion requests (CCPA/CPRA, Delete Act DROP, GDPR Art. 17).

Design rules, in order of importance:
  1. Dry run is the default. Nothing is recorded as filed without --execute --attest.
  2. The ledger never stores secrets: identifiers only, key prefixes only.
  3. The script does not submit forms. It produces the packet, records the receipt you
     come back with, and does the statutory date arithmetic that humans get wrong.

stdlib only. No network calls anywhere in this file.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import pathlib
import sys
import uuid

VERSION = 1
DEFAULT_STATE = pathlib.Path.home() / ".local" / "share" / "privacy-erasure" / "ledger.json"

CCPA_ACK_BUSINESS_DAYS = 10          # 11 CCR 7021(a)
CCPA_RESPONSE_DAYS = 45              # Civ. Code 1798.130(a)(2); +45 extension
CCPA_EXTENSION_DAYS = 45
DROP_CYCLE_DAYS = 45                 # Civ. Code 1798.99.86, until 2026-12-31
DROP_CYCLE_DAYS_2027 = 30            # AB 883, from 2027-01-01
MACHINE_CONTRACT_DAYS = 30           # no statute for a machine identity; use contract SLA
DROP_STATUS_VISIBLE_DAYS = 90        # platform-stated lag

OPEN_STATUSES = {
    "filed", "acknowledged", "in_progress", "pending",
    # DROP statuses that mean "not done yet" — the clock keeps running and you keep polling:
    "opted_out",        # no exact match; data retained but sale/share barred -> add identifiers
    "record_not_found",  # no record, or could not locate the subject -> add identifiers
}
CLOSED_STATUSES = {
    "completed", "denied", "no_record", "withdrawn",
    # DROP statuses that genuinely close the request:
    "deleted",        # matched, non-exempt PI deleted
    "exempted",       # matched, lawfully retained under an exemption
}
VALID_STATUSES = OPEN_STATUSES | CLOSED_STATUSES
VALID_CLASSES = {"broker", "controller", "processor", "machine"}
VALID_ATTEST = {"self", "authorization", "contract"}
VALID_RESULTS = {"removed", "present", "inconclusive"}


# ---------------------------------------------------------------- date helpers


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"bad date {value!r}: expected YYYY-MM-DD ({exc})")


def add_days(day: dt.date, count: int) -> dt.date:
    return day + dt.timedelta(days=count)


def add_business_days(day: dt.date, count: int) -> dt.date:
    """Weekdays only. Federal/state holidays are deliberately NOT modeled."""
    current, added = day, 0
    while added < count:
        current += dt.timedelta(days=1)
        if current.weekday() < 5:
            added += 1
    return current


def drop_cycle_days(day: dt.date) -> int:
    return DROP_CYCLE_DAYS_2027 if day >= dt.date(2027, 1, 1) else DROP_CYCLE_DAYS


# ---------------------------------------------------------------------- ledger


def load_state(path: pathlib.Path) -> dict:
    if not path.exists():
        raise SystemExit(f"no ledger at {path}; run `init` first")
    state = json.loads(path.read_text())
    state.setdefault("targets", {})
    state.setdefault("requests", [])
    return state


def save_state(path: pathlib.Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True))
    tmp.replace(path)


def resolve_state(args) -> pathlib.Path:
    return pathlib.Path(args.state).expanduser() if args.state else DEFAULT_STATE


def find_target(state: dict, target_id: str) -> dict:
    target = state["targets"].get(target_id)
    if not target:
        raise SystemExit(f"unknown target {target_id!r}; see `targets list`")
    return target


def open_requests(state: dict):
    return [r for r in state["requests"] if r.get("status") in OPEN_STATUSES]


def request_deadlines(request: dict) -> dict:
    filed = parse_date(request["filed_on"])
    if request.get("class") == "broker":
        cycle = drop_cycle_days(filed)
    elif request.get("class") == "machine":
        cycle = MACHINE_CONTRACT_DAYS
    else:
        cycle = CCPA_RESPONSE_DAYS
    return {
        # Brokers owe no acknowledgment under DROP: the obligation is the access/process cycle,
        # not the CCPA's 10-business-day ack. Showing a CCPA ack date on a broker row is a
        # credibility bug in the evidence pack.
        "ack": None if request.get("class") == "broker"
        else add_business_days(filed, CCPA_ACK_BUSINESS_DAYS),
        "response": add_days(filed, cycle),
        "extension": add_days(filed, cycle + CCPA_EXTENSION_DAYS) if cycle == CCPA_RESPONSE_DAYS else None,
        "status_visible": add_days(filed, DROP_STATUS_VISIBLE_DAYS) if request.get("class") == "broker" else None,
    }


def _iso_or_dash(value):
    return value.isoformat() if value else "-"


# -------------------------------------------------------------------- commands


def cmd_init(args) -> None:
    path = resolve_state(args)
    if path.exists() and not args.force:
        raise SystemExit(f"ledger exists at {path}; pass --force to replace")
    state = {
        "version": VERSION,
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "subject": {
            "label": args.subject,
            "jurisdiction": args.jurisdiction,
            "basis": None,
            "identifiers": {"names": [], "emails": [], "phones": [], "zips": [], "dob": None},
        },
        "targets": {},
        "requests": [],
    }
    save_state(path, state)
    print(f"created {path}")
    print("next: set identifiers (edit the file), add targets, then `file --target ...`")


def cmd_targets(args) -> None:
    path = resolve_state(args)
    state = load_state(path)

    if args.targets_cmd == "add":
        if args.id in state["targets"]:
            raise SystemExit(f"target {args.id!r} already exists; edit the ledger to change it")
        state["targets"][args.id] = {
            "name": args.name,
            "class": args.klass,
            "portal": args.portal,
            "email": args.email,
            "notes": args.notes or "",
            "added_at": dt.date.today().isoformat(),
        }
        save_state(path, state)
        print(f"added {args.id} ({args.klass})")
        return

    if args.targets_cmd == "list":
        if not state["targets"]:
            print("no targets yet")
            return
        rows = sorted(state["targets"].items(), key=lambda kv: (kv[1]["class"], kv[0]))
        width = max(len(k) for k, _ in rows)
        print(f"{'id'.ljust(width)}  class       name")
        print(f"{'-' * width}  ----------  ----")
        for tid, t in rows:
            print(f"{tid.ljust(width)}  {t['class']:<10}  {t['name']}")
        print(f"\n{len(rows)} targets")
        return

    if args.targets_cmd == "import":
        source = pathlib.Path(args.csv).expanduser()
        if not source.exists():
            raise SystemExit(f"no csv at {source}")
        with source.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.reader(handle))
        header_index = _find_header(rows)
        if header_index is None:
            raise SystemExit("no header row found (need a row naming both a broker and a website column)")
        headers = [_norm_header(h) for h in rows[header_index]]
        added = duplicate = with_rights = with_email = 0
        for row in rows[header_index + 1:]:
            if not any(cell.strip() for cell in row):
                continue
            record = dict(zip(headers, [cell.strip() for cell in row]))
            name = _field(record, "broker", "name") or _field(record, "name")
            if not name:
                continue
            tid = _unique_slug(_slug(name), state["targets"])
            rights = _field(record, "website", "delete") or _field(record, "rights", "website")
            website = _field(record, "primary website", exclude=("delete", "rights", "consumer"))
            email = _field(record, "email")
            phone = _field(record, "phone")
            city = _field(record, "city")
            region = _field(record, "state")
            median = _field(record, "median", "delete")
            notes = [f"imported from {source.name}"]
            if city or region:
                notes.append(f"{city}, {region}".strip(", "))
            if median:
                notes.append(f"self-reported median days to delete (2023): {median}")
            state["targets"][tid] = {
                "name": name,
                "class": "broker",
                "portal": rights or "",
                "website": website,
                "email": email,
                "phone": phone,
                "notes": "; ".join(notes),
                "added_at": dt.date.today().isoformat(),
            }
            added += 1
            with_rights += 1 if rights else 0
            with_email += 1 if email else 0
            if args.limit and added >= args.limit:
                break
        save_state(path, state)
        print(f"imported {added} brokers from {source.name}")
        print(f"  with a stated deletion/rights URL: {with_rights}")
        print(f"  with a contact email:              {with_email}")
        neither = sum(1 for t in state["targets"].values() if not t.get("portal") and not t.get("email"))
        print(f"  no portal and no email:            {neither}")
        print("DROP is one filing for all registered brokers; individual portals are for disputes.")
        return

    raise SystemExit("targets: expected add|list|import")


def _cites(klass: str) -> list:
    if klass == "broker":
        return [
            "Cal. Civ. Code 1798.105 (right to delete)",
            "Cal. Civ. Code 1798.99.86 (DROP; $200 per request per day, administrative fine)",
            "Cal. Civ. Code 1798.130(a)(2); 11 CCR 7021 (timelines)",
        ]
    if klass == "machine":
        return [
            "No statutory right for a machine identity: contractual / security hygiene only",
            "Record the vendor's stated retention and backup expiry window, not a legal deadline",
        ]
    return [
        "Cal. Civ. Code 1798.105 (right to delete)",
        "Cal. Civ. Code 1798.130(a)(2) (45 days, +45)",
        "11 CCR 7021 (10 business days ack); 11 CCR 7022 (requests to delete)",
    ]


def _norm_header(raw: str) -> str:
    text = raw.replace("\xa0", " ").replace("\u2019", "'").strip().rstrip(":").strip().lower()
    return " ".join(text.split())


def _find_header(rows):
    for index, row in enumerate(rows[:10]):
        joined = " ".join(_norm_header(cell) for cell in row)
        if "name" in joined and ("website" in joined or "url" in joined):
            return index
    return None


def _field(record: dict, *needles, exclude=()) -> str:
    for key, value in record.items():
        if all(needle in key for needle in needles) and not any(bad in key for bad in exclude):
            if value and value.strip() and value.strip().upper() != "N/A":
                return value.strip()
    return ""


def _unique_slug(slug: str, targets: dict) -> str:
    if slug not in targets:
        return slug
    index = 2
    while f"{slug}-{index}" in targets:
        index += 1
    return f"{slug}-{index}"


def _both(state: dict) -> list:
    return [t for t in state["targets"].values() if t.get("portal") and t.get("email")]


def _pick(fieldnames, candidates):
    lowered = {f.lower().strip(): f for f in fieldnames if f}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    for candidate in candidates:
        for low, original in lowered.items():
            if candidate in low:
                return original
    return None


def _slug(name: str) -> str:
    keep = [c.lower() if c.isalnum() else "-" for c in name]
    slug = "".join(keep).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug[:48] or "target"


def cmd_file(args) -> None:
    path = resolve_state(args)
    state = load_state(path)
    target = find_target(state, args.target)
    filed = parse_date(args.filed_on) if args.filed_on else dt.date.today()
    if target["class"] == "broker":
        cycle = drop_cycle_days(filed)
    elif target["class"] == "machine":
        cycle = MACHINE_CONTRACT_DAYS
    else:
        cycle = CCPA_RESPONSE_DAYS

    packet = {
        "target": target["name"],
        "class": target["class"],
        "method": args.method,
        "destination": target["portal"] if args.method in ("portal", "api") else target["email"],
        "filed_on": filed.isoformat(),
        "ack_due": _iso_or_dash(None if target["class"] == "broker"
                                else add_business_days(filed, CCPA_ACK_BUSINESS_DAYS)),
        "response_due": add_days(filed, cycle).isoformat(),
        "identifiers": state["subject"]["identifiers"],
        "cites": _cites(target["class"]),
    }
    if not packet["destination"]:
        print(f"WARNING: target {args.target!r} has no portal or email. `targets add --portal/--email` first.")

    if not args.execute:
        print("DRY RUN - nothing recorded. Packet:\n")
        print(json.dumps(packet, indent=2))
        print("\nAfter you submit and receive a confirmation, re-run with:")
        print(f"  file --target {args.target} --method {args.method} --execute "
          f"--attest <self|authorization|contract> --receipt <ID>")
        return

    if args.attest not in VALID_ATTEST:
        raise SystemExit("refuse to record a filing without --attest self|authorization|contract")
    if not args.receipt and not args.allow_no_receipt:
        raise SystemExit("refuse to record a filing without --receipt <confirmation id> (or --allow_no_receipt)")

    record = {
        "id": uuid.uuid4().hex[:8],
        "target": args.target,
        "target_name": target["name"],
        "class": target["class"],
        "method": args.method,
        "attest": args.attest,
        "filed_on": filed.isoformat(),
        "recorded_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "receipt": args.receipt,
        "identifiers": state["subject"]["identifiers"],
        "status": "filed",
        "polls": [],
        "observations": [],
        "exemption": None,
    }
    state["requests"].append(record)
    state["subject"]["basis"] = args.attest
    save_state(path, state)
    print(f"recorded request {record['id']} for {target['name']}")
    print(f"  ack due      {packet['ack_due']}")
    print(f"  response due {packet['response_due']}")


def cmd_poll(args) -> None:
    path = resolve_state(args)
    state = load_state(path)
    if args.status not in VALID_STATUSES:
        raise SystemExit(f"status must be one of {sorted(VALID_STATUSES)}")
    matches = [r for r in state["requests"] if r["target"] == args.target and r["status"] in OPEN_STATUSES]
    if not matches:
        raise SystemExit(f"no open request for {args.target!r}")
    record = matches[-1]
    entry = {
        "at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": args.status,
        "note": args.note or "",
        "evidence": args.evidence,
    }
    record["polls"].append(entry)
    record["status"] = args.status
    if args.exemption:
        record["exemption"] = args.exemption
    save_state(path, state)
    print(f"{args.target}: {args.status}" + (f" (exemption: {args.exemption})" if args.exemption else ""))


def cmd_clock(args) -> None:
    path = resolve_state(args)
    state = load_state(path)
    today = parse_date(args.as_of) if args.as_of else dt.date.today()
    requests = open_requests(state)
    if not requests:
        print(f"no open requests as of {today}")
        return
    print(f"as of {today}  ({len(requests)} open)\n")
    header = f"{'target':<26} {'filed':<11} {'day':>4} {'ack':<11} {'respond by':<11} {'left':>5}  flag"
    print(header)
    print("-" * len(header))
    overdue = 0
    for record in sorted(requests, key=lambda r: r["filed_on"]):
        filed = parse_date(record["filed_on"])
        due = request_deadlines(record)
        left = (due["response"] - today).days
        flag = ""
        if left < 0:
            flag = f"OVERDUE {abs(left)}d"
            overdue += 1
        elif left <= 7:
            flag = "due soon"
        if due["ack"] and due["ack"] >= today and record["status"] == "filed":
            flag = (flag + " ack pending").strip()
        name = record.get("target_name", record["target"])[:26]
        print(f"{name:<26} {record['filed_on']:<11} {(today - filed).days:>4} "
              f"{_iso_or_dash(due['ack']):<11} {due['response'].isoformat():<11} {left:>5}  {flag}")
    print(f"\n{overdue} overdue. Holidays are not modeled; add a buffer before escalating.")


def cmd_verify(args) -> None:
    path = resolve_state(args)
    state = load_state(path)
    if args.result not in VALID_RESULTS:
        raise SystemExit(f"result must be one of {sorted(VALID_RESULTS)}")
    matches = [r for r in state["requests"] if r["target"] == args.target]
    if not matches:
        raise SystemExit(f"no request for {args.target!r}")
    record = matches[-1]
    tier = 3 if args.independent else 2
    record["observations"].append({
        "at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "tier": tier,
        "probe": args.probe,
        "result": args.result,
        "evidence": args.evidence,
        "note": args.note or "",
    })
    save_state(path, state)
    print(f"{args.target}: tier {tier} observation recorded as {args.result}")
    if args.result == "removed" and tier < 3:
        print("note: tier 2 is the target's own word. Schedule a tier 3 re-observation.")


def _mask(value: str) -> str:
    if not value:
        return "-"
    if "@" in value:
        local, _, domain = value.partition("@")
        return f"{local[:1]}{'*' * max(1, len(local) - 1)}@{domain}"
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) >= 4:
        return f"***{digits[-4:]}"
    return value[:1] + "*" * max(1, len(value) - 1)


def cmd_identifiers(args) -> None:
    path = resolve_state(args)
    state = load_state(path)
    ids = state["subject"]["identifiers"]

    def split(value):
        return [item.strip() for item in (value or "").split(",") if item.strip()]

    updates = {
        "names": split(args.names),
        "emails": split(args.emails),
        "phones": split(args.phones),
        "zips": split(args.zips),
        "dob": (args.dob or "").strip() or None,
        "maid": (args.maid or "").strip() or None,
        "ctv_id": (args.ctv or "").strip() or None,
        "vin": (args.vin or "").strip() or None,
    }
    if not args.show:
        changed = {k: v for k, v in updates.items() if v}
        if not changed:
            raise SystemExit("nothing to set; pass --names/--dob/--zips/... or --show")
        for key, value in changed.items():
            ids[key] = value
        save_state(path, state)
        print(f"updated {path}: {', '.join(sorted(changed))}")
        print("values are stored in plain text in the ledger; keep that file out of git.")

    print("current identifiers (masked):")
    for key in ("names", "dob", "zips", "emails", "phones", "maid", "ctv_id", "vin"):
        value = ids.get(key)
        if isinstance(value, list):
            shown = ", ".join(_mask(v) for v in value) if value else "-"
        else:
            shown = _mask(value) if value else "-"
        print(f"  {key:<8} {shown}")


def cmd_preflight(args) -> None:
    path = resolve_state(args)
    state = load_state(path)
    subject = state["subject"]
    ids = subject["identifiers"]
    filled = {k: v for k, v in ids.items() if v}
    print(f"subject: {subject['label']}  jurisdiction: {subject['jurisdiction']}  basis: {subject.get('basis') or 'unset'}")
    print()
    print("identifier coverage (DROP fields):")
    for label, key, required in (
        ("legal name + aliases", "names", True),
        ("date of birth", "dob", True),
        ("ZIP", "zips", True),
        ("email(s)", "emails", False),
        ("phone(s)", "phones", False),
        ("mobile advertising ID", "maid", False),
        ("connected TV ID", "ctv_id", False),
        ("VIN", "vin", False),
    ):
        value = ids.get(key)
        mark = "set" if value else ("MISSING" if required else "-")
        print(f"  {label:<24} {mark}")
    print()
    targets = state["targets"]
    by_class = {}
    for t in targets.values():
        by_class[t["class"]] = by_class.get(t["class"], 0) + 1
    print(f"targets: {len(targets)}  " + "  ".join(f"{k}={v}" for k, v in sorted(by_class.items())))
    brokers = [t for t in targets.values() if t["class"] == "broker"]
    no_channel = [t for t in targets.values() if not t.get("portal") and not t.get("email")]
    print(f"  brokers covered by one DROP filing: {len(brokers)}")
    print(f"  targets with no portal or email:    {len(no_channel)}")
    print()
    blockers = []
    if subject["jurisdiction"].upper() != "CA":
        blockers.append("jurisdiction is not CA: DROP does not apply, use controller paths only")
    for key in ("names", "dob", "zips"):
        if not ids.get(key):
            blockers.append(f"identifier missing: {key}")
    if blockers:
        print("BLOCKED:")
        for item in blockers:
            print(f"  - {item}")
        print(f"\nFill them in {path} under subject.identifiers, then re-run preflight.")
        return
    print("READY for DROP: submit at https://consumer.drop.privacy.ca.gov/ (residency check first),")
    print("then record it:  file --target <target> --method api --execute --attest self --receipt <DROP ID>")
    print("Drop the 8-digit DROP ID into the ledger note so status polls can cite it.")


def cmd_report(args) -> None:
    path = resolve_state(args)
    state = load_state(path)
    today = dt.date.today()
    subject = state["subject"]
    lines = [
        "# Deletion evidence pack",
        "",
        f"Generated: {dt.datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"Subject: {subject['label']}  |  Jurisdiction: {subject['jurisdiction']}  |  Basis: {subject.get('basis') or 'unrecorded'}",
        f"Identifiers submitted: {', '.join(k for k, v in subject['identifiers'].items() if v) or 'none recorded'}",
        "",
        "## Summary",
        "",
        f"- targets enumerated: {len(state['targets'])}",
        f"- requests filed: {len(state['requests'])}",
        f"- open: {len(open_requests(state))}",
        f"- closed: {sum(1 for r in state['requests'] if r['status'] in CLOSED_STATUSES)}",
        f"- tier-3 verified removals: {sum(1 for r in state['requests'] if any(o['tier'] == 3 and o['result'] == 'removed' for o in r['observations']))}",
        "",
        "## Requests",
        "",
    ]
    overdue = []
    for record in sorted(state["requests"], key=lambda r: r["filed_on"]):
        due = request_deadlines(record)
        left = (due["response"] - today).days
        lines.append(f"### {record['target_name']} ({record['target']})")
        lines.append("")
        lines.append(f"- class: {record['class']}  method: {record['method']}  attestation: {record['attest']}")
        lines.append(f"- filed: {record['filed_on']}  receipt: {record['receipt'] or 'MISSING'}")
        lines.append(f"- status: {record['status']}")
        lines.append(f"- ack due: {_iso_or_dash(due['ack'])}  response due: {due['response'].isoformat()}  days left: {left}")
        if record.get("exemption"):
            lines.append(f"- exemption cited: {record['exemption']}")
        for poll in record["polls"]:
            lines.append(f"  - poll {poll['at']}: {poll['status']} {poll['note']}".rstrip())
        for obs in record["observations"]:
            lines.append(f"  - verify {obs['at']} tier {obs['tier']}: {obs['result']} - {obs['probe']}"
                         + (f" [{obs['evidence']}]" if obs.get("evidence") else ""))
        if left < 0 and record["status"] in OPEN_STATUSES and not record.get("exemption"):
            overdue.append(record)
        lines.append("")
    if overdue:
        lines.append("## Overdue - complaint ready")
        lines.append("")
        for record in overdue:
            lines.append(f"- {record['target_name']}: {abs((request_deadlines(record)['response'] - today).days)} days past the response deadline, no substantive reply recorded")
        lines.append("")
        lines.append("Statutory basis: Civ. Code 1798.130(a)(2); 11 CCR 7021. For brokers, Civ. Code 1798.99.86.")
    body = "\n".join(lines) + "\n"
    if args.out:
        out = pathlib.Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(body)
        print(f"wrote {out} ({len(body)} chars)")
    else:
        print(body)


def cmd_selftest(_args) -> None:
    checks = []

    def check(label, got, want):
        checks.append((label, got, want, got == want))

    check("45 days from 2026-11-23", add_days(dt.date(2026, 11, 23), CCPA_RESPONSE_DAYS), dt.date(2027, 1, 7))
    check("10 business days from Mon 2026-11-23", add_business_days(dt.date(2026, 11, 23), CCPA_ACK_BUSINESS_DAYS), dt.date(2026, 12, 7))
    check("business days skip weekend", add_business_days(dt.date(2026, 11, 27), 1), dt.date(2026, 11, 30))
    check("DROP cycle 2026", drop_cycle_days(dt.date(2026, 8, 1)), 45)
    check("DROP cycle 2027", drop_cycle_days(dt.date(2027, 1, 1)), 30)
    check("slug", _slug("Acme, Inc. (US)"), "acme-inc-us")
    check("machine contract cycle", request_deadlines({"filed_on": "2026-11-01", "class": "machine"})["response"], dt.date(2026, 12, 1))
    check("deadlines broker", request_deadlines({"filed_on": "2026-08-01", "class": "broker"})["response"], dt.date(2026, 9, 15))
    check("deadlines controller extension", request_deadlines({"filed_on": "2026-08-01", "class": "controller"})["extension"], dt.date(2026, 10, 30))
    check("90 day visibility", request_deadlines({"filed_on": "2026-08-01", "class": "broker"})["status_visible"], dt.date(2026, 10, 30))

    failures = 0
    for label, got, want, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {label}: got {got} want {want}")
        failures += 0 if ok else 1
    print(f"\n{len(checks) - failures}/{len(checks)} passed")
    if failures:
        raise SystemExit(1)


# ------------------------------------------------------------------------ main


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="erasure", description=__doc__.splitlines()[0])
    parser.add_argument("--state", help=f"ledger path (default {DEFAULT_STATE})")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init", help="create a ledger for one subject")
    p.add_argument("--subject", required=True)
    p.add_argument("--jurisdiction", default="CA")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("targets", help="manage the target list")
    p.add_argument("targets_cmd", choices=["add", "list", "import"])
    p.add_argument("--id")
    p.add_argument("--name")
    p.add_argument("--class", dest="klass", choices=sorted(VALID_CLASSES), default="controller")
    p.add_argument("--portal")
    p.add_argument("--email")
    p.add_argument("--notes")
    p.add_argument("--csv", help="registry csv for import")
    p.add_argument("--limit", type=int, help="cap rows imported")
    p.set_defaults(func=cmd_targets)

    p = sub.add_parser("file", help="print (or record) a request packet")
    p.add_argument("--target", required=True)
    p.add_argument("--method", choices=["portal", "email", "api", "mail"], default="portal")
    p.add_argument("--filed-on", help="YYYY-MM-DD if recorded after the fact")
    p.add_argument("--receipt", help="confirmation / ticket id")
    p.add_argument("--attest", choices=sorted(VALID_ATTEST))
    p.add_argument("--execute", action="store_true", help="record the filing in the ledger")
    p.add_argument("--allow-no-receipt", action="store_true")
    p.set_defaults(func=cmd_file)

    p = sub.add_parser("poll", help="record a status read")
    p.add_argument("--target", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--note")
    p.add_argument("--evidence")
    p.add_argument("--exemption", help="statutory provision the target cited")
    p.set_defaults(func=cmd_poll)

    p = sub.add_parser("clock", help="statutory deadlines for open requests")
    p.add_argument("--as-of", help="YYYY-MM-DD")
    p.set_defaults(func=cmd_clock)

    p = sub.add_parser("verify", help="record a verification observation")
    p.add_argument("--target", required=True)
    p.add_argument("--probe", required=True)
    p.add_argument("--result", required=True, choices=sorted(VALID_RESULTS))
    p.add_argument("--independent", action="store_true", help="tier 3: observed outside the request path")
    p.add_argument("--evidence")
    p.add_argument("--note")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("identifiers", help="set or show the subject's identifiers")
    p.add_argument("--names", help="comma-separated legal name and aliases")
    p.add_argument("--dob", help="YYYY-MM-DD")
    p.add_argument("--zips", help="comma-separated ZIPs (current + prior)")
    p.add_argument("--emails", help="comma-separated")
    p.add_argument("--phones", help="comma-separated")
    p.add_argument("--maid", help="mobile advertising ID")
    p.add_argument("--ctv", help="connected TV advertising ID")
    p.add_argument("--vin", help="vehicle identification number")
    p.add_argument("--show", action="store_true", help="print masked values only")
    p.set_defaults(func=cmd_identifiers)

    p = sub.add_parser("preflight", help="check identifiers and targets before filing")
    p.set_defaults(func=cmd_preflight)

    p = sub.add_parser("report", help="markdown evidence pack")
    p.add_argument("--out")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("selftest", help="assert the date arithmetic")
    p.set_defaults(func=cmd_selftest)
    return parser


def main(argv=None) -> None:
    # --state is global but users type it after the subcommand; accept both.
    argv = list(sys.argv[1:] if argv is None else argv)
    state_path, cleaned, index = None, [], 0
    while index < len(argv):
        item = argv[index]
        if item == "--state":
            if index + 1 >= len(argv):
                raise SystemExit("--state needs a value")
            state_path, index = argv[index + 1], index + 2
            continue
        if item.startswith("--state="):
            state_path, index = item.split("=", 1)[1], index + 1
            continue
        cleaned.append(item)
        index += 1
    args = build_parser().parse_args(cleaned)
    if state_path:
        args.state = state_path
    args.func(args)


if __name__ == "__main__":
    main()
