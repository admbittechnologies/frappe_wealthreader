# Copyright (c) 2026, ADMBit Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
	make_custom_fields()


def make_custom_fields():
	custom_fields = {
		"Bank": [
			{
				"fieldname": "quickbanks_token",
				"label": "Wealthreader Token",
				"fieldtype": "Password",
				"hidden": 1,
				"insert_after": "website",
				"read_only": 1,
			},
		],
		"Bank Account": [
			{
				"fieldname": "quickbanks_source",
				"label": "Wealthreader Source",
				"fieldtype": "Select",
				"options": "\naccounts\ncards",
				"hidden": 1,
				"insert_after": "last_integration_date",
				"read_only": 1,
			},
		],
	}

	create_custom_fields(custom_fields, update=True)
