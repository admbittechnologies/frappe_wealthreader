# Copyright (c) 2026, ADMBit Technologies and contributors
# For license information, please see license.txt

import uuid

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, cint, flt, formatdate, getdate, now, today

import os

import requests

from quickbanks.quickbanks.doctype.quickbanks_settings.quickbanks_connector import (
	WealthreaderConnector,
)


class QuickBanksSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		activation_key: DF.Data | None
		activation_status: DF.SmallText | None
		allowed_connections: DF.Int
		api_key: DF.Password | None
		automatic_sync: DF.Check
		callback_url: DF.Data | None
		default_product_types: DF.Data | None
		enabled: DF.Check
		environment: DF.Literal["", "sandbox", "production"]
		hub_url: DF.Data | None
		license_expiry_date: DF.Date | None
		refresh_endpoint: DF.Data | None
		sync_start_date: DF.Date | None
		widget_domain: DF.Data | None
	# end: auto-generated types

	def validate(self):
		# Try to exchange the activation key for credentials before validating.
		if self.enabled and self.hub_url and self.activation_key and not self.get_password("api_key"):
			self.run_activation()

		if self.enabled:
			if not self.environment:
				frappe.throw(_("Environment is required when QuickBanks is enabled."))
			if not self.get_password("api_key"):
				frappe.throw(
					_(
						"Wealthreader API key is not configured. Please run activation or ask ADMBit to provision it."
					)
				)
			if cint(self.allowed_connections) < 0:
				frappe.throw(_("Allowed Connections cannot be negative."))

		self.callback_url = self.get_callback_url()

	def get_callback_url(self):
		return frappe.utils.get_url(
			"/api/method/quickbanks.quickbanks.doctype.quickbanks_settings.quickbanks_settings.callback"
		)

	def run_activation(self):
		"""Call the ADMBit Hub to exchange the activation key for API credentials."""
		url = self.hub_url.rstrip("/") + "/api/method/wealthreader_hub.wealthreader_hub.api.activate"
		payload = {
			"activation_key": self.activation_key,
			"site_url": frappe.utils.get_url(),
			"site_name": frappe.local.site,
		}

		try:
			response = requests.post(url, json=payload, timeout=30)
			response.raise_for_status()
			result = response.json()
		except Exception as e:
			self.activation_status = f"Activation failed: {str(e)}"
			frappe.log_error("QuickBanks activation error", _("QuickBanks Activation"))
			return

		if result.get("status") != "ok" or not result.get("data"):
			self.activation_status = f"Activation failed: {result.get('message', 'Unknown error')}"
			return

		data = result["data"]
		self.api_key = data.get("api_key")
		self.environment = data.get("environment")
		self.widget_domain = data.get("widget_domain") or frappe.utils.get_url()
		self.allowed_connections = cint(data.get("allowed_connections"))
		if data.get("expiry_date"):
			self.license_expiry_date = getdate(data["expiry_date"])
		self.activation_status = "Activated successfully."

		# Try to register this site's domain and callback with Wealthreader via the Hub.
		self.register_domain_with_hub()

	def register_domain_with_hub(self):
		"""Ask the ADMBit Hub to authorize this site's domain and callback URL with Wealthreader."""
		if not self.hub_url:
			return

		url = self.hub_url.rstrip("/") + "/api/method/wealthreader_hub.wealthreader_hub.api.register_domain"
		payload = {
			"activation_key": self.activation_key,
			"site_url": frappe.utils.get_url(),
			"site_name": frappe.local.site,
			"callback_url": self.get_callback_url(),
		}

		try:
			response = requests.post(url, json=payload, timeout=30)
			response.raise_for_status()
			result = response.json()
			if result.get("status") != "ok":
				message = f"Domain registration failed: {result.get('message', 'Unknown error')}"
				self.activation_status += f"\n{message}"
				frappe.log_error(message, _("QuickBanks Domain Registration"))
			else:
				self.activation_status += "\nDomain and callback registered with Wealthreader."
		except Exception as e:
			message = f"Could not register domain/callback with Wealthreader Hub: {str(e)}"
			self.activation_status += f"\n{message}"
			frappe.log_error(message, _("QuickBanks Domain Registration"))

	@frappe.whitelist()
	def report_usage_to_hub(self):
		"""Send today's active connection count to the ADMBit Hub."""
		if not self.hub_url or not self.activation_key:
			return

		active = self.get_active_connections_count()
		payload = {
			"activation_key": self.activation_key,
			"report_date": str(today()),
			"active_connections": active,
			"site_url": frappe.utils.get_url(),
		}

		url = self.hub_url.rstrip("/") + "/api/method/wealthreader_hub.wealthreader_hub.api.report_usage"
		try:
			response = requests.post(url, json=payload, timeout=30)
			response.raise_for_status()
			return response.json()
		except Exception as e:
			frappe.log_error(f"QuickBanks usage report failed: {str(e)}", _("QuickBanks Usage Report"))

	def get_active_connections_count(self):
		return frappe.db.count("QuickBanks Connection", {"status": "Active"})

	def is_license_valid(self):
		if not self.enabled:
			return False, _("QuickBanks integration is disabled.")

		if not self.get_password("api_key"):
			return False, _(
				"QuickBanks is not activated. Please enter the activation key provided by ADMBit."
			)

		if self.license_expiry_date and getdate(self.license_expiry_date) < today():
			return False, _(
				"Your QuickBanks license expired on {0}. Please renew it to continue."
			).format(formatdate(self.license_expiry_date))

		return True, ""

	def can_add_connection(self):
		valid, message = self.is_license_valid()
		if not valid:
			return valid, message

		allowed = cint(self.allowed_connections)
		if allowed <= 0:
			return False, _(
				"No connections are allowed under the current license. Contact your administrator."
			)

		active = self.get_active_connections_count()
		if active >= allowed:
			return False, _(
				"Connection limit reached ({0}/{1}). Add more connections at €15/month each."
			).format(active, allowed)

		return True, ""



@frappe.whitelist()
def get_widget_config():
	settings = frappe.get_single("QuickBanks Settings")
	if not settings.enabled:
		return {"status": "disabled"}

	allowed, message = settings.can_add_connection()
	if not allowed:
		return {"status": "limit_reached", "message": message}

	date_from = None
	if settings.sync_start_date:
		date_from = formatdate(settings.sync_start_date, "YYYY-MM-dd")

	widget_domain = settings.widget_domain or frappe.utils.get_url()

	return {
		"operation_id": str(uuid.uuid4()),
		"widget_domain": widget_domain,
		"default_product_types": settings.default_product_types or "accounts,cards",
		"environment": settings.environment,
		"date_from": date_from,
	}


@frappe.whitelist()
def get_license_summary():
	settings = frappe.get_single("QuickBanks Settings")
	active = settings.get_active_connections_count()
	allowed = cint(settings.allowed_connections)

	status = "Active"
	if not settings.enabled:
		status = "Disabled"
	elif not settings.get_password("api_key"):
		status = "Not Activated"
	elif settings.license_expiry_date and getdate(settings.license_expiry_date) < today():
		status = "Expired"
	elif allowed <= 0:
		status = "No License"
	elif active >= allowed:
		status = "Limit Reached"

	can_add, message = settings.can_add_connection()

	return {
		"active_connections": active,
		"allowed_connections": allowed,
		"license_status": status,
		"expiry_date": formatdate(settings.license_expiry_date) if settings.license_expiry_date else None,
		"can_add_connection": can_add,
		"message": message,
	}


@frappe.whitelist(methods=["POST"])
def create_link_session(operation_id: str, company: str, bank_name: str):
	"""Create a Link Session before opening the widget so the callback can map operation_id."""
	if not operation_id or not company or not bank_name:
		frappe.throw(_("operation_id, company and bank_name are required"))

	settings = frappe.get_single("QuickBanks Settings")
	allowed, message = settings.can_add_connection()
	if not allowed:
		frappe.throw(message)

	session = frappe.get_doc(
		{
			"doctype": "QuickBanks Link Session",
			"operation_id": operation_id,
			"company": company,
			"bank_name": bank_name,
			"status": "Pending",
		}
	)
	session.insert(ignore_permissions=True)
	return session.name


@frappe.whitelist(allow_guest=True, methods=["POST"])
def callback():
	"""Webhook endpoint receiving Wealthreader callback payloads.

	Runs the whole handler as Administrator because it is an unauthenticated
	server-to-server webhook that must create core ERPNext documents.

	Security notes:
	- Only payloads with a matching pending `QuickBanks Link Session` are accepted.
	- If Wealthreader supports webhook signatures, add verification here before
	  the session lookup.
	"""
	original_user = frappe.session.user
	frappe.set_user("Administrator")
	try:
		return _callback_handler()
	finally:
		frappe.set_user(original_user)


def _callback_handler():
	try:
		data = frappe.parse_json(frappe.request.get_data(as_text=True))
	except Exception:
		frappe.log_error("Wealthreader callback body could not be parsed", _("Wealthreader Callback"))
		return _callback_response()

	if not isinstance(data, dict):
		frappe.log_error("Wealthreader callback body is not a JSON object", _("Wealthreader Callback"))
		return _callback_response()

	settings = frappe.get_single("QuickBanks Settings")
	if not settings.enabled:
		frappe.log_error("Wealthreader callback received while integration is disabled")
		return _callback_response()

	operation_id = data.get("operation_id") or data.get("operationId")
	if not operation_id:
		frappe.log_error("Wealthreader callback missing operation_id", _("Wealthreader Callback"))
		return _callback_response()

	session = _get_link_session(operation_id)
	if not session:
		frappe.log_error(
			f"Wealthreader callback received for unknown operation_id: {operation_id}",
			_("Wealthreader Callback"),
		)
		return _callback_response()

	if session.status == "Completed":
		# Already processed; acknowledge to avoid retries creating duplicate work.
		return _callback_response()

	session.db_set({"payload": frappe.as_json(data)})

	try:
		process_callback(data, session)
		session.db_set({"status": "Completed", "message": "Processed successfully"})
		return _callback_response()
	except Exception:
		frappe.log_error(frappe.get_traceback(), _("Wealthreader Callback Processing Error"))
		session.db_set({"status": "Failed", "message": frappe.get_traceback()[:400]})
		return _callback_response()


def _callback_response():
	# Wealthreader expects HTTP 200 even when we fail; errors are logged locally.
	frappe.response["http_status_code"] = 200
	return {"status": "ok"}


def _get_link_session(operation_id):
	if not operation_id:
		return None
	sessions = frappe.get_all(
		"QuickBanks Link Session",
		filters={"operation_id": operation_id},
		fields=["name", "company", "bank_name", "status"],
		limit=1,
		order_by="creation desc",
	)
	if sessions:
		return frappe.get_doc("QuickBanks Link Session", sessions[0].name)
	return None


def process_callback(payload, session):
	"""Ingest a Wealthreader callback payload.

	Expected top-level keys: operation_id, payload, statistics.
	Wealthreader may wrap the normalized data under a 'payload' key.
	"""
	_statistics = payload.get("statistics", {})
	data = payload.get("payload") if "payload" in payload else payload

	if not isinstance(data, dict):
		frappe.throw(_("Invalid Wealthreader callback payload"))

	statistics = _statistics if isinstance(_statistics, dict) else {}
	token = statistics.get("token")
	if not token:
		frappe.throw(_("Wealthreader callback missing statistics.token"))

	bank_name = session.bank_name
	company = session.company
	if not company:
		frappe.throw(_("Could not determine Company for Wealthreader callback."))

	bank = add_or_update_bank(bank_name, token)
	add_or_update_connection(bank_name, company, token)
	add_bank_accounts(data, bank, company)
	frappe.db.commit()


@frappe.whitelist(methods=["POST"])
def add_institution(bank_name: str, token: str | None = None):
	"""Create or update the Bank record for a linked institution."""
	return add_or_update_bank(bank_name, token)


def add_or_update_bank(bank_name, token=None):
	frappe.db.savepoint("wr_bank")
	try:
		if not frappe.db.exists("Bank", bank_name):
			bank = frappe.get_doc({"doctype": "Bank", "bank_name": bank_name})
			if token:
				bank.quickbanks_token = token
			bank.insert()
		else:
			bank = frappe.get_doc("Bank", bank_name)
			if token:
				bank.quickbanks_token = token
				bank.save()
		return bank
	except Exception:
		frappe.db.rollback(save_point="wr_bank")
		frappe.log_error("Wealthreader Bank creation error")
		frappe.throw(
			_(
				"There was an error creating or updating Bank {0} while linking with Wealthreader."
			).format(bank_name),
			title=_("QuickBanks Link Failed"),
		)


def add_or_update_connection(bank_name, company, token):
	"""Create or update the QuickBanks Connection for a linked institution."""
	frappe.db.savepoint("wr_connection")
	try:
		existing = frappe.db.exists(
			"QuickBanks Connection", {"bank": bank_name, "company": company}
		)
		if existing:
			conn = frappe.get_doc("QuickBanks Connection", existing)
			conn.token = token
			conn.status = "Active"
			conn.license_status = _get_connection_license_status()
			conn.last_sync = now()
		else:
			conn = frappe.get_doc(
				{
					"doctype": "QuickBanks Connection",
					"bank": bank_name,
					"company": company,
					"token": token,
					"status": "Active",
					"license_status": _get_connection_license_status(),
					"linked_date": today(),
					"last_sync": now(),
				}
			)
		conn.save(ignore_permissions=True)
		return conn
	except Exception:
		frappe.db.rollback(save_point="wr_connection")
		frappe.log_error("QuickBanks Connection creation error")
		raise


def _get_connection_license_status():
	settings = frappe.get_single("QuickBanks Settings")
	if settings.license_expiry_date and getdate(settings.license_expiry_date) < today():
		return "Expired"
	return "Licensed"


@frappe.whitelist(methods=["POST"])
def add_bank_accounts(response: str | dict, bank, company: str):
	"""Create or update ERPNext Bank Accounts and Bank Transactions from Wealthreader payload."""
	if isinstance(response, str):
		response = frappe.parse_json(response)

	# Normalize bank to a dict-like object
	if isinstance(bank, str):
		bank = frappe.parse_json(bank)
	elif hasattr(bank, "bank_name"):
		bank = bank.as_dict()

	bank_name = bank.get("bank_name")

	parent_gl_account = frappe.db.get_all(
		"Account",
		{"company": company, "account_type": "Bank", "is_group": 1, "disabled": 0},
	)
	if not parent_gl_account:
		frappe.throw(
			_(
				"Please setup and enable a group account with the Account Type - {0} for the company {1}"
			).format(frappe.bold(_("Bank")), company)
		)

	processed_accounts = []

	# Ingest depository accounts
	for account in response.get("accounts", []):
		processed_accounts.append(
			_upsert_bank_account(
				account=account,
				bank_name=bank_name,
				company=company,
				parent_gl_account=parent_gl_account[0].name,
				source="accounts",
				is_credit_card=0,
			)
		)

	# Ingest cards as bank accounts
	for card in response.get("cards", []):
		processed_accounts.append(
			_upsert_bank_account(
				account=card,
				bank_name=bank_name,
				company=company,
				parent_gl_account=parent_gl_account[0].name,
				source="cards",
				is_credit_card=1,
			)
		)

	# Create transactions for accounts and cards
	for account in response.get("accounts", []):
		for transaction in account.get("transactions", []):
			new_bank_transaction(transaction, account["uuid"], "accounts")

	for card in response.get("cards", []):
		for transaction in card.get("transactions", []):
			new_bank_transaction(transaction, card["uuid"], "cards")

	return processed_accounts


def _upsert_bank_account(
	account, bank_name, company, parent_gl_account, source, is_credit_card=0
):
	account_uuid = account.get("uuid")
	account_name = account.get("name") or account.get("code") or account_uuid
	full_account_name = f"{account_name} - {bank_name}"
	account_subtype = account.get("subtype", "")

	if account_subtype:
		_ensure_account_subtype(account_subtype)

	existing_bank_account = frappe.db.exists("Bank Account", full_account_name)

	if not existing_bank_account:
		frappe.db.savepoint("wr_bank_account")
		try:
			gl_account = frappe.get_doc(
				{
					"doctype": "Account",
					"account_name": account_name + " - " + bank_name,
					"parent_account": parent_gl_account,
					"account_type": "Bank",
					"company": company,
				}
			)
			gl_account.insert(ignore_if_duplicate=True)

			new_account = frappe.get_doc(
				{
					"doctype": "Bank Account",
					"bank": bank_name,
					"account": gl_account.name,
					"account_name": account_name,
					"account_type": account_subtype,
					"account_subtype": account_subtype,
					"iban": account.get("code", ""),
					"bank_account_no": account.get("code", ""),
					"integration_id": account_uuid,
					"quickbanks_source": source,
					"is_company_account": 1,
					"company": company,
					"is_credit_card": is_credit_card,
				}
			)
			new_account.insert()
			return new_account.name
		except frappe.UniqueValidationError:
			frappe.db.rollback(save_point="wr_bank_account")
			frappe.msgprint(
				_(
					"Bank account {0} already exists and could not be created again"
				).format(account_name)
			)
			return None
		except Exception:
			frappe.db.rollback(save_point="wr_bank_account")
			frappe.log_error("Wealthreader Link Error")
			frappe.throw(
				_(
					"There was an error creating Bank Account while linking with Wealthreader."
				),
				title=_("QuickBanks Link Failed"),
			)
	else:
		frappe.db.savepoint("wr_update_account")
		try:
			existing_account = frappe.get_doc("Bank Account", existing_bank_account)
			existing_account.update(
				{
					"bank": bank_name,
					"account_name": account_name,
					"account_type": account_subtype,
					"account_subtype": account_subtype,
					"iban": account.get("code", ""),
					"bank_account_no": account.get("code", ""),
					"integration_id": account_uuid,
					"quickbanks_source": source,
					"is_credit_card": is_credit_card,
				}
			)
			existing_account.save()
			return existing_bank_account
		except Exception:
			frappe.db.rollback(save_point="wr_update_account")
			frappe.log_error("Wealthreader Link Error")
			frappe.throw(
				_(
					"There was an error updating Bank Account {0} while linking with Wealthreader."
				).format(existing_bank_account),
				title=_("QuickBanks Link Failed"),
			)


@frappe.whitelist()
def sync_transactions(bank, bank_account, connection_name=None):
	"""Sync incremental transactions for a linked bank account."""
	try:
		last_transaction_date = frappe.db.get_value(
			"Bank Account", bank_account, "last_integration_date"
		)
		settings = frappe.get_single("QuickBanks Settings")

		if last_transaction_date:
			start_date = formatdate(last_transaction_date, "YYYY-MM-dd")
		elif settings.sync_start_date:
			start_date = formatdate(settings.sync_start_date, "YYYY-MM-dd")
		else:
			start_date = formatdate(add_months(today(), -12), "YYYY-MM-dd")

		end_date = formatdate(today(), "YYYY-MM-dd")

		access_token = _get_access_token(bank, connection_name)
		if not access_token:
			frappe.throw(_("Wealthreader token not found for Bank {0}").format(bank))

		connector = WealthreaderConnector()
		response = connector.refresh(
			token=access_token,
			date_from=start_date,
			date_to=end_date,
			product_types=settings.default_product_types,
		)
		if not response:
			return

		# Extract the data payload
		data = response.get("payload") or response

		# Resolve the target account UUID and source
		related_bank = frappe.db.get_values(
			"Bank Account", bank_account, ["integration_id", "quickbanks_source"], as_dict=True
		)
		if not related_bank:
			return

		account_uuid = related_bank[0].integration_id
		source = related_bank[0].quickbanks_source or "accounts"

		transactions = []
		if source == "accounts":
			for account in data.get("accounts", []):
				if account.get("uuid") == account_uuid:
					transactions = account.get("transactions", [])
					break
		elif source == "cards":
			for card in data.get("cards", []):
				if card.get("uuid") == account_uuid:
					transactions = card.get("transactions", [])
					break

		result = []
		created_dates = []
		for transaction in transactions:
			frappe.db.savepoint("wr_sync_txn")
			try:
				txn_names = new_bank_transaction(transaction, account_uuid, source)
				result.extend(txn_names)
				if txn_names:
					created_dates.append(
						frappe.db.get_value("Bank Transaction", txn_names[0], "date")
					)
			except Exception:
				frappe.db.rollback(save_point="wr_sync_txn")
				raise

		if result and created_dates:
			last_transaction_date = max(created_dates)
			frappe.db.set_value(
				"Bank Account", bank_account, "last_integration_date", last_transaction_date
			)

		if connection_name:
			frappe.db.set_value("QuickBanks Connection", connection_name, "last_sync", now())

		frappe.logger().info(
			f"Wealthreader added {len(result)} new Bank Transactions from '{bank_account}' between {start_date} and {end_date}"
		)
	except Exception:
		frappe.log_error(frappe.get_traceback(), _("Wealthreader transactions sync error"))
		raise


def _get_access_token(bank, connection_name=None):
	"""Resolve the Wealthreader token from the Connection record or the Bank fallback."""
	if connection_name:
		conn = frappe.get_doc("QuickBanks Connection", connection_name)
		if conn.token:
			return conn.get_password("token")

	bank_doc = frappe.get_doc("Bank", bank)
	if bank_doc.quickbanks_token:
		return bank_doc.get_password("quickbanks_token")

	return None


@frappe.whitelist()
def enqueue_synchronization():
	"""Queue sync jobs for all active QuickBanks connections."""
	settings = frappe.get_single("QuickBanks Settings")
	valid, message = settings.is_license_valid()
	if not valid:
		frappe.throw(message)

	connections = frappe.get_all(
		"QuickBanks Connection",
		filters={"status": "Active"},
		fields=["name", "bank", "company"],
	)

	for connection in connections:
		bank_accounts = frappe.get_all(
			"Bank Account",
			filters={
				"bank": connection.bank,
				"company": connection.company,
				"integration_id": ["!=", ""],
				"quickbanks_source": ["is", "set"],
			},
			fields=["name"],
		)
		for bank_account in bank_accounts:
			frappe.enqueue(
				"quickbanks.quickbanks.doctype.quickbanks_settings.quickbanks_settings.sync_transactions",
				bank=connection.bank,
				bank_account=bank_account.name,
				connection_name=connection.name,
			)


def automatic_synchronization():
	"""Entry point for the hourly scheduler."""
	settings = frappe.get_single("QuickBanks Settings")
	if settings.enabled and settings.automatic_sync:
		enqueue_synchronization()


def report_usage():
	"""Entry point for the daily usage-report scheduler."""
	settings = frappe.get_single("QuickBanks Settings")
	if settings.enabled and settings.hub_url and settings.activation_key:
		settings.report_usage_to_hub()


def _ensure_account_subtype(account_subtype):
	"""Create Bank Account Subtype master record if it does not exist."""
	if not account_subtype:
		return
	if not frappe.db.exists("Bank Account Subtype", account_subtype):
		try:
			frappe.get_doc(
				{"doctype": "Bank Account Subtype", "account_subtype": account_subtype}
			).insert()
		except frappe.DuplicateEntryError:
			pass


def new_bank_transaction(transaction, account_uuid, source):
	"""Create a Bank Transaction from a Wealthreader transaction dict.

	Wealthreader convention (verified against sample payloads):
	- negative amount => payment/debit from the account => withdrawal
	- positive amount => receipt/credit to the account => deposit
	This is the inverse of Plaid's account-owner-centric convention.
	"""
	result = []

	bank_account = frappe.db.get_value(
		"Bank Account",
		{"integration_id": account_uuid, "quickbanks_source": source},
	)
	if not bank_account:
		return result

	transaction_id = transaction.get("uuid")
	if not transaction_id:
		return result

	if frappe.db.exists("Bank Transaction", {"transaction_id": transaction_id}):
		return result

	# Skip unsettled/pending card transactions unless explicitly desired
	if source == "cards" and transaction.get("settled") is False:
		return result

	raw_amount = transaction.get("amount")
	if raw_amount is None:
		frappe.throw(_("Transaction amount is missing"))
	amount = flt(raw_amount)

	# Wealthreader: negative amount = debit/withdrawal, positive = credit/deposit
	if amount >= 0:
		deposit = amount
		withdrawal = 0.0
	else:
		deposit = 0.0
		withdrawal = abs(amount)

	reference_number = transaction.get("uuid")
	transfer_details = transaction.get("transfer_details") or {}
	if transfer_details.get("concept"):
		reference_number = transfer_details["concept"]
	elif transfer_details.get("sender_receiver"):
		reference_number = transfer_details["sender_receiver"]

	txn_date = transaction.get("operation_date") or transaction.get("value_date")
	if not txn_date:
		frappe.throw(_("Transaction date is missing"))

	try:
		new_transaction = frappe.get_doc(
			{
				"doctype": "Bank Transaction",
				"date": getdate(txn_date),
				"bank_account": bank_account,
				"deposit": deposit,
				"withdrawal": withdrawal,
				"currency": transaction.get("currency", ""),
				"transaction_id": transaction_id,
				"transaction_type": transaction.get("operation_type", ""),
				"reference_number": reference_number,
				"description": transaction.get("description", ""),
			}
		)
		new_transaction.insert()
		new_transaction.submit()
		result.append(new_transaction.name)
	except Exception:
		frappe.log_error(frappe.get_traceback(), _("QuickBanks Bank Transaction Error"))
		frappe.throw(_("Bank transaction creation error"))

	return result
