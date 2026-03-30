# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import annotations

from datetime import timedelta

import frappe
from frappe.utils.data import flt
from frappe.utils import format_date, format_time, get_datetime, nowdate

from erpnext.projects.doctype.timesheet.timesheet import Timesheet
from hrms.hr.doctype.daily_work_summary.daily_work_summary import get_user_emails_from_group


class EmployeeTimesheet(Timesheet):
	def set_status(self):
		self.status = {"0": "Draft", "1": "Submitted", "2": "Cancelled"}[str(self.docstatus or 0)]

		if flt(self.per_billed, self.precision("per_billed")) >= 100.0:
			self.status = "Billed"

		if 0.0 < flt(self.per_billed, self.precision("per_billed")) < 100.0:
			self.status = "Partially Billed"

		if self.salary_slip:
			self.status = "Payslip"

		if self.sales_invoice and self.salary_slip:
			self.status = "Completed"

	def on_submit(self):
		super().on_submit()
		try:
			post_timesheet_to_daily_work_summary(self)
		except Exception:
			frappe.log_error(
				frappe.get_traceback(),
				"Timesheet -> Daily Work Summary auto-post failed",
			)


@frappe.whitelist()
def quick_log_time(project=None, task=None, activity_type=None, hours=None, log_date=None, description=None):
	user = frappe.session.user
	if not user or user == "Guest":
		frappe.throw("Login required to log time.")

	hours = flt(hours)
	if hours <= 0:
		frappe.throw("Hours must be greater than zero.")

	if not activity_type:
		frappe.throw("Activity Type is required.")

	if not task:
		frappe.throw("Task is required.")

	task_project = None
	if task:
		task_project = frappe.db.get_value("Task", task, "project")
		if not project:
			project = task_project
		elif task_project and task_project != project:
			frappe.throw("Selected task does not belong to the chosen project.")

	log_date = log_date or nowdate()
	from_time = get_next_available_start(user, log_date)
	to_time = from_time + timedelta(hours=hours)

	employee = frappe.db.get_value("Employee", {"user_id": user, "status": "Active"}, "name")
	company = None
	if employee:
		company = frappe.db.get_value("Employee", employee, "company")

	timesheet = get_or_create_timesheet(user, log_date, employee, company)
	timesheet.append(
		"time_logs",
		{
			"activity_type": activity_type,
			"from_time": from_time,
			"to_time": to_time,
			"hours": hours,
			"project": project,
			"task": task,
			"description": description,
		},
	)
	timesheet.save()
	return timesheet.name


def get_or_create_timesheet(user, log_date, employee=None, company=None):
	name = frappe.db.get_value(
		"Timesheet",
		{
			"docstatus": 0,
			"user": user,
			"start_date": log_date,
			"end_date": log_date,
		},
		"name",
	)
	if name:
		return frappe.get_doc("Timesheet", name)

	timesheet = frappe.get_doc({"doctype": "Timesheet", "user": user})
	if employee:
		timesheet.employee = employee
	if company:
		timesheet.company = company
	return timesheet


def get_next_available_start(user, log_date):
	start_of_day = get_datetime(f"{log_date} 09:00:00")
	last_to = frappe.db.sql(
		"""
		select max(td.to_time)
		from `tabTimesheet Detail` td
		join `tabTimesheet` t on t.name = td.parent
		where t.docstatus < 2
			and t.user = %s
			and td.from_time is not null
			and date(td.from_time) = %s
		""",
		(user, log_date),
	)
	last_to = last_to[0][0] if last_to else None
	if last_to and get_datetime(last_to) > start_of_day:
		return get_datetime(last_to)
	return start_of_day


def post_timesheet_to_daily_work_summary(timesheet: Timesheet) -> None:
	user = timesheet.user
	if not user and timesheet.employee:
		user = frappe.db.get_value("Employee", timesheet.employee, "user_id")

	if not user:
		return

	user_email = frappe.db.get_value("User", user, "email")
	if not user_email:
		return

	groups = get_enabled_groups_for_user(user)
	if not groups:
		return

	text = build_timesheet_text(timesheet)
	if not text:
		return

	for group in groups:
		daily_work_summary = get_or_create_daily_work_summary(group)
		subject = f"Timesheet {timesheet.name} submitted"

		if frappe.db.exists(
			"Communication",
			{
				"reference_doctype": "Daily Work Summary",
				"reference_name": daily_work_summary.name,
				"sender": user_email,
				"subject": subject,
			},
		):
			continue

		communication = frappe.get_doc(
			{
				"doctype": "Communication",
				"communication_type": "Communication",
				"communication_medium": "Email",
				"sent_or_received": "Received",
				"reference_doctype": "Daily Work Summary",
				"reference_name": daily_work_summary.name,
				"subject": subject,
				"sender": user_email,
				"content": text,
				"text_content": text,
			}
		)
		communication.insert(ignore_permissions=True)


def get_enabled_groups_for_user(user: str) -> list[str]:
	group_names = frappe.get_all(
		"Daily Work Summary Group User", filters={"user": user}, pluck="parent"
	)
	if not group_names:
		return []

	return frappe.get_all(
		"Daily Work Summary Group",
		filters={"name": ["in", group_names], "enabled": 1},
		pluck="name",
	)


def get_or_create_daily_work_summary(group: str):
	start = get_datetime(nowdate())
	end = start + timedelta(days=1)

	name = frappe.db.get_value(
		"Daily Work Summary",
		{
			"daily_work_summary_group": group,
			"status": "Open",
			"creation": ["between", [start, end]],
		},
		"name",
		order_by="creation desc",
	)

	if name:
		return frappe.get_doc("Daily Work Summary", name)

	group_doc = frappe.get_doc("Daily Work Summary Group", group)
	emails = get_user_emails_from_group(group_doc) or []

	daily_work_summary = frappe.get_doc(
		{
			"doctype": "Daily Work Summary",
			"daily_work_summary_group": group_doc.name,
			"email_sent_to": "\n".join(emails),
		}
	)
	return daily_work_summary.insert(ignore_permissions=True)


def build_timesheet_text(timesheet: Timesheet) -> str:
	lines = []
	for row in timesheet.time_logs:
		activity = row.activity_type or "-"
		project = row.project or "-"
		task = row.task or "-"
		hours = row.hours or 0
		description = (row.description or "").strip()

		time_range = ""
		if row.from_time and row.to_time:
			try:
				time_range = f"{format_time(row.from_time)}-{format_time(row.to_time)}"
			except Exception:
				time_range = ""

		parts = [activity, f"{hours}h"]
		if time_range:
			parts.append(time_range)
		if project != "-":
			parts.append(f"Project: {project}")
		if task != "-":
			parts.append(f"Task: {task}")
		if description:
			parts.append(description)

		lines.append("- " + " | ".join(parts))

	if not lines:
		return ""

	header = f"Timesheet {timesheet.name} submitted"
	if timesheet.start_date or timesheet.end_date:
		start = format_date(timesheet.start_date) if timesheet.start_date else ""
		end = format_date(timesheet.end_date) if timesheet.end_date else ""
		if start or end:
			header += f" ({start} - {end})"

	total = f"Total Hours: {timesheet.total_hours or 0}"

	return "\n".join([header, total, "", *lines])
