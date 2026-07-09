# Wealthreader Integration for ERPNext

A Frappe app that connects ERPNext to [Wealthreader](https://www.wealthreader.com/) for automatic bank transaction synchronization, similar to the built-in Plaid integration.

## Model

ADMBit holds the Wealthreader API contract and provisions each client site once. The end client only sees a **Connect Bank Account** button and their list of linked banks. The Wealthreader API key is never exposed in the ERPNext UI.

## End-client experience

1. Open the **Bank Sync** workspace in ERPNext.
2. Click **Connect Bank Account**.
3. Select a company and bank name, then complete the Wealthreader widget flow.
4. Bank accounts and transactions are created automatically via the callback.
5. View and manage connections from **Bank Sync > Connections**.

## ADMBit setup (per client site)

The Wealthreader API key is provisioned outside the ERPNext UI so the client never sees it.

### 1. Set the API key

Use one of the following methods (in order of preference):

**Site config (recommended)**

```bash
bench --site <site-name> set-config wealthreader_api_key "<ADMBit API key>"
```

**Environment variable**

```bash
export WEALTHREADER_API_KEY="<ADMBit API key>"
```

### 2. Configure the integration

Open **Wealthreader Settings** (System Manager only) and set:

- **Environment** (sandbox / production)
- **Widget Domain** — defaults to the ERPNext site URL; update only if a custom domain is registered in Wealthreader
- **Allowed Connections** — connection limit for this client
- **Billing Expiry Date** — optional billing-period end date
- **Synchronize every hour** if desired

### 3. Register the callback URL

Copy the auto-generated **Callback URL** from `Wealthreader Settings` into the Wealthreader clients area.

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

- The API key is read from site config or an environment variable and is **never stored in an ERPNext DocType field**.
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
