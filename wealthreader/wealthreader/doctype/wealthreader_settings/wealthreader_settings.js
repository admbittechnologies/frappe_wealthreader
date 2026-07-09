// Copyright (c) 2026, ADMBit Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Wealthreader Settings", {
	enabled: function (frm) {
		frm.toggle_reqd("api_key", frm.doc.enabled);
		frm.toggle_reqd("environment", frm.doc.enabled);
		frm.trigger("refresh");
	},

	refresh: function (frm) {
		frm.trigger("render_license_summary");

		if (!frm.doc.enabled) {
			return;
		}

		frappe.xcall(
			"wealthreader.wealthreader.doctype.wealthreader_settings.wealthreader_settings.get_license_summary"
		).then((summary) => {
			frm._license_summary = summary;
			frm.trigger("render_license_summary");

			if (summary.can_add_connection) {
				frm.add_custom_button(__("Link Bank Account"), () => {
					new erpnext.integrations.wealthreaderLink(frm);
				});
			}
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

	render_license_summary: function (frm) {
		let summary = frm._license_summary || {
			license_status: frm.doc.enabled ? "Loading..." : "Disabled",
			active_connections: "-",
			allowed_connections: "-",
			expiry_date: null,
			can_add_connection: false,
			message: "",
		};

		let status_color = {
			Active: "green",
			Disabled: "grey",
			Expired: "red",
			"Limit Reached": "orange",
			"No License": "red",
			"Loading...": "grey",
		}[summary.license_status] || "grey";

		let html = `
			<div class="row">
				<div class="col-md-6">
					<table class="table table-bordered" style="margin-top: 0;">
						<tr>
							<td style="width: 50%;"><strong>${__("License Status")}</strong></td>
							<td><span class="indicator ${status_color}">${__(summary.license_status)}</span></td>
						</tr>
						<tr>
							<td><strong>${__("Active Connections")}</strong></td>
							<td>${summary.active_connections} / ${summary.allowed_connections}</td>
						</tr>
						${
							summary.expiry_date
								? `<tr><td><strong>${__("Expiry Date")}</strong></td><td>${summary.expiry_date}</td></tr>`
								: ""
						}
					</table>
				</div>
				<div class="col-md-6">
					<div class="text-muted">
						${__("Each active bank connection is billed at €15/month. Manage connections from the Wealthreader Connection list.")}
					</div>
					${
						summary.message && !summary.can_add_connection
							? `<div class="alert alert-warning margin-top" style="margin-top: 10px;">${__(summary.message)}</div>`
							: ""
					}
				</div>
			</div>
		`;

		frm.fields_dict.license_summary.$wrapper.html(html);
	},
});
