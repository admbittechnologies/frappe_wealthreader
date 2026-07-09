# Wealthreader Integration for ERPNext

A Frappe app that connects ERPNext to [Wealthreader](https://www.wealthreader.com/) for automatic bank transaction synchronization, similar to the built-in Plaid integration.

## Features

- **Plug-and-play setup**: Configure Wealthreader API credentials once in `Wealthreader Settings`; end users only choose a company and bank name to start linking.
- **Per-connection licensing**: Each active bank connection is a billable unit (€15/month). Built-in connection counting and license enforcement.
- **Wealthreader widget flow**: Launch the official widget from ERPNext to link bank accounts.
- **Webhook callback**: Receive normalized financial data via Wealthreader callback and create/update ERPNext `Bank`, `Bank Account`, and `Bank Transaction` records.
- **Manual and scheduled incremental synchronization**.

## Installation

```bash
bench get-app https://github.com/admbittechnologies/frappe_wealthreader.git
bench --site <site-name> install-app wealthreader
```

## Setup

1. Open **Wealthreader Settings** in ERPNext.
2. Enable the integration and enter your API key and environment.
3. Set the **Allowed Connections** count and optional **License Key / Expiry Date**.
4. Register the displayed callback URL in the [Wealthreader clients area](https://www.wealthreader.com/clients/).
5. Add your ERPNext site domain as the allowed widget domain.
6. Click **Link Bank Account** and complete the widget flow.

## Licensing

- Each active bank connection is billed at **€15 per month**.
- The **Allowed Connections** field in `Wealthreader Settings` controls how many connections can be active.
- When the limit is reached or the license expires, new bank links and background syncs are blocked until the license is renewed.
- Connection status and history are tracked in `Wealthreader Connection`.

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
