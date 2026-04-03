# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import append_number_if_name_exists
from frappe.utils import flt, validate_email_address

from hrms.hr.doctype.interview.interview import get_interviewers


class DuplicationError(frappe.ValidationError):
	pass


class JobApplicant(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		applicant_name: DF.Data
		applicant_rating: DF.Rating
		country: DF.Link | None
		cover_letter: DF.Text | None
		currency: DF.Link | None
		designation: DF.Link | None
		email_id: DF.Data
		employee_referral: DF.Link | None
		job_title: DF.Link | None
		lower_range: DF.Currency
		notes: DF.Data | None
		phone_number: DF.Data | None
		resume_attachment: DF.Attach | None
		resume_link: DF.Data | None
		source: DF.Link | None
		source_name: DF.Link | None
		status: DF.Literal["Open", "Replied", "Rejected", "Hold", "Accepted"]
		upper_range: DF.Currency
	# end: auto-generated types

	def onload(self):
		job_offer = frappe.get_all("Job Offer", filters={"job_applicant": self.name})
		if job_offer:
			self.get("__onload").job_offer = job_offer[0].name

	def autoname(self):
		self.name = self.email_id

		# applicant can apply more than once for a different job title or reapply
		if frappe.db.exists("Job Applicant", self.name):
			self.name = append_number_if_name_exists("Job Applicant", self.name)

	def validate(self):
		if self.email_id:
			validate_email_address(self.email_id, True)

		if self.employee_referral:
			self.set_status_for_employee_referral()

		if not self.applicant_name and self.email_id:
			guess = self.email_id.split("@")[0]
			self.applicant_name = " ".join([p.capitalize() for p in guess.split(".")])

	def on_update(self):
		self._create_employee_on_accept()

	def _create_employee_on_accept(self):
		before = self.get_doc_before_save()
		if before and before.status == self.status:
			return

		if self.status not in ["Accepted", "Cleared"]:
			return

		if _employee_exists_for_applicant(self):
			return

		employee = frappe.new_doc("Employee")
		first_name, middle_name, last_name = _split_name(self.applicant_name or self.email_id)

		employee.first_name = first_name
		if middle_name:
			employee.middle_name = middle_name
		if last_name:
			employee.last_name = last_name

		employee.company = _get_default_company()
		employee.status = "Active"
		employee.gender = _get_default_gender()
		employee.date_of_birth = _get_default_dob()
		employee.date_of_joining = frappe.utils.nowdate()

		if self.email_id:
			employee.personal_email = self.email_id
			if frappe.db.exists("User", self.email_id):
				employee.user_id = self.email_id

		if self.designation:
			employee.designation = self.designation

		employee.flags.ignore_permissions = True
		employee.insert(ignore_permissions=True)


def _employee_exists_for_applicant(applicant: JobApplicant) -> bool:
	if applicant.email_id:
		if frappe.db.exists("Employee", {"personal_email": applicant.email_id}):
			return True
		if frappe.db.exists("Employee", {"user_id": applicant.email_id}):
			return True
	return False


def _split_name(name: str | None) -> tuple[str, str | None, str | None]:
	if not name:
		return "Employee", None, None
	parts = [p for p in name.replace(",", " ").split() if p]
	if not parts:
		return "Employee", None, None
	if len(parts) == 1:
		return parts[0], None, None
	if len(parts) == 2:
		return parts[0], None, parts[1]
	return parts[0], " ".join(parts[1:-1]), parts[-1]


def _get_default_company() -> str:
	defaults = frappe.defaults.get_defaults() or {}
	company = defaults.get("company")
	if company:
		return company
	company = frappe.db.get_value("Company", {}, "name")
	if not company:
		frappe.throw(_("Please create a Company first to create Employee records."))
	return company


def _get_default_gender() -> str:
	gender = frappe.db.get_value("Gender", "Other", "name")
	if gender:
		return gender
	gender = frappe.db.get_value("Gender", "Male", "name")
	if gender:
		return gender
	gender = frappe.db.get_value("Gender", "Female", "name")
	if gender:
		return gender
	gender = frappe.db.get_value("Gender", {}, "name")
	if not gender:
		frappe.throw(_("Please create a Gender master before creating Employee records."))
	return gender


def _get_default_dob() -> str:
	# Default DOB to keep validation happy; can be updated later.
	return "1995-01-01"

	def before_insert(self):
		if self.job_title:
			job_opening_status = frappe.db.get_value("Job Opening", self.job_title, "status")
			if job_opening_status == "Closed":
				frappe.throw(
					_("Cannot create a Job Applicant against a closed Job Opening"), title=_("Not Allowed")
				)

	def set_status_for_employee_referral(self):
		emp_ref = frappe.get_doc("Employee Referral", self.employee_referral)
		if self.status in ["Open", "Replied", "Hold"]:
			emp_ref.db_set("status", "In Process")
		elif self.status in ["Accepted", "Rejected"]:
			emp_ref.db_set("status", self.status)


@frappe.whitelist()
def create_interview(job_applicant: str, interview_round: str) -> Document:
	doc = frappe.get_doc("Job Applicant", job_applicant)
	if not interview_round:
		interview_round = frappe.db.get_value(
			"Interview Round", {"designation": doc.designation}, "name"
		) or frappe.db.get_value("Interview Round", {}, "name")
		if not interview_round:
			frappe.throw(_("Please create an Interview Round first"))

	round_designation = frappe.db.get_value("Interview Round", interview_round, "designation")

	if round_designation and doc.designation and round_designation != doc.designation:
		frappe.throw(
			_("Interview Round {0} is only applicable for the Designation {1}").format(
				interview_round, round_designation
			)
		)

	interview = frappe.new_doc("Interview")
	interview.interview_round = interview_round
	interview.job_applicant = doc.name
	interview.designation = doc.designation
	interview.resume_link = doc.resume_link
	interview.job_opening = doc.job_title

	interviewers = get_interviewers(interview_round)
	for d in interviewers:
		interview.append("interview_details", {"interviewer": d.interviewer})

	return interview


@frappe.whitelist()
def get_interview_details(job_applicant: str) -> dict:
	interview_details = frappe.db.get_all(
		"Interview",
		filters={"job_applicant": job_applicant, "docstatus": ["!=", 2]},
		fields=["name", "interview_round", "scheduled_on", "average_rating", "status"],
	)
	interview_detail_map = {}
	meta = frappe.get_meta("Interview")
	number_of_stars = meta.get_options("average_rating") or 5

	for detail in interview_details:
		detail.average_rating = detail.average_rating * number_of_stars if detail.average_rating else 0

		interview_detail_map[detail.name] = detail

	return {"interviews": interview_detail_map, "stars": number_of_stars}


@frappe.whitelist()
def get_applicant_to_hire_percentage() -> dict:
	frappe.has_permission("Job Applicant", throw=True)

	total_applicants = frappe.db.count("Job Applicant")
	total_hired = frappe.db.count("Job Applicant", filters={"status": "Accepted"})

	return {
		"value": flt(total_hired) / flt(total_applicants) * 100 if total_applicants else 0,
		"fieldtype": "Percent",
	}
