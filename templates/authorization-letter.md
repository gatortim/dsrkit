# Authorized agent permission (11 CCR §7063)

A business may require proof that the consumer gave the agent signed permission, and may require the
consumer to confirm the permission directly with the business. Keep this signed, dated, scoped, and
revocable. Do not bundle it into a terms-of-service click.

---

**AUTHORIZATION TO SUBMIT PRIVACY REQUESTS AS MY AGENT**

I, {{consumer_legal_name}}, residing at {{address}}, authorize {{agent_legal_name}}
("Agent") to act on my behalf to submit requests to {{target_or_all_businesses}} under the California
Consumer Privacy Act, including:

- ☐ Request to delete (Cal. Civ. Code §1798.105)
- ☐ Request to correct (§1798.106)
- ☐ Request to know / access (§1798.110, §1798.115)
- ☐ Request to opt out of sale or sharing (§1798.120)
- ☐ Delete Act / DROP deletion request (Civ. Code §1798.99.80 et seq.)

**Identifying information the Agent may submit on my behalf:**
{{identifier_list}}

The Agent may not submit any other information about me, may not act for anyone else under this
document, and may not use my information for any purpose other than making and tracking these
requests.

I understand that a business may contact me directly to confirm this authorization, and I agree to
confirm it when asked.

**Term:** this authorization begins {{start_date}} and remains in effect until I revoke it in writing.
I may revoke it at any time by emailing {{revocation_address}}; revocation takes effect when sent.

Signature: ______________________  Date: {{date}}

Printed name: {{consumer_legal_name}}

Contact for confirmation: {{consumer_email}} / {{consumer_phone}}

---

## Operator checklist

- [ ] Signed and dated by the consumer, not typed on their behalf
- [ ] Scope limited to named request types and named businesses (or explicitly "all")
- [ ] Identifier list attached and initialled
- [ ] Revocation channel stated and monitored
- [ ] Stored outside the repo, access-controlled, retained only as long as needed to defend the work
- [ ] Filed in the ledger as the `attest: authorization` basis, with the document hash recorded

If the target asks the consumer to confirm directly, that is normal and permitted. Route it to the
consumer; do not answer for them.
