# Wealthreader Integration for ERPNext

A Frappe app that connects ERPNext to [Wealthreader](https://www.wealthreader.com/) for automatic bank transaction synchronization, similar to the built-in Plaid integration.

## Features

- Configure Wealthreader API credentials in a single **Wealthreader Settings** DocType.
- Launch the Wealthreader widget from ERPNext to link bank accounts.
- Receive normalized financial data via Wealthreader callback webhook.
- Automatically create/update ERPNext `Bank`, `Bank Account`, and `Bank Transaction` records.
- Manual and scheduled incremental synchronization.

## Installation

```bash
bench get-app https://github.com/admbittechnologies/frappe_wealthreader.git
bench --site <site-name> install-app wealthreader
```

## Setup

1. Open **Wealthreader Settings** in ERPNext.
2. Enable the integration and enter your API key and environment.
3. Register the displayed callback URL in the [Wealthreader clients area](https://www.wealthreader.com/clients/).
4. Add your ERPNext site domain as the allowed widget domain.
5. Click **Link a new bank account** and complete the widget flow.

## Synchronization

- **Manual**: Click **Sync Now** on `Wealthreader Settings` or use the action on a linked `Bank Account`.
- **Automatic**: Enable **Synchronize every hour** in `Wealthreader Settings`.

## Supported data

Currently ingests:
- Bank accounts (`accounts`)
- Credit/debit cards (`cards`)
- Account and card transactions

Other Wealthreader product types (loans, deposits, leases, portfolios, etc.) are ignored for the bank-transaction feed but remain available in the raw callback payload stored on `Wealthreader Link Session`.

## Security notes

- The callback endpoint is `allow_guest` because Wealthreader POSTs to it from their servers. It immediately switches to Administrator context, but **only processes payloads that match a pending `Wealthreader Link Session`** created from the ERPNext UI.
- The Wealthreader token is stored encrypted (Password field) on the `Bank` DocType.
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
