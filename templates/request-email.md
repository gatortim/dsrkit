# Deletion request email

Use when a target has no working webform, or when you want a dated paper trail independent of a
portal. Send from an address you control and keep the sent copy.

---

**To:** {{privacy_email}}
**Cc:** {{dpo_or_legal_email}}
**Subject:** Request to delete personal information — {{subject_legal_name}}

To the Privacy Office:

I am requesting the deletion of my personal information under {{legal_basis}}. Please treat this email
as a verifiable consumer request to delete.

Use the cites your ledger printed for your own state — do not copy California's into a filing
elsewhere:

- California: `the California Consumer Privacy Act, Cal. Civ. Code §1798.105`
- Colorado: `the Colorado Privacy Act, C.R.S. §6-1-1306(1), and the 45-day response period in §6-1-1306(2)(a)`

A filing that cites the wrong state's statute is a filing the recipient can set aside, and it tells
them you copied a template.

**Identifying information**, so you can locate my records:

- Name: {{legal_name}} (also known as: {{aliases}})
- Date of birth: {{dob}}
- ZIP: {{zip}}
- Email(s): {{emails}}
- Phone(s): {{phones}}
- Account / customer ID, if any: {{account_id}}

The request covers all personal information you collected about me, including information held by
your service providers and contractors, and information you have sold or shared with third parties.
Please direct those parties to delete it as well, as §1798.105(c) requires.

Please confirm receipt within 10 business days and complete the deletion within 45 calendar days,
as required by §1798.130(a)(2) and 11 CCR §7021. If you need an extension, please tell me within the
first 45 days and state the reason.

If you decline any part of this request, please identify the specific provision of §1798.105(d) you
are relying on and the categories of information you are retaining under it.

Please send confirmation of completion, including the date of deletion and any categories retained,
to this address.

Sincerely,
{{name}}
{{contact_block}}

---

## Notes for the operator

- Send one email per target. CC'ing five privacy offices in one thread gives each of them a reason to
  say "we thought someone else handled it".
- Put the receipt (message ID + timestamp) straight into the ledger:
  `file --target <id> --method email --execute --attest self --receipt <message-id>`
- If the target replies with a portal link, use the portal **and keep the email thread** — the email
  is your proof the request existed before the portal did.
- Do not attach an ID document in the first message. Offer it only if they ask, and only through
  their secure channel. A privacy request should not become an identity-theft kit in someone's inbox.
