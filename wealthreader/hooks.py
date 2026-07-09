# Copyright (c) 2026, ADMBit Technologies and contributors
# For license information, please see license.txt

app_name = "wealthreader"
app_title = "Wealthreader"
app_publisher = "ADMBit Technologies"
app_description = "Wealthreader bank feed integration for ERPNext"
app_email = "info@admbit.com"
app_license = "MIT"
required_apps = ["frappe/erpnext"]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "wealthreader",
# 		"logo": "/assets/wealthreader/logo.png",
# 		"title": "Wealthreader",
# 		"route": "/wealthreader",
# 		"has_permission": "wealthreader.api.permission.has_app_permission",
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/wealthreader/css/wealthreader.css"
app_include_js = "/assets/wealthreader/js/wealthreader_link.js"

# include js, css files in header of web template
# web_include_css = "/assets/wealthreader/css/wealthreader.css"
# web_include_js = "/assets/wealthreader/js/wealthreader.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "wealthreader/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "wealthreader/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "wealthreader.utils.jinja_methods",
# 	"filters": "wealthreader.utils.jinja_filters",
# 	"macros": "wealthreader.utils.jinja_macros"
# }

# Installation
# ------------

after_install = "wealthreader.setup.install.after_install"

# Fixtures
# --------

fixtures = [
	{
		"doctype": "Workspace",
		"filters": [["name", "=", "Wealthreader"]],
	}
]

# Uninstallation
# --------------

# before_uninstall = "wealthreader.uninstall.before_uninstall"
# after_uninstall = "wealthreader.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "wealthreader.utils.before_app_install"
# after_app_install = "wealthreader.utils.after_app_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "wealthreader.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"hourly": [
		"wealthreader.wealthreader.doctype.wealthreader_settings.wealthreader_settings.automatic_synchronization"
	]
}

# Testing
# -------

# before_tests = "wealthreader.install.before_tests"

# Overriding Methods
# ------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "wealthreader.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation when the hooks are referenced.

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting data
# -----------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------

# before_request = ["wealthreader.utils.before_request"]
# after_request = ["wealthreader.utils.after_request"]

# Job Events
# ----------

# before_job = ["wealthreader.utils.before_job"]
# after_job = ["wealthreader.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{first_field}", "{second_field}"],
# 		"primary": True,
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"wealthreader.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_mail_footer = "<div><span class='indicator'>Wealthreader</span></div>"

# Sounds
# ----------------

# notification_sound = "assets/wealthreader/sounds/notification.mp3"
# submission_sound = "assets/wealthreader/sounds/submission.mp3"

# setup_wizard_exception = ["wealthreader.setup.install.after_install"]
