# Escalation paths and letter templates

Escalation is a filing, not a feeling. Go when you have: a receipt, a date, a statute, and an
observation. Without all four you are writing a diary entry to a regulator.

## 1. Routes, ranked by cost

| Route | Use when | Where |
|---|---|---|
| Cure letter to the target | clock at risk, no substantive reply | privacy@ or the DPO address in the policy |
| CalPrivacy complaint | CCPA/CPRA or Delete Act failure, CA subject | cppa.ca.gov complaints portal |
| California AG | broader consumer-protection pattern | oag.ca.gov/report |
| Other state AG | that state's statute | state AG consumer protection form |
| Supervisory authority (Art. 77) | EU/UK subject | any DPA, or the ICO for UK |
| DROP status dispute | broker reported a denial you believe is unlawful | CalPrivacy help / DROP support |

Reality check on outcomes: regulators triage by volume and evidence quality, not by outrage. A
single consumer complaint rarely produces a public action; it does produce a file that matters when
the same target accumulates complaints. Say that to a customer instead of promising enforcement.

## 2. What a complaint must contain

1. Subject identity and basis (self / §7063 authorization attached).
2. Target legal name, and the exact intake channel used, with URL.
3. Receipt number, timestamp, and identifier set submitted.
4. Deadline arithmetic: filed date, ack date, response date, days overdue.
5. What you did to verify, including the failed probe.
6. What the target said, verbatim. Especially any exemption.
7. The ask: investigation, and (for brokers) DROP compliance review.

Attach the evidence pack (`scripts/erasure.py report --out pack.md`), the receipt artifacts, and —
for brokers — the DROP ID and status history.

Do **not** write "you owe me $200/day". That fine is CalPrivacy's to assess. Claiming it as personal
damages marks you as unserious and, in a sales context, as misleading.

## 3. The cure period question

The CPRA removed the mandatory 30-day right-to-cure for administrative enforcement (2023). A cure
letter is therefore **evidence of good faith and a chance to fix it**, not a legal prerequisite.
Send one anyway: it is cheap, it dates your diligence, and it occasionally gets the data deleted.

---

## 4. Pre-complaint cure letter

> To: [privacy@target / DPO address]
> Subject: Deletion request [RECEIPT] — response overdue since [DATE]
>
> I submitted a request to delete my personal information under Cal. Civ. Code §1798.105 on
> [FILED DATE] through [CHANNEL], confirmation [RECEIPT]. Under §1798.130(a)(2) and 11 CCR §7021
> you were required to respond by [DUE DATE]. As of [TODAY] I have received no substantive response
> and no notice of an extension.
>
> My information as submitted: [IDENTIFIERS]. I verified on [DATE] that [OBSERVATION].
>
> Please either (a) confirm completion of the deletion, or (b) identify the specific exemption under
> §1798.105(d) you are relying on and the categories of information retained under it.
>
> If I have not heard from you by [DATE + 10 days], I will file a complaint with the California
> Privacy Protection Agency with the attached record. Nothing in this letter waives any right.
>
> [NAME] · [CONTACT] · [ATTACHMENTS]

## 5. Broker / DROP variant

Same skeleton, with these substitutions:

- Legal frame: Delete Act, Civ. Code §1798.99.86, plus the DROP request ID and the date each 45-day
  (or, from 2027, 30-day) cycle closed without a reported status.
- Attach the DROP status history (screenshots, dated) and the registry entry showing the broker is
  registered and therefore in scope.
- Ask specifically: was the denial reported to CalPrivacy, and under which provision?

## 6. GDPR variant

Reference Art. 12(3) (one month, +2 with notice), Art. 17(1) ground invoked, Art. 19 (recipients),
and state the intention to complain under Art. 77. Keep it shorter than the US version; EU
controllers respond to terse, cited letters.

## 7. Escalation ladder for the ledger

Mark a request escalated only when a filing exists (URL or email sent, with date). Track the
regulator's reference number in the request note. An "escalated" flag with no filing is worse than
no flag: it is the kind of claim that collapses under one question.
