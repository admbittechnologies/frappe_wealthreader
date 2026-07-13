// Copyright (c) 2026, ADMBit Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Wealthreader Settings", {
	enabled: function (frm) {
		frm.trigger("refresh");
	},

	refresh: function (frm) {
		if (!frm.doc.enabled) {
			return;
		}

		if (frm.doc.hub_url && frm.doc.activation_key && !frm.doc.api_key) {
			frm.add_custom_button(__("Activate"), () => {
				frm.save().then(() => {
					frappe.show_alert({
						message: __("Activation complete. Please refresh the page."),
						indicator: "green",
					});
				});
			}).addClass("btn-primary");
		}

		if (frm.doc.api_key) {
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
		}
	},
});
