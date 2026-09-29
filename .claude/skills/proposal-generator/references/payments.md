# Payments

Checked 2026-09-25. Fees and availability change, so re-check before quoting a fee to a client.

## Why not Stripe (yet)

Stripe does not onboard businesses registered in Pakistan. The route in is a US company:
Stripe Atlas takes Pakistani founders ($500 to incorporate), plus roughly $300-400 a year in
Delaware fees and registered agent, plus an annual Form 5472 filing for a foreign-owned LLC, where
a missed filing carries a $25,000 penalty. That overhead makes sense once direct retainers are
recurring and auto-billing matters. Before the first direct client it does not.

**The drop-in later:** a Stripe Payment Link goes in the same `pay_url` field. `buy.stripe.com`
and `checkout.stripe.com` are already on the renderer's allowlist, so nothing else changes.

## Payoneer now

Payoneer works with a Pakistani CNIC. The client pays by card, US bank debit (ACH), bank transfer
or their own Payoneer balance. Fees as reported in 2026 sources: card about 3-4 percent, ACH about
1 percent. For large one-time invoices, ACH or wire is the cheaper ask.

Two ways it plugs into the page, and the page handles both per option:

| Mode | Set up | What the client sees after signing |
|---|---|---|
| **Pay link ready** (`pay_url` set) | Before deploying, create a fixed-amount Payoneer payment link or payment request for that option's *amount due to start* (not the full price), and paste its URL into `pay_url` | "Continue to secure payment" button, opens Payoneer in a new tab |
| **Invoice after signing** (`pay_url` empty) | Nothing up front | "Your secure payment link from Payoneer arrives at <email> within one business day." The alert email tells Aleem to send the request |

**Check which one the account has.** Payoneer's reusable "Payment Link" may not be available in
every country. "Request a payment" is: it emails the client a link, and the link can also be
copied. Creating a request per option before the client chooses would email them several
requests, so when only "Request a payment" exists, use invoice-after-signing.

**Amount due, not full price.** The page and the alert email both state the amount due to start
(the deposit, or the first month for monthly options). The request must match it.

**Retainers:** Payoneer requests are one-off, so a monthly option means a new request each month
until Stripe is in place. Say so in `terms` if the client asks about auto-billing.

## Upwork boundary

Clients found through Upwork pay through Upwork. Sending one to Payoneer or Stripe within 24 months
of meeting on Upwork breaks Upwork's terms of service and risks the account. This skill is for
direct clients from cold email, LinkedIn, Instagram, referrals and the website.

## Sources

- [Stripe Atlas](https://stripe.com/atlas)
- [Stripe Atlas vs US LLC for Pakistani founders, 2026](https://www.xpezia.com.pk/blog/stripe-atlas-vs-us-llc-pakistan/)
- [Payoneer: Request a payment, information for receivers](https://payoneer.custhelp.com/app/answers/detail/a_id/12280/~/request-a-payment---information-for-receivers)
- [Payoneer: Payment Link](https://www.payoneer.com/payment-links/)
- [Payoneer review for Pakistan, WorldFirst, 2026](https://www.worldfirst.com/sasia/blog/business-banking-insights/payoneer-review/)

**Not in sources:** the $25,000 Form 5472 penalty and the Delaware cost range come from general
knowledge of US tax filing for foreign-owned LLCs, not from the pages above. Confirm with an
accountant before forming the company.
