# Copyright (c) 2026, ADMBit Technologies and contributors
# For license information, please see license.txt

import requests

import frappe
from frappe import _


class WealthreaderConnector:
	"""Thin wrapper around the Wealthreader REST API."""

	BASE_URLS = {
		"sandbox": "https://sandbox.wealthreader.com",
		"production": "https://api.wealthreader.com",
	}

	def __init__(self):
		self.settings = frappe.get_single("QuickBanks Settings")
		if not self.settings.environment:
			frappe.throw(_("Wealthreader Environment is not configured."))
		if self.settings.environment not in self.BASE_URLS:
			frappe.throw(_("Invalid Wealthreader Environment: {0}").format(self.settings.environment))

		self.base_url = self.BASE_URLS[self.settings.environment].rstrip("/")
		self.api_key = self.settings.get_password("api_key", raise_exception=False)
		if not self.api_key:
			frappe.throw(_("Wealthreader API Key is not configured. Run activation first."))

	def get_headers(self):
		return {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json",
			"Accept": "application/json",
		}

	def refresh(self, token, date_from=None, date_to=None, product_types=None):
		"""Call the Wealthreader refresh endpoint using a stored token.

		Args:
			token: The token returned in the callback payload statistics.token.
			date_from: ISO date string (YYYY-MM-DD) for incremental sync.
			date_to: ISO date string (YYYY-MM-DD) for incremental sync.
			product_types: Comma-separated product types.

		Returns:
			The normalized JSON payload on success.
		"""
		endpoint = self.settings.refresh_endpoint or "/api/v1/sync"
		url = f"{self.base_url}{endpoint}"
		payload = {"token": token}
		if date_from:
			payload["date_from"] = date_from
		if date_to:
			payload["date_to"] = date_to
		if product_types:
			payload["product_types"] = product_types

		try:
			response = requests.post(url, headers=self.get_headers(), json=payload, timeout=120)
			response.raise_for_status()
			try:
				return response.json()
			except ValueError as e:
				frappe.log_error(
					f"Wealthreader refresh returned non-JSON: {response.text[:500]} ({e})",
					_("Wealthreader Refresh Error"),
				)
				frappe.throw(_("Wealthreader returned an unexpected response."))
		except requests.exceptions.HTTPError as e:
			message = f"Wealthreader refresh HTTP error: {e.response.status_code} - {e.response.text[:500]}"
			frappe.log_error(message, _("Wealthreader Refresh Error"))
			frappe.throw(_("Failed to refresh data from Wealthreader."))
		except requests.exceptions.RequestException as e:
			frappe.log_error(f"Wealthreader refresh request error: {str(e)}", _("Wealthreader Refresh Error"))
			frappe.throw(_("Could not connect to Wealthreader."))

	def get_entities(self):
		"""Fetch the list of supported entities (banks)."""
		url = f"{self.base_url}/entities/"
		try:
			response = requests.get(url, headers=self.get_headers(), timeout=60)
			response.raise_for_status()
			try:
				return response.json()
			except ValueError as e:
				frappe.log_error(
					f"Wealthreader entities returned non-JSON: {response.text[:500]} ({e})",
					_("Wealthreader Entities Error"),
				)
				return []
		except requests.exceptions.RequestException as e:
			frappe.log_error(f"Wealthreader entities error: {str(e)}", _("Wealthreader Entities Error"))
			return []
