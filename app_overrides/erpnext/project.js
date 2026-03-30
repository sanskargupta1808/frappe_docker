// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
frappe.ui.form.on("Project", {
	setup(frm) {
		frm.make_methods = {
			Timesheet: () => {
				open_form(frm, "Timesheet", "Timesheet Detail", "time_logs");
			},
			"Purchase Order": () => {
				open_form(frm, "Purchase Order", "Purchase Order Item", "items");
			},
			"Purchase Receipt": () => {
				open_form(frm, "Purchase Receipt", "Purchase Receipt Item", "items");
			},
			"Purchase Invoice": () => {
				open_form(frm, "Purchase Invoice", "Purchase Invoice Item", "items");
			},
		};
	},
	onload: function (frm) {
		const so = frm.get_docfield("sales_order");
		so.get_route_options_for_new_doc = () => {
			if (frm.is_new()) return {};
			return {
				customer: frm.doc.customer,
				project_name: frm.doc.name,
			};
		};

		frm.set_query("user", "users", function () {
			return {
				query: "erpnext.projects.doctype.project.project.get_users_for_project",
			};
		});

		frm.set_query("department", function (doc) {
			return {
				filters: {
					company: doc.company,
				},
			};
		});

		// sales order
		frm.set_query("sales_order", function () {
			var filters = {
				project: ["in", frm.doc.__islocal ? [""] : [frm.doc.name, ""]],
				company: frm.doc.company,
			};

			if (frm.doc.customer) {
				filters["customer"] = frm.doc.customer;
			}

			return {
				filters: filters,
			};
		});

		frm.set_query("cost_center", () => {
			return {
				filters: {
					company: frm.doc.company,
				},
			};
		});
	},

	refresh: function (frm) {
		if (frm.doc.__islocal) {
			frm.web_link && frm.web_link.remove();
		} else {
			frm.add_web_link("/projects?project=" + encodeURIComponent(frm.doc.name));

			frm.trigger("show_dashboard");
		}
		frm.trigger("set_custom_buttons");
		frm.trigger("set_quick_log_button");
		frm.trigger("show_project_tasks");
	},

	set_custom_buttons: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(
				__("Duplicate Project with Tasks"),
				() => {
					frm.events.create_duplicate(frm);
				},
				__("Actions")
			);

			frm.add_custom_button(
				__("Update Costing and Billing"),
				() => {
					frm.events.update_costing_and_billing(frm);
				},
				__("Actions")
			);

			frm.trigger("set_project_status_button");

			if (frappe.model.can_read("Task")) {
				frm.add_custom_button(
					__("Gantt Chart"),
					function () {
						frappe.route_options = {
							project: frm.doc.name,
						};
						frappe.set_route("List", "Task", "Gantt");
					},
					__("View")
				);

				frm.add_custom_button(
					__("Kanban Board"),
					() => {
						frappe
							.call(
								"erpnext.projects.doctype.project.project.create_kanban_board_if_not_exists",
								{
									project: frm.doc.name,
								}
							)
							.then(() => {
								frappe.set_route("List", "Task", "Kanban", frm.doc.project_name);
							});
					},
					__("View")
				);
			}
		}
	},

	set_quick_log_button: function (frm) {
		if (!frm.is_new() && frappe.model.can_create("Timesheet")) {
			frm.add_custom_button(
				__("Log Time"),
				() => {
					open_timesheet_quick_log(frm, {
						project: frm.doc.name,
						project_read_only: true,
					});
				},
				__("Create")
			);
		}
	},

	show_project_tasks: function (frm) {
		if (frm.is_new() || !frappe.model.can_read("Task")) {
			return;
		}

		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Task",
				fields: ["name", "subject", "status", "priority", "exp_end_date"],
				filters: { project: frm.doc.name },
				order_by: "modified desc",
				limit_page_length: 50,
			},
			callback: (r) => {
				if (frm.project_tasks_section) {
					frm.project_tasks_section.remove();
				}

				const section = frm.dashboard.add_section("", __("Project Tasks"));
				frm.project_tasks_section = section;
				const rows = $("<div class='project-task-list'></div>").appendTo(section);

				if (!r.message || r.message.length === 0) {
					$("<div class='text-muted'>No tasks yet.</div>").appendTo(rows);
					frm.dashboard.show();
					return;
				}

				const table = $(`
					<table class="table table-bordered">
						<thead>
							<tr>
								<th>${__("Task")}</th>
								<th>${__("Status")}</th>
								<th>${__("Priority")}</th>
								<th>${__("Expected End")}</th>
								<th>${__("Log Time")}</th>
							</tr>
						</thead>
						<tbody></tbody>
					</table>
				`);

				r.message.forEach((task) => {
					const row = $(`
						<tr>
							<td>
								<a href="/app/task/${encodeURIComponent(task.name)}">
									${frappe.utils.escape_html(task.subject || task.name)}
								</a>
							</td>
							<td>${frappe.utils.escape_html(task.status || "")}</td>
							<td>${frappe.utils.escape_html(task.priority || "")}</td>
							<td>${task.exp_end_date ? frappe.datetime.str_to_user(task.exp_end_date) : ""}</td>
							<td>
								<button class="btn btn-xs btn-primary">
									${__("Log Time")}
								</button>
							</td>
						</tr>
					`);

					row.find("button").on("click", () => {
						open_timesheet_quick_log(frm, {
							project: frm.doc.name,
							project_read_only: true,
							task: task.name,
							task_read_only: true,
						});
					});

					table.find("tbody").append(row);
				});

				rows.append(table);
				frm.dashboard.show();
			},
		});
	},

	update_costing_and_billing: function (frm) {
		frappe.call({
			method: "erpnext.projects.doctype.project.project.update_costing_and_billing",
			args: { project: frm.doc.name },
			freeze: true,
			freeze_message: __("Updating Costing and Billing fields against this Project..."),
			callback: function (r) {
				if (r && !r.exc) {
					frappe.msgprint(__("Costing and Billing fields has been updated"));
					frm.refresh();
				}
			},
		});
	},

	set_project_status_button: function (frm) {
		frm.add_custom_button(
			__("Set Project Status"),
			() => frm.events.get_project_status_dialog(frm).show(),
			__("Actions")
		);
	},

	get_project_status_dialog: function (frm) {
		const dialog = new frappe.ui.Dialog({
			title: __("Set Project Status"),
			fields: [
				{
					fieldname: "status",
					fieldtype: "Select",
					label: "Status",
					reqd: 1,
					options: "Completed\nCancelled",
				},
			],
			primary_action: function () {
				frm.events.set_status(frm, dialog.get_values().status);
				dialog.hide();
			},
			primary_action_label: __("Set Project Status"),
		});
		return dialog;
	},

	create_duplicate: function (frm) {
		return new Promise((resolve) => {
			frappe.prompt("Project Name", (data) => {
				frappe
					.xcall("erpnext.projects.doctype.project.project.create_duplicate_project", {
						prev_doc: frm.doc,
						project_name: data.value,
					})
					.then(() => {
						frappe.set_route("Form", "Project", data.value);
						frappe.show_alert(__("Duplicate project has been created"));
					});
				resolve();
			});
		});
	},

	set_status: function (frm, status) {
		frappe.confirm(__("Set Project and all Tasks to status {0}?", [__(status).bold()]), () => {
			frappe
				.xcall("erpnext.projects.doctype.project.project.set_project_status", {
					project: frm.doc.name,
					status: status,
				})
				.then(() => {
					frm.reload_doc();
				});
		});
	},

	collect_progress: function (frm) {
		if (frm.doc.collect_progress && !frm.doc.subject) {
			frm.set_value("subject", __("For project - {0}, update your status", [frm.doc.project_name]));
		}
	},
});

function open_form(frm, doctype, child_doctype, parentfield) {
	frappe.model.with_doctype(doctype, () => {
		let new_doc = frappe.model.get_new_doc(doctype);

		// add a new row and set the project
		let new_child_doc = frappe.model.get_new_doc(child_doctype);
		new_child_doc.project = frm.doc.name;
		new_child_doc.parent = new_doc.name;
		new_child_doc.parentfield = parentfield;
		new_child_doc.parenttype = doctype;
		new_doc[parentfield] = [new_child_doc];
		new_doc.project = frm.doc.name;

		frappe.ui.form.make_quick_entry(doctype, null, null, new_doc);
	});
}

function open_timesheet_quick_log(frm, opts = {}) {
	const dialog = new frappe.ui.Dialog({
		title: __("Log Time"),
		fields: [
			{
				fieldname: "project",
				fieldtype: "Link",
				label: __("Project"),
				options: "Project",
				reqd: 1,
				read_only: opts.project_read_only ? 1 : 0,
				default: opts.project || frm.doc.name,
			},
			{
				fieldname: "task",
				fieldtype: "Link",
				label: __("Task"),
				options: "Task",
				reqd: 1,
				read_only: opts.task_read_only ? 1 : 0,
				default: opts.task,
			},
			{
				fieldname: "activity_type",
				fieldtype: "Link",
				label: __("Activity Type"),
				options: "Activity Type",
				reqd: 1,
			},
			{
				fieldname: "hours",
				fieldtype: "Float",
				label: __("Hours"),
				reqd: 1,
				default: 1,
			},
			{
				fieldname: "log_date",
				fieldtype: "Date",
				label: __("Date"),
				reqd: 1,
				default: frappe.datetime.now_date(),
			},
			{
				fieldname: "description",
				fieldtype: "Small Text",
				label: __("Work Description"),
			},
		],
		primary_action_label: __("Log Time"),
		primary_action(values) {
			if (!values) return;
			frappe.call({
				method: "hrms.overrides.employee_timesheet.quick_log_time",
				args: values,
				freeze: true,
				callback: (r) => {
					if (!r.exc) {
						dialog.hide();
						frappe.show_alert({
							message: __("Time logged in Timesheet {0}", [r.message]),
							indicator: "green",
						});
					}
				},
			});
		},
	});

	const project_field = dialog.get_field("project");
	project_field.df.onchange = () => {
		dialog.set_value("task", "");
	};
	project_field.refresh();

	dialog.fields_dict.task.get_query = () => {
		const project = dialog.get_value("project");
		return project ? { filters: { project } } : {};
	};

	dialog.show();
}
