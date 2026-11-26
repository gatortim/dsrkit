#!/usr/bin/env python3
"""enumerate.py - find a company's privacy-request intake, without a shared registry.

Why this exists: only California publishes a registry of deletion endpoints. Everywhere else
(Colorado included) there is no shared enumeration, so the intake channel has to be discovered
per company. This script does the mechanical part: probe the standard paths, fingerprint the DSR
vendor, pull the request links out of the policy, and emit ready-to-paste ledger targets.

Design rules:
  1. Public pages only. One GET per path, no forms, no auth, no cookies beyond what a redirect needs.
  2. Slow by default (1s between requests) and capped. This is a personal tool, not a crawler;
     bulk probing of third-party sites invites ToS and CFAA arguments.
  3. Absence is a finding. "No rights path found" is recorded, because the missing disclosure is
     itself the evidence.
  4. It never decides a target is compliant. It reports what the site said, with the URL and date.

stdlib only. Exit codes: 0 ok, 2 nothing found at all.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) privacy-harness/1.0 (+personal use)"

PROBE_PATHS = [
    "/privacy",
    "/privacy-policy",
    "/legal/privacy",
    "/legal/privacy-policy",
    "/privacy-notice",
    "/privacy/request",
    "/your-privacy-choices",
    "/do-not-sell",
    "/privacy-rights",
    "/data-privacy",
    "/legal/privacy-notice",
]

# DSR / consent vendor fingerprints. Heuristic: tells you what experience to expect and where the
# receipt will come from. It does NOT tell you who is legally responsible - the controller is.
VENDORS = {
    "onetrust": ["privacyportal.onetrust.com", "app.onetrust.com", "cdn.cookielaw.org", "optanon"],
    "transcend": ["transcend.io", "sombra.transcend.io", "dsar.transcend.io"],
    "ketch": ["ketch.com", "ketchcdn.com", "global.ketch"],
    "trustarc": ["trustarc.com", "consent.trustarc.com", "truste.com", "submit-irm.trustarc.com"],
    "datagrail": ["datagrail.io", "integration.datagrail.io"],
    "ethyca": ["ethyca.com", "privacy.ethyca.com", "fides"],
    "osano": ["osano.com"],
    "didomi": ["didomi.io"],
    "usercentrics": ["usercentrics"],
    "sourcepoint": ["sourcepoint"],
    "cookiebot": ["cookiebot"],
    "iubenda": ["iubenda"],
    "termly": ["termly"],
    "privacybot": ["privacybot"],
    "secureprivacy": ["secureprivacy"],
    "mineos": ["mineos"],
    "cassie": ["cassie.com"],
}

# Signals that the policy was actually updated for the state you live in. A policy that never says
# "Colorado" will usually still take the request, but it will argue about the clock.
SIGNALS = {
    "colorado": r"colorado|\bCPA\b|6-1-13",
    "ccpa": r"california|ccpa|cpra",
    "virginia": r"virginia|vcdpa",
    "connecticut": r"connecticut|ctdpa",
    "utah": r"utah|ucpa",
    "texas": r"texas|tdpsa",
    "gpc": r"global privacy control|\bGPC\b",
    "do_not_sell": r"do not sell|do not share",
    "opt_out": r"opt[- ]out",
    "delete": r"\bdelet(e|ion)\b",
    "appeal": r"\bappeal\b",
    "45_days": r"forty[- ]five \(?45\)?[- ]days?|45 days",
    "authorized_agent": r"authorized agent",
}

DSR_LINK = re.compile(
    r"https?://[^\s\"'<>]+|/(?:[^\s\"'<>]*)(?:privacy|dsar|do-not-sell|opt-out|data-request|rights)[^\s\"'<>]*",
    re.IGNORECASE,
)


def fetch(url: str, timeout: float, gpc: bool) -> tuple[int, str, str]:
    """Return (status, final_url, body). status 0 means it did not resolve."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    if gpc:
        req.add_header("Sec-GPC", "1")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(400_000).decode(resp.headers.get_content_charset() or "utf-8", "replace")
            return resp.status, resp.geturl(), body
    except urllib.error.HTTPError as exc:
        return exc.code, url, ""
    except Exception:
        return 0, url, ""


def probe_domain(domain: str, args) -> dict:
    base = domain if domain.startswith(("http://", "https://")) else f"https://{domain}"
    base = base.rstrip("/")
    record = {
        "domain": urllib.parse.urlparse(base).netloc or domain,
        "base": base,
        "checked_on": date.today().isoformat(),
        "probes": [],
        "policy_url": None,
        "vendors": [],
        "dsr_links": [],
        "signals": {},
        "note": "",
    }
    bodies = []
    hits = 0
    for path in PROBE_PATHS:
        status, final, body = fetch(base + path, args.timeout, args.gpc)
        record["probes"].append({"path": path, "status": status, "final": final})
        if status == 200 and body:
            hits += 1
            bodies.append(body)
            if not record["policy_url"]:
                record["policy_url"] = final
            if hits >= 2:
                break
        if args.delay:
            time.sleep(args.delay)

    if not bodies:
        best = next((p for p in record["probes"] if p["status"] not in (0, 404)), None)
        record["note"] = (
            f"no readable policy page; best probe: {best['path']} -> {best['status']}" if best
            else "no response from any policy path"
        )
        return record

    blob = "\n".join(bodies).lower()
    record["vendors"] = sorted({name for name, needles in VENDORS.items()
                                if any(n in blob for n in needles)})
    record["signals"] = {name: bool(re.search(rx, blob, re.IGNORECASE)) for name, rx in SIGNALS.items()}

    links = []
    for body in bodies:
        for raw in DSR_LINK.findall(body):
            if raw.lower().endswith((".png", ".jpg", ".svg", ".css", ".js", ".webp")):
                continue
            if "privacy" not in raw.lower() and not any(k in raw.lower() for k in
                                                       ("dsar", "do-not-sell", "opt-out",
                                                        "data-request", "rights")):
                continue
            url = urllib.parse.urljoin(base + "/", html.unescape(raw))
            parsed = urllib.parse.urlparse(url)
            if parsed.netloc and record["domain"] not in url:
                continue  # third-party host: fingerprint only, not a submission endpoint
            if parsed.path in ("", "/") or url.rstrip("/") == base.rstrip("/"):
                continue  # link resolves to the homepage: not an intake channel
            if url not in links:
                links.append(url)
    # Prefer an actual request form over a policy page: the policy explains the right, the form
    # exercises it, and only the form produces a receipt.
    def link_score(url: str) -> int:
        u = url.lower()
        score = 0
        for key, weight in (("dsar", 5), ("data-request", 5), ("request", 4), ("rights", 4),
                            ("do-not-sell", 4), ("opt-out", 3), ("privacy", 1)):
            if key in u:
                score += weight
        return -score

    links.sort(key=link_score)
    record["dsr_links"] = [_strip_tracking(u) for u in links[:8]]
    record["dsr_links"] = list(dict.fromkeys(record["dsr_links"]))
    return record


TRACKING_PARAMS = ("utm_", "__hs", "gclid", "fbclid", "msclkid", "mc_cid", "mc_eid", "_ga", "igshid")


def _strip_tracking(url: str) -> str:
    """Drop analytics junk from a pasted portal URL; the ledger should hold the endpoint, not a tag."""
    parts = urllib.parse.urlsplit(url)
    if not parts.query:
        return url
    kept = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
            if not any(k.lower().startswith(p) or k.lower() == p for p in TRACKING_PARAMS)]
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(kept)))


def grade(record: dict) -> str:
    """Rank the record for triage. Not a compliance score - a 'will this filing go anywhere' hint."""
    if not record["policy_url"]:
        return "NO-POLICY"
    if record["dsr_links"] or record["vendors"]:
        return "STRONG"
    if record["signals"].get("delete") or record["signals"].get("do_not_sell"):
        return "WEAK"
    return "NO-RIGHTS"


def target_command(record: dict) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", record["domain"].lower()).strip("-")
    notes = (f"enumerated {record['checked_on']}; "
             f"vendors={','.join(record['vendors']) or 'none'}; "
             f"colorado={record['signals'].get('colorado')}")
    portal = record["dsr_links"][0] if record["dsr_links"] else ""
    if not portal:
        notes += "; NO INTAKE FOUND - use phone/mail or a browser"
        return (f"python3 scripts/erasure.py targets add --id {slug} "
                f"--name \"{record['domain']}\" --class controller --notes \"{notes}\""
                f"   # then: file by mail/phone, or re-probe in a browser")
    return (f"python3 scripts/erasure.py targets add --id {slug} "
            f"--name \"{record['domain']}\" --class controller "
            f"--portal \"{portal}\" --notes \"{notes}\"")


def main() -> int:
    ap = argparse.ArgumentParser(description="Discover privacy-request intake for a list of domains.")
    ap.add_argument("domains", nargs="*", help="domains, e.g. spokeo.com whitepages.com")
    ap.add_argument("--input", help="file with one domain per line (# comments allowed)")
    ap.add_argument("--out", default="enumerated.json", help="JSON output path")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between requests (default 1.0)")
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--limit", type=int, default=60, help="max domains per run")
    ap.add_argument("--gpc", action="store_true", help="send Sec-GPC: 1 on every probe")
    ap.add_argument("--commands", action="store_true", help="only print paste-ready targets add lines")
    args = ap.parse_args()

    domains = list(args.domains)
    if args.input:
        with open(args.input, encoding="utf-8") as fh:
            domains += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    seen, ordered = set(), []
    for d in domains:
        key = d.lower().removeprefix("https://").removeprefix("http://").strip("/")
        if key and key not in seen:
            seen.add(key)
            ordered.append(d)
    ordered = ordered[: args.limit]
    if not ordered:
        ap.error("no domains given (pass domains or --input FILE)")

    records = []
    for dom in ordered:
        rec = probe_domain(dom, args)
        rec["grade"] = grade(rec)
        records.append(rec)
        if not args.commands:
            sig = ",".join(k for k, v in rec["signals"].items() if v) or "-"
            print(f"{rec['domain']:<34} {rec['grade']:<10} vendors={','.join(rec['vendors']) or '-':<22} {sig}")
            sys.stdout.flush()
        if args.delay:
            time.sleep(args.delay)

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump({"generated": date.today().isoformat(), "gpc": args.gpc, "records": records}, fh, indent=2)

    if args.commands:
        for rec in records:
            print(target_command(rec))
    else:
        strong = sum(1 for r in records if r["grade"] == "STRONG")
        print(f"\n{len(records)} domains, {strong} with a named intake, 0 judged compliant.")
        print(f"details: {args.out}")
        print("paste-ready targets:\n")
        for rec in records:
            print("  " + target_command(rec))
    return 0 if any(r["policy_url"] for r in records) else 2


if __name__ == "__main__":
    raise SystemExit(main())
