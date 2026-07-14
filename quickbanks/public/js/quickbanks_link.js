// Copyright (c) 2026, ADMBit Technologies and contributors
// For license information, please see license.txt

frappe.provide("erpnext.integrations");

/**
 * Thin wrapper used by the QuickBanks Settings form.
 * The actual widget flow lives in quickbanks_widget.js.
 */
erpnext.integrations.quickbanksLink = class quickbanksLink {
	constructor(parent) {
		this.frm = parent || {};
		this.flow = new erpnext.integrations.quickbanksWidget({
			on_complete: () => {
				frappe.show_alert({
					message: __("Bank linking completed."),
					indicator: "green",
				});
			},
		});
		this.flow.start();
	}
};
