# The model layer: optional, and deliberately not implemented

A privacy tool that ships your name, date of birth, and ZIP to an inference API is self-defeating.
So the question is not "can a local model help" — it is "which four percent of this job is prose,
and is a small model good enough at that four percent".

## 1. What is arithmetic, and needs no model at all

| Job | Why a model must not touch it |
|---|---|
| Deadline arithmetic (45 + 45, business days, DROP cycle by year) | A model that is 99% right about a date is a model that loses a complaint. `add_business_days()` is exact and testable. |
| Status normalization (`Deleted` / `Exempted` / `Opted-out` / `Record not found`) | These are a closed vocabulary with legal meaning. Map them in code. |
| Whether a response satisfies the request | This is a judgement with a statutory test behind it. A model will happily call a Tier 1 receipt a deletion. |
| Whether to escalate | Same. Overdue + recorded poll + no substantive response. Deterministic. |

That is most of the harness, and it is why `erasure.py` has **zero** model dependency and **zero**
network calls. Keep it that way.

## 2. Where prose genuinely appears

| Job | Worth a local model? | Why |
|---|---|---|
| Policy page → "how do I submit a deletion request" (method, URL or email, required fields) | **Yes** | Policies are prose, and the regex path in `enumerate.py` misses phrasings. This is extraction, not judgement. |
| Policy page → which states are named, what verification is demanded | Maybe | The signal flags in `enumerate.py` already catch state names cheaply. A model adds nuance about verification. |
| Drafting the request body for one target | Marginally | `templates/request-email.md` plus slot-fill is more reliable and more auditable. |
| Drafting an appeal or a regulator complaint | **Yes** | Genuinely generative, low frequency, and a human reviews it before it is sent. |
| Classifying an incoming response ("we need more ID" / "denied under exemption" / "done") | **Yes** | Short text, closed label set, high volume with a long tail of broker phrasing. |

## 3. The guard that makes a small model safe

The failure mode that matters is not a clumsy sentence — it is an invented endpoint or an invented
email address, which produces a request that goes nowhere and a clock that never starts.

So the model never gets to assert. It proposes, and the script verifies:

```json
{
  "method": "portal",
  "url": "https://acme.example/privacy/request",
  "email": null,
  "required_fields": ["name", "email", "state"],
  "quote": "To submit a deletion request, use our privacy request form at acme.example/privacy/request."
}
```

Accept the object **only if** `quote` is a verbatim substring of the page body that was fetched
(after whitespace normalization). If the quote is not found, discard the proposal and fall back to
the regex path. This costs three lines and turns "hallucination" into "no output", which is a
failure mode the ledger already knows how to record.

Two more cheap rules:

- **Constrain the decode.** Use grammar/JSON-schema-constrained sampling (llama.cpp grammars,
  `outlines`, or an Ollama `format:` schema) so the shape is valid by construction and you are not
  parsing apologies.
- **Quote-before-cite.** The same guard applies to statute cites: the state string must come from
  `references/legal-clock.md`, not from the model's memory. Models misremember section numbers
  confidently, and a wrong cite is worse than no cite.

## 4. Model size, honestly

| Task | Floor that works |
|---|---|
| JSON-shaped extraction with a quote guard | ~7-8B instruct, Q4, 8 GB VRAM; a 4B class model works for classification but drops fields |
| Response classification into 4 labels | 4B, with the quote guard and a temperature of 0 |
| Appeal / complaint drafting | 14B+ before the prose is worth editing; below that you rewrite it anyway |

A 4B model is useful here, but as a **classifier and extractor under guard**, not as the thing that
decides what to file. The distinction is the whole design.

## 5. Interface, when someone implements it

Keep it out of the critical path:

```bash
# opt-in, off by default, never required for the core loop
python3 scripts/enumerate.py --input domains.txt --explain --endpoint http://localhost:11434
```

- `--explain` runs the extraction on policy pages where the regex path graded `WEAK`.
- Endpoint is a local base URL only; refuse anything that is not loopback unless the user passes
  `--i-understand-this-sends-my-policy-text-offbox`.
- Every accepted proposal records the model name and the verbatim quote in the ledger note, so a
  later reader can see exactly why the endpoint was chosen.

## 6. Status

Not implemented, on purpose. No model runtime was available to test against in the session that
wrote this file, and shipping an untested inference path into a tool whose entire value is
"trustworthy evidence" is the wrong trade. The seam is described above; the guard is the part worth
copying into any implementation.
