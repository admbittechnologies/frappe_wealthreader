// Copyright (c) 2026, ADMBit Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Wealthreader Settings", {
	enabled: function (frm) {
		frm.toggle_reqd("api_key", frm.doc.enabled);
		frm.toggle_reqd("environment", frm.doc.enabled);
		frm.trigger("refresh");
	},

	refresh: function (frm) {
		if (!frm.doc.enabled) {
			return;
		}

		frm.add_custom_button(__("Link Bank Account"), () => {
			new erpnext.integrations.wealthreaderLink(frm);
		});

		frm.add_custom_button(__("Sync Now"), () => {
			frappe.call({
				method: "wealthreader.wealthreader.doctype.wealthreader_settings.wealthreader_settings.enqueue_synchronization",
				freeze: true,
				callback: () => {
					let bank_transaction_link = frappe.utils.get_form_link(
						"Bank Transaction",
						"",
						true,
						__("Bank Transaction")
					);

					frappe.msgprint({
						title: __("Sync Started"),
						message: __(
							"The sync has started in the background, please check the {0} list for new records.",
							[bank_transaction_link]
						),
						alert: 1,
					});
				},
			});
		}).addClass("btn-primary");
	},
});
