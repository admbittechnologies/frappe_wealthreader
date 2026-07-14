// Copyright (c) 2026, ADMBit Technologies and contributors
// For license information, please see license.txt

frappe.provide("erpnext.integrations");

erpnext.integrations.quickbanksLink = class quickbanksLink {
	constructor(parent) {
		this.frm = parent || {};
		this.widgetUrl = "https://widget.wealthreader.com/js/load.js";
		this.widgetOrigin = new URL(this.widgetUrl).origin;
		this.init_config();
	}

	async init_config() {
		const config = await this.get_widget_config();

		if (!config || config.status === "disabled") {
			frappe.throw(__("QuickBanks integration is disabled."));
		}

		if (config.status === "limit_reached") {
			frappe.throw(config.message || __("Connection limit reached."));
		}

		this.operation_id = config.operation_id;
		this.environment = config.environment;
		this.default_product_types = config.default_product_types || "accounts,cards";
		this.widget_domain = config.widget_domain;
		this.date_from = config.date_from;

		frappe.prompt(
			[
				{
					fieldtype: "Link",
					options: "Company",
					label: __("Company"),
					fieldname: "company",
					reqd: 1,
					default: frappe.defaults.get_user_default("Company"),
				},
				{
					fieldtype: "Data",
					label: __("Bank Name"),
					fieldname: "bank_name",
					reqd: 1,
					default: __("QuickBanks Bank"),
				},
			],
			async (data) => {
				this.company = data.company;
				this.bank_name = data.bank_name;
				try {
					await this.create_link_session();
					this.open_widget();
				} catch (error) {
					frappe.msgprint(
						__("Could not start the QuickBanks linking session. Check Error Log for details.")
					);
					console.error(error);
				}
			},
			__("Link Bank Account"),
			__("Continue")
		);
	}

	async get_widget_config() {
		const resp = await frappe.xcall(
			"quickbanks.quickbanks.doctype.quickbanks_settings.quickbanks_settings.get_widget_config"
		);
		return resp;
	}

	async create_link_session() {
		await frappe.xcall(
			"quickbanks.quickbanks.doctype.quickbanks_settings.quickbanks_settings.create_link_session",
			{
				operation_id: this.operation_id,
				company: this.company,
				bank_name: this.bank_name,
			}
		);
	}

	open_widget() {
		const me = this;
		if (me.frm.disable_form) {
			me.frm.disable_form();
		}
		me.loadScript(me.widgetUrl)
			.then(() => {
				if (me.frm.enable_form) {
					me.frm.enable_form();
				}
				me.showWidgetModal();
			})
			.catch((error) => {
				if (me.frm.enable_form) {
					me.frm.enable_form();
				}
				me.onScriptError(error);
			});
	}

	loadScript(src) {
		return new Promise(function (resolve, reject) {
			if (document.querySelector('script[src="' + src + '"]')) {
				resolve();
				return;
			}
			const el = document.createElement("script");
			el.type = "text/javascript";
			el.async = true;
			el.src = src;
			el.addEventListener("load", resolve);
			el.addEventListener("error", reject);
			el.addEventListener("abort", reject);
			document.head.appendChild(el);
		});
	}

	showWidgetModal() {
		const me = this;

		const dialog = new frappe.ui.Dialog({
			title: __("Link Bank Account"),
			fields: [
				{
					fieldname: "widget_html",
					fieldtype: "HTML",
					options: `<iframe id="wr-iframe" title="Wealth Reader widget" width="100%" height="600" frameBorder="0" referrerpolicy="origin"></iframe>`,
				},
			],
			size: "large",
		});

		dialog.show();

		// Configure and load the widget
		window.wr_conf = {
			operation_id: me.operation_id,
			entities_to_display: [],
			wait_full_response: true,
			product_types: me.default_product_types,
		};

		if (me.widget_domain) {
			window.wr_conf.widget_domain = me.widget_domain;
		}

		if (me.date_from) {
			window.wr_conf.date_from = me.date_from;
		}

		// Listen for widget messages
		const messageHandler = (e) => {
			// Only trust messages from the Wealthreader widget origin
			if (e.origin !== me.widgetOrigin) {
				return;
			}

			if (e.data === "flow completed") {
				dialog.hide();
				window.removeEventListener("message", messageHandler);

				frappe.show_alert({
					message: __(
						"Bank linking completed. Accounts and transactions will appear via the callback shortly."
					),
					indicator: "green",
				});
			} else if (e.data === "flow failed" || e.data === "flow cancelled") {
				dialog.hide();
				window.removeEventListener("message", messageHandler);

				frappe.show_alert({
					message: __(
						"Bank linking was not completed. You can try again."
					),
					indicator: "red",
				});
			}
		};
		window.addEventListener("message", messageHandler);

		// Clean up listener if the user closes the dialog manually
		dialog.onhide = () => {
			window.removeEventListener("message", messageHandler);
		};
	}

	onScriptError(error) {
		frappe.msgprint(
			__("There was an issue loading the Wealthreader widget. Check the browser console for details.")
		);
		console.error(error);
	}
};
