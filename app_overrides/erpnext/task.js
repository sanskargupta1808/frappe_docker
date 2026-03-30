// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.projects");

frappe.ui.form.on("Task", {
	setup: function (frm) {
		frm.make_methods = {
			Timesheet: () =>
				frappe.model.open_mapped_doc({
					method: "erpnext.projects.doctype.task.task.make_timesheet",
					frm: frm,
				}),
		};
	},
	onload: function (frm) {
		frm.set_query("task", "depends_on", function () {
			let filters = {
				name: ["!=", frm.doc.name],
			};
			if (frm.doc.project) filters["project"] = frm.doc.project;
			return {
				filters: filters,
			};
		});

		frm.set_query("parent_task", function () {
			let filters = {
				is_group: 1,
				name: ["!=", frm.doc.name],
			};
			if (frm.doc.project) filters["project"] = frm.doc.project;
			return {
				filters: filters,
			};
		});
	},

	refresh: function (frm) {
		if (!frm.is_new() && frappe.model.can_create("Timesheet")) {
			frm.add_custom_button(
				__("Log Time"),
				() => {
					open_timesheet_quick_log(frm, {
						project: frm.doc.project,
						project_read_only: !!frm.doc.project,
						task: frm.doc.name,
						task_read_only: true,
					});
				},
				__("Create")
			);
		}
	},

	is_group: function (frm) {
		frappe.call({
			method: "erpnext.projects.doctype.task.task.check_if_child_exists",
			args: {
				name: frm.doc.name,
			},
			callback: function (r) {
				if (r.message.length > 0) {
					let message = __(
						"Cannot convert Task to non-group because the following child Tasks exist: {0}.",
						[r.message.join(", ")]
					);
					frappe.msgprint(message);
					frm.reload_doc();
				}
			},
		});
	},

	validate: function (frm) {
		frm.doc.project && frappe.model.remove_from_locals("Project", frm.doc.project);
	},
});

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
				default: opts.project,
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

	dialog.fields_dict.task.get_query = () => {
		const project = dialog.get_value("project");
		return project ? { filters: { project } } : {};
	};

	dialog.show();
}
