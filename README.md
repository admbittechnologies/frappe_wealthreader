# Wealthreader Integration for ERPNext

A Frappe app that connects ERPNext to [Wealthreader](https://www.wealthreader.com/) for automatic bank transaction synchronization, similar to the built-in Plaid integration.

## Model

ADMBit holds the Wealthreader API contract and configures each client site once. The end client only sees a **Connect Bank Account** button and their list of linked banks.

## End-client experience

1. Open the **Bank Sync** workspace in ERPNext.
2. Click **Connect Bank Account**.
3. Select a company and bank name, then complete the Wealthreader widget flow.
4. Bank accounts and transactions are created automatically via the callback.
5. View and manage connections from **Bank Sync > Connections**.

## ADMBit setup (per client site)

1. Install the app on the client bench/site.
2. Open **Wealthreader Settings** (System Manager only).
3. Enable the integration and enter:
   - **API Key** from the Wealthreader clients area.
   - **Environment** (sandbox / production).
   - **Widget Domain** — defaults to the ERPNext site URL; update only if a custom domain is registered in Wealthreader.
   - **Allowed Connections** — connection limit for this client.
   - **Billing Expiry Date** — optional billing-period end date.
4. Copy the auto-generated **Callback URL** into the Wealthreader clients area.
5. Enable **Synchronize every hour** if desired.

## Billing

- Each active bank connection is billed at **€15 per month**.
- **Allowed Connections** in `Wealthreader Settings` controls the site limit.
- The **Connections** list shows the current active count and monthly cost.
- New connections are blocked when the limit is reached or the billing period has expired.

## Synchronization

- **Manual**: Click **Sync Now** on `Wealthreader Settings`.
- **Automatic**: Enable **Synchronize every hour** in `Wealthreader Settings`.
- Sync jobs iterate over active `Wealthreader Connection` records and refresh the linked bank accounts.

## Supported data

Currently ingests:
- Bank accounts (`accounts`)
- Credit/debit cards (`cards`)
- Account and card transactions

Other Wealthreader product types (loans, deposits, leases, portfolios, etc.) are ignored for the bank-transaction feed but remain available in the raw callback payload stored on `Wealthreader Link Session`.

## Security notes

- The callback endpoint is `allow_guest` because Wealthreader POSTs to it from their servers. It immediately switches to Administrator context, but **only processes payloads that match a pending `Wealthreader Link Session`** created from the ERPNext UI.
- The Wealthreader token is stored encrypted (Password field) on both the `Bank` DocType and the `Wealthreader Connection` DocType.
- `postMessage` events from the widget iframe are validated against the Wealthreader widget origin.
- If Wealthreader provides a webhook signature mechanism, add it to `callback()` in `wealthreader_settings.py` before production use.

## Amount sign convention

Wealthreader sample payloads use:
- **Negative amount** = payment/debit from the account → recorded as `withdrawal`.
- **Positive amount** = receipt/credit to the account → recorded as `deposit`.

This is the inverse of Plaid’s account-owner-centric convention. Verify against your live Wealthreader payloads before relying on the figures.

## Development / testing

Run the test suite inside a Frappe bench:

```bash
bench --site <site-name> run-tests --app wealthreader
```

## License

MIT
