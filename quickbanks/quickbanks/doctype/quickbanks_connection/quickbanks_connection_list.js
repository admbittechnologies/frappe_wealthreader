// Copyright (c) 2026, ADMBit Technologies and contributors
// For license information, please see license.txt

frappe.listview_settings["QuickBanks Connection"] = {
	onload: function (listview) {
		listview.page.add_inner_button(__("Connect Bank Account"), function () {
			new erpnext.integrations.quickbanksLink({});
		});

		frappe.xcall(
			"quickbanks.quickbanks.doctype.quickbanks_settings.quickbanks_settings.get_license_summary"
		).then((summary) => {
			let monthly_cost = flt(summary.active_connections) * 15;
			let indicator = summary.can_add_connection ? "green" : "orange";
			let message = summary.can_add_connection
				? __(
						"Active connections: {0} of {1} · Monthly cost: €{2}",
						[summary.active_connections, summary.allowed_connections, monthly_cost]
				  )
				: summary.message;

			let banner = `
				<div class="row">
					<div class="col-md-12">
						<div class="alert alert-${indicator}">
							${message}
						</div>
					</div>
				</div>
			`;
			listview.page.wrapper.find(".list-row-head").before(banner);
		});
	},
};
