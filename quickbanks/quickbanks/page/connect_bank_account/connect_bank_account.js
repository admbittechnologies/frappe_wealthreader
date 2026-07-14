// Copyright (c) 2026, ADMBit Technologies and contributors
// For license information, please see license.txt

frappe.pages["connect-bank-account"] = {
	on_page_load: function (wrapper) {
		var page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Connect Bank Account"),
			single_column: true,
		});

		page.set_title(__("Connect Bank Account"));

		// Use page.main because some Frappe versions render that container more reliably.
		let $main = $(page.main || page.body);
		$main.addClass("px-4 py-4").append(
			`<div class="row">
				<div class="col-md-8">
					<div class="card p-4 mb-4">
						<h4>${__("Link a bank account")}</h4>
						<p class="text-muted">
							${__(
								"Click the button below to start the bank connection. You will be asked for a Company and a Bank Name, then the Wealthreader widget will open so you can log in to your bank."
							)}
						</p>
						<p class="text-muted">
							${__(
								"When the flow finishes, your bank accounts and transactions will be created automatically in ERPNext."
							)}
						</p>
					</div>
				</div>
			</div>`
		);

		page.set_primary_action(__("Connect Bank Account"), () => {
			let flow = new erpnext.integrations.quickbanksWidget({
				on_complete: () => {
					frappe.set_route("List", "QuickBanks Connection");
				},
			});
			flow.start();
		});
	},
};
