# Copyright (c) 2026, ADMBit Technologies and Contributors
# See license.txt

import json
import unittest

import frappe
from frappe.utils.response import json_handler

from wealthreader.wealthreader.doctype.wealthreader_settings.wealthreader_settings import (
	add_bank_accounts,
	get_widget_config,
	new_bank_transaction,
)


class TestWealthreaderSettings(unittest.TestCase):
	def test_wealthreader_disabled(self):
		frappe.db.set_single_value("Wealthreader Settings", "enabled", 0)
		self.assertEqual(get_widget_config(), {"status": "disabled"})

	def test_new_transaction_with_negative_amount(self):
		# Wealthreader convention: negative amount = withdrawal/debit
		if not frappe.db.exists("Bank", "Test Wealthreader Bank"):
			frappe.get_doc({"doctype": "Bank", "bank_name": "Test Wealthreader Bank"}).insert()

		company = "_Test Company"
		if not frappe.db.exists("Company", company):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": company,
					"default_currency": "EUR",
					"country": "Spain",
				}
			).insert()

		payload = {
			"accounts": [
				{
					"uuid": "wr-account-001",
					"name": "Test Checking",
					"subtype": "checking",
					"code": "ES4914651234561234567890",
					"currency": "EUR",
					"transactions": [],
				}
			]
		}

		bank = json.dumps(
			frappe.get_doc("Bank", "Test Wealthreader Bank").as_dict(), default=json_handler
		)
		add_bank_accounts(payload, bank, company)

		transaction = {
			"uuid": "wr-txn-001",
			"operation_date": "2024-01-15",
			"value_date": "2024-01-15",
			"amount": -25.5,
			"currency": "EUR",
			"description": "Payment to vendor",
		}

		new_bank_transaction(transaction, "wr-account-001", "accounts")

		bank_transactions = frappe.get_all("Bank Transaction", fields=["deposit", "withdrawal"])
		self.assertEqual(len(bank_transactions), 1)
		self.assertEqual(bank_transactions[0].deposit, 0.0)
		self.assertEqual(bank_transactions[0].withdrawal, 25.5)
