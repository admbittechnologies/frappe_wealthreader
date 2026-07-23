// Copyright (c) 2026, ADMBit Technologies and contributors
// For license information, please see license.txt

frappe.provide("erpnext.integrations");

/**
 * Self-service Wealthreader widget flow.
 *
 * Usage:
 *   let flow = new erpnext.integrations.quickbanksWidget();
 *   flow.start();
 *
 * The helper asks for Company and Bank Name, creates a link session on the
 * server and opens the Wealthreader iframe widget.  When the widget finishes,
 * the data is delivered to the configured callback URL and the ERPNext Bank,
 * Bank Account and Bank Transaction records are created automatically.
 */
erpnext.integrations.quickbanksWidget = class quickbanksWidget {
	constructor(opts) {
		opts = opts || {};
		this.on_complete = opts.on_complete;
		this.on_close = opts.on_close;
	}

	async start() {
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
		this.hub_url = config.hub_url;
		this.activation_key = config.activation_key;
		this.callback_url = config.callback_url;
		this.hub_origin = this.hub_url ? new URL(this.hub_url).origin : "";
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
			__("Connect Bank Account"),
			__("Continue")
		);
	}

	async get_widget_config() {
		return await frappe.xcall(
			"quickbanks.quickbanks.doctype.quickbanks_settings.quickbanks_settings.get_widget_config"
		);
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

		const widgetUrl = me.build_widget_url();

		const dialog = new frappe.ui.Dialog({
			title: __("Connect Bank Account"),
			fields: [
				{
					fieldname: "widget_html",
					fieldtype: "HTML",
					options: `<iframe id="wr-iframe" src="${widgetUrl}" title="Wealth Reader widget" width="100%" height="650" frameBorder="0" referrerpolicy="origin"></iframe>`,
				},
			],
			size: "large",
		});

		dialog.show();

		// Listen for widget lifecycle messages relayed by the Hub page.
		const messageHandler = (e) => {
			if (e.origin !== me.hub_origin) {
				return;
			}

			if (e.data === "flow completed") {
				dialog.hide();
				window.removeEventListener("message", messageHandler);

				frappe.show_alert({
					message: __(
						"Bank linking completed. Accounts and transactions will appear shortly via the callback."
					),
					indicator: "green",
				});

				if (me.on_complete) {
					me.on_complete();
				}
			} else if (e.data === "flow failed" || e.data === "flow cancelled") {
				dialog.hide();
				window.removeEventListener("message", messageHandler);

				frappe.show_alert({
					message: __("Bank linking was not completed. You can try again."),
					indicator: "red",
				});
			}
		};
		window.addEventListener("message", messageHandler);

		dialog.onhide = () => {
			window.removeEventListener("message", messageHandler);
			if (me.on_close) {
				me.on_close();
			}
		};
	}

	build_widget_url() {
		const params = new URLSearchParams();
		params.set("activation_key", this.activation_key);
		params.set("operation_id", this.operation_id);
		params.set("callback_url", this.callback_url);
		params.set("parent_origin", window.location.origin);
		params.set("product_types", this.default_product_types);
		if (this.date_from) {
			params.set("date_from", this.date_from);
		}
		return `${this.hub_url}/api/method/wealthreader_hub.wealthreader_hub.api.widget?${params.toString()}`;
	}
};
