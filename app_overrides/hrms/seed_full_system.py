# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import annotations

import os
import random
import re
import string
from collections.abc import Iterable

import frappe
from frappe import _
from frappe.utils import add_days, add_months, nowdate


INDIA_FIRST_NAMES = [
	"Aarav",
	"Vivaan",
	"Aditya",
	"Vihaan",
	"Arjun",
	"Ishaan",
	"Kabir",
	"Rohan",
	"Rahul",
	"Kunal",
	"Siddharth",
	"Manish",
	"Arnav",
	"Pranav",
	"Ritvik",
	"Ananya",
	"Aditi",
	"Isha",
	"Kavya",
	"Priya",
	"Riya",
	"Sneha",
	"Pooja",
	"Meera",
	"Neha",
	"Nisha",
	"Tanvi",
	"Shruti",
]
INDIA_LAST_NAMES = [
	"Sharma",
	"Verma",
	"Gupta",
	"Patel",
	"Mehta",
	"Shah",
	"Khan",
	"Iyer",
	"Nair",
	"Menon",
	"Reddy",
	"Das",
	"Roy",
	"Bose",
	"Chatterjee",
	"Jain",
	"Singh",
	"Bhat",
	"Kulkarni",
	"Joshi",
]
INDIA_CITIES = [
	"Mumbai",
	"Delhi",
	"Bengaluru",
	"Hyderabad",
	"Chennai",
	"Pune",
	"Kolkata",
	"Ahmedabad",
	"Jaipur",
	"Surat",
	"Noida",
	"Gurugram",
	"Indore",
	"Lucknow",
	"Bhopal",
	"Chandigarh",
]
INDIA_STATES = {
	"Mumbai": "Maharashtra",
	"Delhi": "Delhi",
	"Bengaluru": "Karnataka",
	"Hyderabad": "Telangana",
	"Chennai": "Tamil Nadu",
	"Pune": "Maharashtra",
	"Kolkata": "West Bengal",
	"Ahmedabad": "Gujarat",
	"Jaipur": "Rajasthan",
	"Surat": "Gujarat",
	"Noida": "Uttar Pradesh",
	"Gurugram": "Haryana",
	"Indore": "Madhya Pradesh",
	"Lucknow": "Uttar Pradesh",
	"Bhopal": "Madhya Pradesh",
	"Chandigarh": "Chandigarh",
}
INDIA_STREETS = [
	"MG Road",
	"Brigade Road",
	"Link Road",
	"Park Street",
	"Banjara Hills",
	"Hitech City",
	"Anna Salai",
	"FC Road",
	"Sector 18",
	"Salt Lake",
	"Civil Lines",
	"Ashok Nagar",
	"Viman Nagar",
	"Navrangpura",
]
INDIA_DOMAINS = [
	"aakartech.in",
	"nimbuscorp.in",
	"pragati.co.in",
	"vistaragroup.in",
	"horizonlabs.in",
	"orbitnet.in",
	"saakshar.in",
	"avani.in",
	"triveni.in",
	"rangoli.in",
	"nurture.in",
	"aurora.in",
	"meridian.in",
	"satwik.in",
]
COMPANY_PREFIXES = [
	"Nimbus",
	"Apex",
	"BlueSky",
	"GreenLeaf",
	"Bright",
	"Swift",
	"Silverline",
	"Urban",
	"Sunrise",
	"NorthStar",
	"Quantum",
	"Everest",
	"Sapphire",
	"Prism",
	"Indigo",
	"Harmony",
	"Pioneer",
	"Summit",
]
COMPANY_SUFFIXES = [
	"Technologies",
	"Systems",
	"Solutions",
	"Industries",
	"Labs",
	"Enterprises",
	"Consulting",
	"Foods",
	"Retail",
	"Logistics",
	"Services",
	"Manufacturing",
	"Networks",
	"Pharma",
	"Energy",
	"Infotech",
]
PRODUCT_NAMES = [
	"Laptop",
	"Desktop",
	"Monitor",
	"Printer",
	"Router",
	"Switch",
	"UPS",
	"Server",
	"Office Chair",
	"Standing Desk",
	"Projector",
	"Scanner",
	"Air Conditioner",
	"Phone",
	"Tablet",
]
PROJECT_NAMES = [
	"Website Revamp",
	"Mobile App Launch",
	"ERP Rollout",
	"Customer Portal",
	"Data Migration",
	"HR Process Upgrade",
	"CRM Optimization",
	"Warehouse Automation",
	"Finance Dashboard",
	"Recruitment Drive",
]
TASK_NAMES = [
	"Requirement Gathering",
	"Design Review",
	"Backend Setup",
	"Frontend Implementation",
	"Testing",
	"User Training",
	"Go Live",
	"Documentation",
	"Data Cleanup",
	"Stakeholder Review",
]
SUBJECT_LINES = [
	"Onboarding",
	"Follow-up Call",
	"Site Visit",
	"Budget Review",
	"Quality Check",
	"Weekly Update",
	"Vendor Discussion",
	"Client Presentation",
	"Contract Review",
	"Status Meeting",
]
BANNED_WORDS = ("demo", "seed", "sample", "example")


def _rand_suffix(length: int = 4) -> str:
	return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def _compose_label(prefix: str | None, base: str, index: int | None = None) -> str:
	parts: list[str] = []
	if prefix:
		prefix = prefix.strip()
		if prefix:
			parts.append(prefix)
	if base:
		base = base.strip()
		if base:
			parts.append(base)
	if index is not None:
		parts.append(str(index))
	return " ".join(parts).strip()


def _rand_choice(options: Iterable[str]) -> str:
	options_list = list(options)
	return random.choice(options_list) if options_list else ""


def _rand_full_name() -> str:
	return f"{_rand_choice(INDIA_FIRST_NAMES)} {_rand_choice(INDIA_LAST_NAMES)}"


def _rand_company() -> str:
	return f"{_rand_choice(COMPANY_PREFIXES)} {_rand_choice(COMPANY_SUFFIXES)}"


def _rand_city_state() -> tuple[str, str]:
	city = _rand_choice(INDIA_CITIES)
	return city, INDIA_STATES.get(city, "India")


def _rand_pincode() -> str:
	return f"{random.randint(110001, 899999)}"


def _rand_phone() -> str:
	return f"{random.randint(6, 9)}{random.randint(100000000, 999999999)}"


def _rand_email(name: str | None = None, company: str | None = None) -> str:
	base = (name or _rand_choice(INDIA_FIRST_NAMES)).lower().replace(" ", ".")
	domain_root = (company or "").lower().replace(" ", "")
	if not domain_root or _has_banned(domain_root):
		domain_root = _rand_choice(INDIA_DOMAINS)
		if "@" in domain_root:
			domain_root = domain_root.split("@", 1)[1]
		return f"{base}.{random.randint(10, 99)}@{domain_root}"
	return f"{base}.{random.randint(10, 99)}@{domain_root}.in"


def _rand_address() -> str:
	city, _state = _rand_city_state()
	return f"{random.randint(10, 350)} { _rand_choice(INDIA_STREETS)}, {city}"


def _rand_item_name() -> str:
	return f"{_rand_choice(PRODUCT_NAMES)} {random.randint(100, 999)}"


def _rand_item_code() -> str:
	code_root = _rand_choice(["LAP", "DESK", "MON", "PRN", "RTR", "UPS", "SRV", "CHR", "AC"])
	return f"{code_root}-{_rand_suffix(3)}"


def _rand_subject() -> str:
	return _rand_choice(SUBJECT_LINES)


def _rand_sentence() -> str:
	return f"{_rand_choice(SUBJECT_LINES)} for {_rand_choice(INDIA_CITIES)} office"


def _rand_date(days_back: int = 365) -> str:
	return add_days(nowdate(), -random.randint(0, days_back))


def _has_banned(value: str | None) -> bool:
	if not value:
		return False
	lower = str(value).lower()
	return any(word in lower for word in BANNED_WORDS)


def _doctype_exists(doctype: str) -> bool:
	return bool(frappe.db.exists("DocType", doctype))


def _safe_insert(doc, *, ignore_mandatory: bool = True, ignore_validate: bool = True):
	doc.flags.ignore_permissions = True
	if ignore_mandatory:
		doc.flags.ignore_mandatory = True
	if ignore_validate:
		doc.flags.ignore_validate = True
	doc.insert()
	return doc


def _safe_submit(doc, *, ignore_validate: bool = True):
	doc.flags.ignore_permissions = True
	if ignore_validate:
		doc.flags.ignore_validate = True
	doc.submit()
	return doc


def _get_default_company() -> str | None:
	company = frappe.db.get_single_value("Global Defaults", "default_company")
	if company:
		return company
	return frappe.db.get_value("Company", {}, "name")


def _get_company_currency(company: str) -> str | None:
	return frappe.db.get_value("Company", company, "default_currency")


def _ensure_simple(doctype: str, name_field: str, value: str, extra: dict | None = None) -> str:
	extra = extra or {}
	existing = frappe.db.exists(doctype, {name_field: value})
	if existing:
		return existing
	doc = frappe.get_doc({"doctype": doctype, name_field: value, **extra})
	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _ensure_customer_group() -> str:
	return _ensure_simple("Customer Group", "customer_group_name", "All Customer Groups")


def _ensure_supplier_group() -> str:
	return _ensure_simple("Supplier Group", "supplier_group_name", "All Supplier Groups")


def _ensure_item_group() -> str:
	return _ensure_simple("Item Group", "item_group_name", "All Item Groups")


def _ensure_territory() -> str:
	return _ensure_simple("Territory", "territory_name", "All Territories")


def _ensure_uom(uom: str = "Nos") -> str:
	return _ensure_simple("UOM", "uom_name", uom)


def _ensure_designation() -> str:
	return _ensure_simple("Designation", "designation_name", "Operations Executive")


def _ensure_department(company: str) -> str:
	existing = frappe.db.exists("Department", {"department_name": "Operations", "company": company})
	if existing:
		return existing
	doc = frappe.get_doc(
		{"doctype": "Department", "department_name": "Operations", "company": company}
	)
	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _ensure_gender() -> str:
	return _ensure_simple("Gender", "gender", "Male")


def _ensure_employee(company: str, designation: str, department: str) -> str:
	existing = frappe.db.exists("Employee", {"employee_name": "Aarav Sharma"})
	if existing:
		return existing

	gender = _ensure_gender()
	doc = frappe.get_doc(
		{
			"doctype": "Employee",
			"first_name": "Aarav",
			"last_name": "Sharma",
			"employee_name": "Aarav Sharma",
			"company": company,
			"status": "Active",
			"designation": designation,
			"department": department,
			"gender": gender,
			"date_of_birth": "1990-01-01",
			"date_of_joining": nowdate(),
			"personal_email": "seed.employee@example.com",
			"prefered_email": "seed.employee@example.com",
		}
	)
	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _ensure_warehouse(company: str) -> str:
	existing = frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
	if existing:
		return existing
	doc = frappe.get_doc(
		{"doctype": "Warehouse", "warehouse_name": "Main Warehouse", "company": company}
	)
	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _ensure_asset_category(company: str) -> str:
	existing = frappe.db.exists("Asset Category", {"asset_category_name": "Fixed Assets"})
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "Asset Category",
			"asset_category_name": "Fixed Assets",
			"company": company,
		}
	)
	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _ensure_salary_component() -> str:
	existing = frappe.db.exists("Salary Component", {"salary_component": "Basic"})
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "Salary Component",
			"salary_component": "Basic",
			"salary_component_abbr": "BASIC",
			"type": "Earning",
		}
	)
	_safe_insert(doc, ignore_mandatory=False, ignore_validate=False)
	return doc.name


def _ensure_salary_component_deduction() -> str:
	existing = frappe.db.exists("Salary Component", {"salary_component": "Professional Tax"})
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "Salary Component",
			"salary_component": "Professional Tax",
			"salary_component_abbr": "PT",
			"type": "Deduction",
		}
	)
	_safe_insert(doc, ignore_mandatory=False, ignore_validate=False)
	return doc.name


def _ensure_salary_structure(company: str, currency: str) -> str:
	existing = frappe.db.exists("Salary Structure", {"name": "Standard Salary Structure"})
	if existing:
		return existing
	component = _ensure_salary_component()
	doc = frappe.get_doc(
		{
			"doctype": "Salary Structure",
			"name": "Standard Salary Structure",
			"company": company,
			"is_active": "Yes",
			"currency": currency,
			"payroll_frequency": "Monthly",
			"earnings": [{"salary_component": component, "amount": 50000}],
		}
	)
	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _ensure_salary_structure_assignment(employee: str, company: str, salary_structure: str):
	existing = frappe.db.exists(
		"Salary Structure Assignment",
		{"employee": employee, "salary_structure": salary_structure},
	)
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "Salary Structure Assignment",
			"employee": employee,
			"salary_structure": salary_structure,
			"from_date": nowdate(),
			"company": company,
			"base": 50000,
		}
	)
	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _ensure_activity_type() -> str:
	return _ensure_simple("Activity Type", "activity_type", "Project Work")


def _ensure_crm_statuses():
	if _doctype_exists("CRM Lead Status"):
		_ensure_simple("CRM Lead Status", "lead_status", "New")
	if _doctype_exists("CRM Deal Status"):
		_ensure_simple("CRM Deal Status", "deal_status", "Qualification")


def _extract_nodes_from_svg(svg_path: str) -> list[dict]:
	nodes: list[dict] = []
	with open(svg_path, "r", encoding="utf-8") as handle:
		for line in handle:
			if "xlink:href" not in line:
				continue
			url_match = re.search(r'xlink:href="([^"]+)"', line)
			if not url_match:
				continue
			title_match = re.search(r'xlink:title="([^"]+)"', line)
			nodes.append(
				{
					"url": url_match.group(1),
					"label": title_match.group(1) if title_match else None,
					"node": None,
				}
			)
	return nodes


def _extract_nodes_from_dot(dot_path: str) -> list[dict]:
	nodes: list[dict] = []
	try:
		path_lower = dot_path.lower()
		if path_lower.endswith(".svg"):
			return _extract_nodes_from_svg(dot_path)

		with open(dot_path, "r", encoding="utf-8") as handle:
			for line in handle:
				if "URL=" not in line:
					continue
				url_match = re.search(r'URL="([^"]+)"', line)
				if not url_match:
					continue
				label_match = re.search(r'label="([^"]+)"', line)
				node_match = re.match(r"^\s*([A-Za-z0-9_]+)\s+\[", line)
				nodes.append(
					{
						"url": url_match.group(1),
						"label": label_match.group(1) if label_match else None,
						"node": node_match.group(1) if node_match else None,
					}
				)
	except FileNotFoundError:
		frappe.throw(_("Map file not found at {0}").format(dot_path))
	return nodes


def _single_has_value(doctype: str) -> bool:
	return bool(
		frappe.db.sql(
			"select value from `tabSingles` where doctype=%s limit 1",
			(doctype,),
		)
	)


def _titleize_route(route: str) -> str:
	parts = [p for p in route.split("-") if p]
	if not parts:
		return route
	head = parts[0].lower()
	if head == "crm":
		parts[0] = "CRM"
	elif head == "erpnext":
		parts[0] = "ERPNext"
	elif head == "hrms":
		parts[0] = "HRMS"
	elif head == "fcrm":
		parts[0] = "FCRM"
	return " ".join(p if p.isupper() else p.capitalize() for p in parts)


def _resolve_doctype(label: str | None, route: str | None) -> str | None:
	if label:
		label_map = {"Full And Final Statement": "Full and Final Statement"}
		if label in label_map and frappe.db.exists("DocType", label_map[label]):
			return label_map[label]
		if frappe.db.exists("DocType", label):
			return label

	if route:
		route = route.strip("/")
		route_map = {"full-and-final-statement": "Full and Final Statement"}
		if route in route_map and frappe.db.exists("DocType", route_map[route]):
			return route_map[route]
		frappe_crm_map = {
			"frappe-crm/leads": "CRM Lead",
			"frappe-crm/deals": "CRM Deal",
			"frappe-crm/contacts": "CRM Contacts",
			"frappe-crm/organizations": "CRM Organization",
			"frappe-crm/dashboard": None,
		}
		if route in frappe_crm_map:
			return frappe_crm_map[route]

		candidate = _titleize_route(route)
		if frappe.db.exists("DocType", candidate):
			return candidate

		if route.startswith("crm-"):
			candidate = "CRM " + _titleize_route(route[4:])
			if frappe.db.exists("DocType", candidate):
				return candidate

		if route.startswith("erpnext-"):
			candidate = "ERPNext " + _titleize_route(route[8:])
			if frappe.db.exists("DocType", candidate):
				return candidate

	if label:
		fallback = label.strip()
		if frappe.db.exists("DocType", fallback):
			return fallback

	return None


def _first_select_option(options: str | None) -> str | None:
	if not options:
		return None
	for option in options.split("\n"):
		option = option.strip()
		if option:
			return option
	return None


def _get_first_record(doctype: str) -> str | None:
	return frappe.db.get_value(doctype, {}, "name")


def _placeholder_value(field, prefix: str, index: int, depth: int):
	fieldtype = field.fieldtype
	if fieldtype in ("Data", "Small Text", "Text", "Long Text", "Text Editor", "HTML", "Code"):
		fieldname = (field.fieldname or "").lower()
		label = (field.label or "").lower()
		key = f"{fieldname} {label}"
		if "email" in key:
			return _rand_email()
		if "phone" in key or "mobile" in key or "contact" in key:
			return _rand_phone()
		if "first_name" in key or "firstname" in key:
			return _rand_choice(INDIA_FIRST_NAMES)
		if "last_name" in key or "lastname" in key:
			return _rand_choice(INDIA_LAST_NAMES)
		if "employee_name" in key or "employee" == fieldname:
			return _rand_full_name()
		if "company" in key and "company_name" in key:
			return _rand_company()
		if "company_name" in key:
			return _rand_company()
		if "organization" in key:
			return _rand_company()
		if "subject" in key or "title" in key:
			return _rand_subject()
		if "item_code" in key:
			return _rand_item_code()
		if "item_name" in key:
			return _rand_item_name()
		if "address" in key:
			return _rand_address()
		if "city" in key:
			return _rand_city_state()[0]
		if "state" in key:
			return _rand_city_state()[1]
		if "country" in key:
			return "India"
		if "pincode" in key or "pin" in key:
			return _rand_pincode()
		if "website" in key:
			return f"www.{_rand_company().lower().replace(' ', '')}.in"
		return _rand_sentence()
	if fieldtype in ("Int",):
		return random.randint(1, 10)
	if fieldtype in ("Float", "Currency", "Percent"):
		return random.randint(1000, 50000)
	if fieldtype == "Check":
		return random.choice([0, 1])
	if fieldtype == "Date":
		return _rand_date()
	if fieldtype == "Datetime":
		return f"{_rand_date()} 10:00:00"
	if fieldtype == "Time":
		return "09:00:00"
	if fieldtype == "Select":
		return _first_select_option(field.options)
	if fieldtype == "Link":
		target = field.options
		if not target:
			return None
		if field.parent == "Asset Maintenance" and field.fieldname == "asset_name":
			asset = frappe.db.get_value(
				"Asset",
				{
					"name": [
						"not in",
						frappe.get_all("Asset Maintenance", pluck="asset_name") or [""],
					]
				},
				"name",
			)
			if asset:
				return asset
		if field.parent == "Staffing Plan" and field.fieldname == "company":
			company = _get_default_company()
			if company:
				return company
		if field.parent == "Shift Assignment" and field.fieldname == "company":
			company = _get_default_company()
			if company:
				return company
		if field.parent == "Shift Request" and field.fieldname == "company":
			company = _get_default_company()
			if company:
				return company
		if field.parent == "Payroll Period" and field.fieldname == "company":
			company = _get_default_company()
			if company:
				return company
		value = _get_first_record(target)
		if value:
			return value
		if depth >= 2:
			return None
		value = _create_placeholder_doc(target, prefix, index, depth + 1)
		return value
	return None


def _create_placeholder_doc(doctype: str, prefix: str, index: int, depth: int = 0) -> str | None:
	if doctype == "Full and Final Statement":
		company = _get_default_company()
		designation = _ensure_designation()
		department = _ensure_department(company) if company else None
		employee = _ensure_employee(company, designation, department) if company and department else None
		if not employee:
			return None
		doc = frappe.get_doc(
			{
				"doctype": "Full and Final Statement",
				"employee": employee,
				"transaction_date": nowdate(),
			}
		)
		_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
		return doc.name

	meta = frappe.get_meta(doctype)
	autoname = (meta.autoname or "").strip()
	if meta.issingle:
		values_to_set: dict = {}
		for field in meta.fields:
			if field.reqd:
				value = _placeholder_value(field, prefix, index, depth)
				if value is not None:
					values_to_set[field.fieldname] = value
		if not values_to_set:
			for field in meta.fields:
				if field.fieldtype == "Select":
					option = _first_select_option(field.options)
					if option:
						values_to_set[field.fieldname] = option
						break
			if not values_to_set:
				for field in meta.fields:
					if field.fieldtype in ("Data", "Text", "Small Text"):
						values_to_set[field.fieldname] = f"{prefix} {doctype}"
						break
		for fieldname, value in values_to_set.items():
			frappe.db.set_single_value(doctype, fieldname, value)
		return doctype

	doc = frappe.new_doc(doctype)

	if autoname.lower() == "prompt" and not doc.name:
		doc.name = _compose_label(prefix, _rand_company(), index if prefix else None)
	elif autoname.startswith("field:"):
		fieldname = autoname.split("field:", 1)[1].strip()
		if fieldname and not doc.get(fieldname):
			doc.set(fieldname, _compose_label(prefix, _rand_company(), None))

	for field in meta.fields:
		if not field.reqd:
			continue
		if doc.get(field.fieldname):
			continue
		value = _placeholder_value(field, prefix, index, depth)
		if value is not None:
			doc.set(field.fieldname, value)

	# Populate required child tables with one row if still empty
	for field in meta.fields:
		if field.fieldtype != "Table" or not field.reqd:
			continue
		if doc.get(field.fieldname):
			continue
		child_doctype = field.options
		if not child_doctype:
			continue
		row = _build_child_row(child_doctype, prefix, index, depth + 1)
		if row:
			doc.set(field.fieldname, [row])

	# Minimal fallbacks for User if still missing email
	if doctype == "User" and not doc.get("email"):
		doc.set("email", _rand_email())
		if not doc.get("first_name"):
			doc.set("first_name", _rand_choice(INDIA_FIRST_NAMES))

	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _build_child_row(
	doctype: str,
	prefix: str,
	index: int,
	depth: int = 0,
	fill_all_fields: bool = False,
) -> dict:
	meta = frappe.get_meta(doctype)
	row: dict = {"doctype": doctype}
	for field in meta.fields:
		if field.fieldtype in ("Section Break", "Column Break", "Tab Break"):
			continue
		if not fill_all_fields and not field.reqd:
			continue
		value = _placeholder_value(field, prefix, index, depth)
		if value is not None:
			row[field.fieldname] = value
	return row


def _get_next_child_idx(child_doctype: str, parent: str, parenttype: str, parentfield: str) -> int:
	result = frappe.db.sql(
		f"""
			select max(idx) from `tab{child_doctype}`
			where parent=%s and parenttype=%s and parentfield=%s
		""",
		(parent, parenttype, parentfield),
	)
	max_idx = (result[0][0] if result else 0) or 0
	return int(max_idx) + 1


def _insert_child_row_direct(
	parent_doctype: str,
	parent_name: str,
	parentfield: str,
	child_doctype: str,
	prefix: str,
	index: int,
	depth: int = 0,
	fill_all_fields: bool = True,
) -> bool:
	row = _build_child_row(child_doctype, prefix, index, depth + 1, fill_all_fields=fill_all_fields)
	if not row:
		return False
	if child_doctype == "Maintenance Team Member":
		unused_user = _get_unused_maintenance_user()
		if not unused_user:
			return False
		row["team_member"] = unused_user
		row["maintenance_role"] = _get_default_role()
	if child_doctype == "Has Role":
		row["role"] = _get_default_role()
	if child_doctype == "Block Module":
		row["module"] = _get_default_module()
	if child_doctype == "User Email":
		email_account = _ensure_email_account()
		if not email_account:
			return False
		row["email_account"] = email_account
	if child_doctype == "DefaultValue":
		row.setdefault("defkey", "language")
		row.setdefault("defvalue", "en")
	if child_doctype == "User Social Login":
		row.setdefault("provider", "Google")
		row.setdefault("username", parent_name)
		row.setdefault("userid", parent_name)
	row.update(
		{
			"doctype": child_doctype,
			"parent": parent_name,
			"parenttype": parent_doctype,
			"parentfield": parentfield,
			"idx": _get_next_child_idx(child_doctype, parent_name, parent_doctype, parentfield),
		}
	)
	try:
		doc = frappe.get_doc(row)
		doc.flags.ignore_permissions = True
		doc.flags.ignore_validate = True
		doc.flags.ignore_mandatory = True
		doc.insert()
		return True
	except Exception:
		return False


def _get_default_role() -> str | None:
	for role in ("Maintenance User", "Manufacturing User", "System Manager", "HR User"):
		if frappe.db.exists("Role", role):
			return role
	return frappe.db.get_value("Role", {}, "name")


def _get_default_module() -> str | None:
	for module in ("CRM", "Accounts", "HR", "Assets", "Projects", "Selling"):
		if frappe.db.exists("Module Def", module):
			return module
	return frappe.db.get_value("Module Def", {}, "name")


def _ensure_email_account() -> str | None:
	if not _doctype_exists("Email Account"):
		return None
	existing = frappe.db.get_value("Email Account", {}, "name")
	if existing:
		return existing
	email_id = _rand_email("noreply", _rand_choice(COMPANY_PREFIXES))
	doc = frappe.get_doc(
		{
			"doctype": "Email Account",
			"email_id": email_id,
			"email_account_name": "No Reply",
			"enable_outgoing": 0,
			"enable_incoming": 0,
		}
	)
	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _get_unused_maintenance_user() -> str | None:
	used = set(
		frappe.db.sql_list("select team_member from `tabMaintenance Team Member`")
	)
	users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")
	for user in users:
		if user and user not in used and user != "Guest":
			return user
	# create a new user if needed
	email = _rand_email()
	doc = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": _rand_choice(INDIA_FIRST_NAMES),
			"last_name": _rand_choice(INDIA_LAST_NAMES),
			"send_welcome_email": 0,
		}
	)
	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _ensure_salary_structure_children(limit: int = 5):
	if not _doctype_exists("Salary Structure"):
		return
	earning_component = _ensure_salary_component()
	deduction_component = _ensure_salary_component_deduction()
	structures = frappe.get_all("Salary Structure", pluck="name", limit=limit)
	for name in structures:
		doc = frappe.get_doc("Salary Structure", name)
		updated = False

		if not doc.get("earnings"):
			doc.append(
				"earnings",
				{
					"salary_component": earning_component,
					"amount": 50000,
				},
			)
			updated = True

		if not doc.get("deductions"):
			doc.append(
				"deductions",
				{
					"salary_component": deduction_component,
					"amount": 2000,
				},
			)
			updated = True

		if updated:
			doc.flags.ignore_permissions = True
			doc.flags.ignore_validate = True
			doc.flags.ignore_mandatory = True
			doc.save()


def _ensure_child_tables(doc, prefix: str, index: int, depth: int = 0, required_only: bool = False) -> bool:
	"""Ensure table fields on a document have at least one row."""
	meta = doc.meta
	updated = False
	for field in meta.fields:
		if field.fieldtype != "Table":
			continue
		if required_only and not field.reqd:
			continue
		if doc.get(field.fieldname):
			continue
		child_doctype = field.options
		if not child_doctype:
			continue
		row = _build_child_row(child_doctype, prefix, index, depth + 1, fill_all_fields=not required_only)
		if row:
			doc.set(field.fieldname, [row])
			updated = True
	return updated


@frappe.whitelist()
def audit_full_system_map(dot_path: str = "/tmp/full_system_map_linked.dot"):
	"""Audit SVG/DOT nodes against actual DocTypes and record counts."""
	nodes = _extract_nodes_from_dot(dot_path)
	doctypes: dict[str, dict] = {}
	unmapped: list[dict] = []

	for node in nodes:
		url = node.get("url")
		label = node.get("label")
		route = None
		if url and "/app/" in url:
			route = url.split("/app/", 1)[1]
		doctype = _resolve_doctype(label, route)
		if doctype:
			doctypes[doctype] = {"label": label, "route": route}
		else:
			unmapped.append(node)

	counts: dict[str, int] = {}
	empty: list[str] = []
	for doctype in sorted(doctypes.keys()):
		try:
			meta = frappe.get_meta(doctype)
			if meta.issingle:
				count = 1 if _single_has_value(doctype) else 0
			else:
				count = frappe.db.count(doctype)
		except Exception:
			count = 0
		counts[doctype] = count
		if count == 0:
			empty.append(doctype)

	return {
		"total_nodes": len(nodes),
		"mapped_doctypes": len(doctypes),
		"empty_doctypes": empty,
		"counts": counts,
		"unmapped_nodes": unmapped,
	}


@frappe.whitelist()
def audit_child_tables_for_map(
	map_path: str = "/tmp/full_system_map_linked.svg",
	records_per_doctype: int = 5,
):
	"""Audit child table coverage for doctypes in the SVG/DOT map."""
	nodes = _extract_nodes_from_dot(map_path)
	doctypes: list[str] = []
	for node in nodes:
		url = node.get("url")
		label = node.get("label")
		route = None
		if url and "/app/" in url:
			route = url.split("/app/", 1)[1]
		doctype = _resolve_doctype(label, route)
		if doctype and doctype not in doctypes:
			doctypes.append(doctype)

	try:
		limit = int(records_per_doctype)
	except Exception:
		limit = 5
	limit = max(1, limit)

	missing: dict[str, list[str]] = {}
	for doctype in doctypes:
		try:
			meta = frappe.get_meta(doctype)
			table_fields = [f.fieldname for f in meta.fields if f.fieldtype == "Table"]
			if not table_fields:
				continue

			if meta.issingle:
				doc = frappe.get_doc(doctype)
				for fieldname in table_fields:
					if not doc.get(fieldname):
						missing.setdefault(doctype, []).append(fieldname)
				continue

			names = frappe.get_all(doctype, pluck="name", limit=limit)
			for name in names:
				doc = frappe.get_doc(doctype, name)
				for fieldname in table_fields:
					if not doc.get(fieldname):
						missing.setdefault(doctype, []).append(fieldname)
		except Exception:
			continue

	return {"missing_child_tables": missing, "status": "ok"}


@frappe.whitelist()
def fill_full_system_map(
	records_per_doctype: int = 5,
	dot_path: str = "/tmp/full_system_map_linked.dot",
	name_prefix: str = "",
):
	"""Ensure every SVG/DOT node has at least N records."""
	frappe.flags.mute_emails = True

	try:
		target = int(records_per_doctype)
	except Exception:
		target = 5
	target = max(1, target)
	prefix = str(name_prefix or "").strip()

	nodes = _extract_nodes_from_dot(dot_path)
	doctypes: list[str] = []
	for node in nodes:
		url = node.get("url")
		label = node.get("label")
		route = None
		if url and "/app/" in url:
			route = url.split("/app/", 1)[1]
		doctype = _resolve_doctype(label, route)
		if doctype and doctype not in doctypes:
			doctypes.append(doctype)

	errors: list[str] = []
	skipped: list[str] = []
	min_target_overrides = {"Company": 1}
	for doctype in doctypes:
		try:
			meta = frappe.get_meta(doctype)
			if meta.issingle:
				_create_placeholder_doc(doctype, prefix, 1, 0)
				continue

			count = frappe.db.count(doctype)
			min_target = min_target_overrides.get(doctype, target)
			if count >= min_target:
				continue
			for i in range(count + 1, min_target + 1):
				_create_placeholder_doc(doctype, prefix, i, 0)
		except Exception as exc:
			message = str(exc)
			if "doesn't exist" in message or "does not exist" in message:
				skipped.append(doctype)
				continue
			errors.append(f"{doctype}: {exc}")

	frappe.db.commit()
	return {"target": target, "errors": errors, "skipped": skipped, "status": "ok"}


@frappe.whitelist()
def fill_child_tables_for_map(
	records_per_doctype: int = 5,
	map_path: str = "/tmp/full_system_map_linked.svg",
	required_only: bool = False,
):
	"""Ensure all table fields for doctypes in the map have at least one row."""
	nodes = _extract_nodes_from_dot(map_path)
	doctypes: list[str] = []
	for node in nodes:
		url = node.get("url")
		label = node.get("label")
		route = None
		if url and "/app/" in url:
			route = url.split("/app/", 1)[1]
		doctype = _resolve_doctype(label, route)
		if doctype and doctype not in doctypes:
			doctypes.append(doctype)

	try:
		limit = int(records_per_doctype)
	except Exception:
		limit = 5
	limit = max(1, limit)

	updated = {}
	for doctype in doctypes:
		try:
			meta = frappe.get_meta(doctype)
			if not any(f.fieldtype == "Table" for f in meta.fields):
				continue

			if meta.issingle:
				doc = frappe.get_doc(doctype)
				for field in meta.fields:
					if field.fieldtype != "Table":
						continue
					if required_only and not field.reqd:
						continue
					if doc.get(field.fieldname):
						continue
					if _insert_child_row_direct(
						doctype,
						doctype,
						field.fieldname,
						field.options,
						"",
						1,
						0,
						fill_all_fields=not required_only,
					):
						updated[doctype] = updated.get(doctype, 0) + 1
				continue

			names = frappe.get_all(doctype, pluck="name", limit=limit)
			for idx, name in enumerate(names, start=1):
				doc = frappe.get_doc(doctype, name)
				for field in meta.fields:
					if field.fieldtype != "Table":
						continue
					if required_only and not field.reqd:
						continue
					if doc.get(field.fieldname):
						continue
					if _insert_child_row_direct(
						doctype,
						doc.name,
						field.fieldname,
						field.options,
						"",
						idx,
						0,
						fill_all_fields=not required_only,
					):
						updated[doctype] = updated.get(doctype, 0) + 1
		except Exception:
			continue

	frappe.db.commit()
	_ensure_salary_structure_children(limit=limit)
	frappe.db.commit()
	return {"updated": updated, "status": "ok"}


@frappe.whitelist()
def debug_doctype(doctype: str):
	meta = frappe.get_meta(doctype)
	return {
		"issingle": meta.issingle,
		"autoname": meta.autoname,
	}


@frappe.whitelist()
def touch_fcrm_settings():
	frappe.db.set_single_value("FCRM Settings", "brand_name", "CRM")
	return True


@frappe.whitelist()
def fix_fcrm_settings_service_provider():
	frappe.db.set_single_value("FCRM Settings", "service_provider", "frankfurter.app")
	frappe.db.commit()
	return True


def _create_customers(count: int, customer_group: str, territory: str):
	created = 0
	attempts = 0
	while created < count and attempts < count * 3:
		attempts += 1
		name = _rand_company()
		if frappe.db.exists("Customer", {"customer_name": name}):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": name,
				"customer_group": customer_group,
				"territory": territory,
			}
		)
		_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
		created += 1


def _create_suppliers(count: int, supplier_group: str):
	created = 0
	attempts = 0
	while created < count and attempts < count * 3:
		attempts += 1
		name = _rand_company()
		if frappe.db.exists("Supplier", {"supplier_name": name}):
			continue
		doc = frappe.get_doc(
			{"doctype": "Supplier", "supplier_name": name, "supplier_group": supplier_group}
		)
		_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
		created += 1


def _create_items(count: int, item_group: str, uom: str, asset_category: str):
	created = 0
	attempts = 0
	while created < count and attempts < count * 4:
		attempts += 1
		code = _rand_item_code()
		if frappe.db.exists("Item", {"item_code": code}):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": code,
				"item_name": _rand_item_name(),
				"item_group": item_group,
				"stock_uom": uom,
				"is_stock_item": 0,
				"is_sales_item": 1,
				"is_purchase_item": 1,
				"is_fixed_asset": 1,
				"asset_category": asset_category,
			}
		)
		_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
		created += 1


def _create_assets(company: str, count: int, asset_category: str):
	items = frappe.get_all(
		"Item",
		filters={"is_fixed_asset": 1},
		fields=["item_code", "item_name"],
		limit=count,
	)
	if not items:
		return
	for i, item in enumerate(items, start=1):
		name = f"{item.item_name} - {random.randint(1, 50)}"
		if frappe.db.exists("Asset", {"asset_name": name}):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Asset",
				"asset_name": name,
				"item_code": item.item_code,
				"asset_category": asset_category,
				"company": company,
				"available_for_use_date": nowdate(),
				"purchase_amount": 100000,
				"net_purchase_amount": 100000,
			}
		)
		_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)


def _create_projects(company: str, employee: str, count: int):
	activity_type = _ensure_activity_type()
	for i in range(1, count + 1):
		project_name = _rand_choice(PROJECT_NAMES)
		project = frappe.db.exists("Project", {"project_name": project_name})
		if not project:
			project_doc = frappe.get_doc(
				{"doctype": "Project", "project_name": project_name, "company": company}
			)
			_safe_insert(project_doc, ignore_mandatory=True, ignore_validate=True)
			project = project_doc.name

		task_subject = _rand_choice(TASK_NAMES)
		task = frappe.db.exists("Task", {"subject": task_subject})
		if not task:
			task_doc = frappe.get_doc(
				{
					"doctype": "Task",
					"subject": task_subject,
					"project": project,
					"status": "Open",
				}
			)
			_safe_insert(task_doc, ignore_mandatory=True, ignore_validate=True)
			task = task_doc.name

		ts_doc = frappe.get_doc(
			{
				"doctype": "Timesheet",
				"employee": employee,
				"company": company,
				"time_logs": [
					{
						"activity_type": activity_type,
						"from_time": f"{nowdate()} 09:00:00",
						"to_time": f"{nowdate()} 11:00:00",
						"hours": 2,
						"task": task,
						"project": project,
					}
				],
			}
		)
		_safe_insert(ts_doc, ignore_mandatory=True, ignore_validate=True)


def _create_hr(company: str, employee: str, designation: str, count: int):
	for i in range(1, count + 1):
		applicant_name = _rand_full_name()
		if not frappe.db.exists("Job Applicant", {"applicant_name": applicant_name}):
			app_doc = frappe.get_doc(
				{
					"doctype": "Job Applicant",
					"applicant_name": applicant_name,
					"email_id": _rand_email(applicant_name),
					"status": "Open",
					"designation": designation,
				}
			)
			_safe_insert(app_doc, ignore_mandatory=True, ignore_validate=True)

		app_name = frappe.db.get_value("Job Applicant", {"applicant_name": applicant_name}, "name")
		if app_name and _doctype_exists("Job Offer"):
			if not frappe.db.exists("Job Offer", {"job_applicant": app_name, "status": "Accepted"}):
				offer_doc = frappe.get_doc(
					{
						"doctype": "Job Offer",
						"job_applicant": app_name,
						"company": company,
						"designation": designation,
						"offer_date": nowdate(),
						"status": "Accepted",
					}
				)
				_safe_insert(offer_doc, ignore_mandatory=True, ignore_validate=True)
				_safe_submit(offer_doc, ignore_validate=True)

	leave_type = _ensure_simple("Leave Type", "leave_type_name", "Annual Leave")
	holiday_list = frappe.db.exists("Holiday List", {"holiday_list_name": "Default Holiday List"})
	if not holiday_list:
		holiday_doc = frappe.get_doc(
			{
				"doctype": "Holiday List",
				"holiday_list_name": "Default Holiday List",
				"company": company,
				"holidays": [
					{
						"holiday_date": nowdate(),
						"description": "Holiday",
					}
				],
			}
		)
		_safe_insert(holiday_doc, ignore_mandatory=True, ignore_validate=True)
		holiday_list = holiday_doc.name

	alloc = frappe.db.exists(
		"Leave Allocation",
		{"employee": employee, "leave_type": leave_type, "from_date": nowdate()},
	)
	if not alloc:
		alloc_doc = frappe.get_doc(
			{
				"doctype": "Leave Allocation",
				"employee": employee,
				"leave_type": leave_type,
				"from_date": nowdate(),
				"to_date": add_months(nowdate(), 12),
				"new_leaves_allocated": 12,
			}
		)
		_safe_insert(alloc_doc, ignore_mandatory=True, ignore_validate=True)

	if not frappe.db.exists(
		"Leave Application",
		{"employee": employee, "leave_type": leave_type, "from_date": nowdate()},
	):
		leave_doc = frappe.get_doc(
			{
				"doctype": "Leave Application",
				"employee": employee,
				"leave_type": leave_type,
				"from_date": nowdate(),
				"to_date": add_days(nowdate(), 1),
				"status": "Open",
			}
		)
		_safe_insert(leave_doc, ignore_mandatory=True, ignore_validate=True)

	if not frappe.db.exists("Attendance", {"employee": employee, "attendance_date": nowdate()}):
		att_doc = frappe.get_doc(
			{
				"doctype": "Attendance",
				"employee": employee,
				"attendance_date": nowdate(),
				"status": "Present",
			}
		)
		_safe_insert(att_doc, ignore_mandatory=True, ignore_validate=True)


def _create_payroll(company: str, employee: str):
	currency = _get_company_currency(company) or "INR"
	salary_structure = _ensure_salary_structure(company, currency)
	_ensure_salary_structure_assignment(employee, company, salary_structure)

	if not frappe.db.exists("Salary Slip", {"employee": employee, "start_date": nowdate()}):
		slip_doc = frappe.get_doc(
			{
				"doctype": "Salary Slip",
				"employee": employee,
				"company": company,
				"salary_structure": salary_structure,
				"posting_date": nowdate(),
				"start_date": nowdate(),
				"end_date": add_months(nowdate(), 1),
			}
		)
		_safe_insert(slip_doc, ignore_mandatory=True, ignore_validate=True)


def _create_accounting(company: str):
	accounts = frappe.get_all(
		"Account",
		filters={
			"company": company,
			"is_group": 0,
			"account_type": ["in", ["Cash", "Bank"]],
		},
		fields=["name"],
		limit=2,
	)
	if len(accounts) < 2:
		accounts = frappe.get_all(
			"Account",
			filters={"company": company, "is_group": 0},
			fields=["name"],
			limit=2,
		)
	if len(accounts) < 2:
		return

	if not frappe.db.exists("Journal Entry", {"title": "Journal Entry"}):
		je_doc = frappe.get_doc(
			{
				"doctype": "Journal Entry",
				"title": "Journal Entry",
				"company": company,
				"posting_date": nowdate(),
				"accounts": [
					{"account": accounts[0].name, "debit_in_account_currency": 1000},
					{"account": accounts[1].name, "credit_in_account_currency": 1000},
				],
			}
		)
		_safe_insert(je_doc, ignore_mandatory=True, ignore_validate=True)


def _create_crm(company: str, count: int):
	_ensure_crm_statuses()

	if _doctype_exists("CRM Lead"):
		for i in range(1, count + 1):
			lead_name = _rand_full_name()
			if not frappe.db.exists("CRM Lead", {"lead_name": lead_name}):
				lead_doc = frappe.get_doc(
					{
						"doctype": "CRM Lead",
						"first_name": lead_name.split(" ", 1)[0],
						"last_name": lead_name.split(" ", 1)[1] if " " in lead_name else "",
						"lead_name": lead_name,
						"status": "New",
						"email": _rand_email(lead_name),
					}
				)
				_safe_insert(lead_doc, ignore_mandatory=True, ignore_validate=True)
			lead = frappe.db.get_value("CRM Lead", {"lead_name": lead_name}, "name")
			if lead and _doctype_exists("CRM Deal"):
				if not frappe.db.exists("CRM Deal", {"lead": lead}):
					deal_doc = frappe.get_doc(
						{
							"doctype": "CRM Deal",
							"status": "Qualification",
							"lead": lead,
							"organization_name": _rand_company(),
						}
					)
					_safe_insert(deal_doc, ignore_mandatory=True, ignore_validate=True)

		if _doctype_exists("CRM Task"):
			if not frappe.db.exists("CRM Task", {"title": "Call Follow-up"}):
				task_doc = frappe.get_doc(
					{"doctype": "CRM Task", "title": "Call Follow-up", "status": "Todo"}
				)
				_safe_insert(task_doc, ignore_mandatory=True, ignore_validate=True)
		return

	# ERPNext CRM fallback
	if _doctype_exists("Lead"):
		for i in range(1, count + 1):
			lead_name = _rand_full_name()
			if not frappe.db.exists("Lead", {"lead_name": lead_name}):
				lead_doc = frappe.get_doc(
					{
						"doctype": "Lead",
						"lead_name": lead_name,
						"company_name": _rand_company(),
						"email_id": _rand_email(lead_name),
						"status": "Lead",
					}
				)
				_safe_insert(lead_doc, ignore_mandatory=True, ignore_validate=True)


def _bulk_delete(doctype: str, filters: dict) -> int:
	if not _doctype_exists(doctype):
		return 0
	names = frappe.get_all(doctype, filters=filters, pluck="name")
	deleted = 0
	for name in names:
		try:
			frappe.delete_doc(doctype, name, ignore_permissions=True, force=1)
			deleted += 1
		except Exception:
			continue
	return deleted


@frappe.whitelist()
def purge_seed_data():
	"""Remove older seeded data (Seed/Demo prefixes) before repopulating."""
	deleted: dict[str, int] = {}

	deleted["Customer"] = _bulk_delete("Customer", {"customer_name": ["like", "Seed %"]})
	deleted["Supplier"] = _bulk_delete("Supplier", {"supplier_name": ["like", "Seed %"]})
	deleted["Item"] = _bulk_delete("Item", {"item_code": ["like", "SEED-ITEM-%"]})
	deleted["ItemName"] = _bulk_delete("Item", {"item_name": ["like", "Seed %"]})
	deleted["Asset"] = _bulk_delete("Asset", {"asset_name": ["like", "Seed %"]})
	deleted["Project"] = _bulk_delete("Project", {"project_name": ["like", "Seed %"]})
	deleted["Task"] = _bulk_delete("Task", {"subject": ["like", "Seed %"]})
	deleted["Job Applicant"] = _bulk_delete("Job Applicant", {"applicant_name": ["like", "Seed %"]})
	deleted["Leave Type"] = _bulk_delete("Leave Type", {"leave_type_name": ["like", "Seed %"]})
	deleted["Holiday List"] = _bulk_delete("Holiday List", {"holiday_list_name": ["like", "Seed %"]})
	deleted["Salary Component"] = _bulk_delete(
		"Salary Component", {"salary_component": ["like", "Seed %"]}
	)
	deleted["Salary Structure"] = _bulk_delete("Salary Structure", {"name": ["like", "Seed %"]})
	deleted["Designation"] = _bulk_delete("Designation", {"designation_name": ["like", "Seed %"]})
	deleted["Department"] = _bulk_delete("Department", {"department_name": ["like", "Seed %"]})
	deleted["Warehouse"] = _bulk_delete("Warehouse", {"warehouse_name": ["like", "Seed %"]})
	deleted["Asset Category"] = _bulk_delete(
		"Asset Category", {"asset_category_name": ["like", "Seed %"]}
	)
	deleted["Activity Type"] = _bulk_delete("Activity Type", {"activity_type": ["like", "Seed %"]})
	deleted["CRM Lead"] = _bulk_delete("CRM Lead", {"lead_name": ["like", "Seed %"]})
	deleted["CRM Deal"] = _bulk_delete("CRM Deal", {"organization_name": ["like", "Seed %"]})
	deleted["CRM Task"] = _bulk_delete("CRM Task", {"title": ["like", "Seed %"]})
	deleted["Lead"] = _bulk_delete("Lead", {"lead_name": ["like", "Seed %"]})
	deleted["LeadCompany"] = _bulk_delete("Lead", {"company_name": ["like", "Seed %"]})
	deleted["Journal Entry"] = _bulk_delete("Journal Entry", {"title": ["like", "Seed %"]})

	seed_employees = []
	if _doctype_exists("Employee"):
		seed_employees = frappe.get_all(
			"Employee",
			filters={"employee_name": ["like", "Seed %"]},
			pluck="name",
		)
		if frappe.db.exists("Employee", {"employee_name": "Employee 1"}):
			seed_employees += frappe.get_all(
				"Employee",
				filters={"employee_name": "Employee 1"},
				pluck="name",
			)

	if seed_employees:
		employee_filter = {"employee": ["in", seed_employees]}
		deleted["Salary Slip"] = _bulk_delete("Salary Slip", employee_filter)
		deleted["Salary Structure Assignment"] = _bulk_delete("Salary Structure Assignment", employee_filter)
		deleted["Leave Allocation"] = _bulk_delete("Leave Allocation", employee_filter)
		deleted["Leave Application"] = _bulk_delete("Leave Application", employee_filter)
		deleted["Attendance"] = _bulk_delete("Attendance", employee_filter)
		deleted["Timesheet"] = _bulk_delete("Timesheet", employee_filter)
		deleted["Employee"] = _bulk_delete("Employee", {"name": ["in", seed_employees]})

	job_applicants = []
	if _doctype_exists("Job Applicant"):
		job_applicants = frappe.get_all(
			"Job Applicant",
			filters={"applicant_name": ["like", "Seed %"]},
			pluck="name",
		)
	if job_applicants:
		deleted["Job Offer"] = _bulk_delete("Job Offer", {"job_applicant": ["in", job_applicants]})

	frappe.db.commit()
	return {"deleted": deleted, "status": "ok"}


def _doc_has_banned(doc) -> bool:
	if _has_banned(doc.name):
		return True
	for field in doc.meta.fields:
		if field.fieldtype not in (
			"Data",
			"Small Text",
			"Text",
			"Long Text",
			"Text Editor",
			"Email",
			"Autocomplete",
		):
			continue
		value = doc.get(field.fieldname)
		if isinstance(value, str) and _has_banned(value):
			return True
	return False


@frappe.whitelist()
def purge_banned_words_in_map(map_path: str = "/tmp/full_system_map_linked.svg"):
	"""Delete records containing banned words and scrub singles."""
	nodes = _extract_nodes_from_dot(map_path)
	doctypes: list[str] = []
	for node in nodes:
		url = node.get("url")
		label = node.get("label")
		route = None
		if url and "/app/" in url:
			route = url.split("/app/", 1)[1]
		doctype = _resolve_doctype(label, route)
		if doctype and doctype not in doctypes:
			doctypes.append(doctype)

	skip_doctypes = {
		"Role",
		"Module Def",
		"DocType",
		"System Settings",
		"Global Defaults",
		"User",
		"Company",
	}
	removed: dict[str, int] = {}
	updated: dict[str, int] = {}

	for doctype in doctypes:
		if doctype in skip_doctypes:
			continue
		try:
			meta = frappe.get_meta(doctype)
			if meta.issingle:
				doc = frappe.get_doc(doctype)
				changed = False
				for field in meta.fields:
					if field.fieldtype not in (
						"Data",
						"Small Text",
						"Text",
						"Long Text",
						"Text Editor",
						"Email",
						"Autocomplete",
					):
						continue
					value = doc.get(field.fieldname)
					if isinstance(value, str) and _has_banned(value):
						doc.set(field.fieldname, _placeholder_value(field, "", 1, 0))
						changed = True
				if changed:
					doc.flags.ignore_permissions = True
					doc.flags.ignore_validate = True
					doc.flags.ignore_mandatory = True
					doc.save()
					updated[doctype] = updated.get(doctype, 0) + 1
				continue

			names = frappe.get_all(doctype, pluck="name")
			for name in names:
				doc = frappe.get_doc(doctype, name)
				if _doc_has_banned(doc):
					try:
						frappe.delete_doc(doctype, name, ignore_permissions=True, force=1)
						removed[doctype] = removed.get(doctype, 0) + 1
					except Exception:
						continue
		except Exception:
			continue

	frappe.db.commit()
	return {"removed": removed, "updated": updated, "status": "ok"}


@frappe.whitelist()
def seed_full_system(records_per_doctype: int = 5):
	"""Seed realistic-looking sample data across core modules."""
	frappe.flags.mute_emails = True

	try:
		count = int(records_per_doctype) if records_per_doctype else 5
	except Exception:
		count = 5
	count = max(1, count)

	company = _get_default_company()
	if not company:
		frappe.throw(_("No company found. Please complete setup first."))

	customer_group = _ensure_customer_group()
	supplier_group = _ensure_supplier_group()
	item_group = _ensure_item_group()
	territory = _ensure_territory()
	uom = _ensure_uom("Nos")
	designation = _ensure_designation()
	department = _ensure_department(company)
	employee = _ensure_employee(company, designation, department)
	_ensure_warehouse(company)
	asset_category = _ensure_asset_category(company)

	_create_customers(count, customer_group, territory)
	_create_suppliers(count, supplier_group)
	_create_items(count, item_group, uom, asset_category)
	_create_assets(company, count, asset_category)
	_create_projects(company, employee, count)
	_create_hr(company, employee, designation, count)
	_create_payroll(company, employee)
	_create_accounting(company)
	_create_crm(company, count)

	frappe.db.commit()
	return {
		"company": company,
		"records_per_doctype": count,
		"status": "ok",
	}


@frappe.whitelist()
def replace_with_realistic_data(
	records_per_doctype: int = 5,
	map_path: str = "/tmp/full_system_map_linked.svg",
):
	"""Delete older seeded records and repopulate with realistic data."""
	purge_seed_data()
	purge_banned_words_in_map(map_path=map_path)
	seed_full_system(records_per_doctype=records_per_doctype)

	path = map_path
	if not path or not isinstance(path, str):
		path = "/tmp/full_system_map_linked.svg"
	if not os.path.exists(path):
		alt = "/tmp/full_system_map_linked.dot"
		if os.path.exists(alt):
			path = alt

	fill_full_system_map(records_per_doctype=records_per_doctype, dot_path=path, name_prefix="")
	fill_child_tables_for_map(records_per_doctype=records_per_doctype, map_path=path, required_only=False)
	purge_banned_words_in_map(map_path=path)
	fill_full_system_map(records_per_doctype=records_per_doctype, dot_path=path, name_prefix="")
	fill_child_tables_for_map(records_per_doctype=records_per_doctype, map_path=path, required_only=False)
	return {"status": "ok", "map_path": path, "records_per_doctype": records_per_doctype}


@frappe.whitelist()
def set_hr_only_workspaces():
	"""Hide all workspaces except HR and restrict HR workspace to HR roles."""
	if not _doctype_exists("Workspace"):
		return {"status": "skipped", "reason": "Workspace doctype not found"}

	keep_roles = ["HR User", "HR Manager", "System Manager"]
	hr_roles = [r for r in keep_roles if frappe.db.exists("Role", r)]

	updated = {"hidden": 0, "visible": 0}
	for name in frappe.get_all("Workspace", pluck="name"):
		try:
			ws = frappe.get_doc("Workspace", name)
			is_hr = ws.module == "HR" or ws.name == "HR" or ws.label == "HR"
			if is_hr:
				ws.is_hidden = 0
				if hr_roles:
					ws.roles = [{"role": role} for role in hr_roles]
				ws.save(ignore_permissions=True)
				updated["visible"] += 1
			else:
				ws.is_hidden = 1
				ws.save(ignore_permissions=True)
				updated["hidden"] += 1
		except Exception:
			continue

	frappe.db.commit()
	return {"status": "ok", "updated": updated}


def _ensure_property_setter(
	doctype: str,
	fieldname: str,
	property_name: str,
	value,
	property_type: str = "Check",
	doctype_or_field: str = "DocField",
):
	filters = {
		"doc_type": doctype,
		"field_name": fieldname,
		"property": property_name,
	}
	existing = frappe.db.exists("Property Setter", filters)
	if existing:
		doc = frappe.get_doc("Property Setter", existing)
		changed = False
		if doc.doctype_or_field != doctype_or_field:
			doc.doctype_or_field = doctype_or_field
			changed = True
		if str(doc.value) != str(value):
			doc.value = value
			changed = True
		if doc.property_type != property_type:
			doc.property_type = property_type
			changed = True
		if changed:
			doc.save(ignore_permissions=True)
		return existing
	doc = frappe.get_doc(
		{
			"doctype": "Property Setter",
			"doc_type": doctype,
			"field_name": fieldname,
			"property": property_name,
			"value": value,
			"property_type": property_type,
			"doctype_or_field": doctype_or_field,
		}
	)
	_safe_insert(doc, ignore_mandatory=True, ignore_validate=True)
	return doc.name


def _force_docfield_set_only_once(doctype: str, fieldname: str, value: int = 0):
	docfield = frappe.db.exists("DocField", {"parent": doctype, "fieldname": fieldname})
	if not docfield:
		return False
	frappe.db.set_value("DocField", docfield, "set_only_once", value)
	return True


@frappe.whitelist()
def allow_interview_time_edit():
	"""Allow updating Interview Schedule/From/To Time/Status even after initial save."""
	if not _doctype_exists("Interview"):
		return {"status": "skipped", "reason": "Interview doctype not found"}
	frappe.db.delete(
		"Property Setter",
		{
			"doc_type": "Interview",
			"field_name": ["in", ["scheduled_on", "from_time", "to_time", "status"]],
			"property": ["in", ["set_only_once", "allow_on_submit"]],
			"value": ["in", [1, 0]],
		},
	)
	_ensure_property_setter("Interview", "status", "allow_on_submit", 1, "Check", "DocField")
	_ensure_property_setter("Interview", "scheduled_on", "set_only_once", 0, "Check", "DocField")
	_ensure_property_setter("Interview", "from_time", "set_only_once", 0, "Check", "DocField")
	_ensure_property_setter("Interview", "to_time", "set_only_once", 0, "Check", "DocField")
	_ensure_property_setter("Interview", "scheduled_on", "allow_on_submit", 1, "Check", "DocField")
	_ensure_property_setter("Interview", "from_time", "allow_on_submit", 1, "Check", "DocField")
	_ensure_property_setter("Interview", "to_time", "allow_on_submit", 1, "Check", "DocField")
	_force_docfield_set_only_once("Interview", "scheduled_on", 0)
	_force_docfield_set_only_once("Interview", "from_time", 0)
	_force_docfield_set_only_once("Interview", "to_time", 0)
	frappe.db.set_value("DocField", {"parent": "Interview", "fieldname": "status"}, "allow_on_submit", 1)
	frappe.db.set_value("DocField", {"parent": "Interview", "fieldname": "scheduled_on"}, "allow_on_submit", 1)
	frappe.db.set_value("DocField", {"parent": "Interview", "fieldname": "from_time"}, "allow_on_submit", 1)
	frappe.db.set_value("DocField", {"parent": "Interview", "fieldname": "to_time"}, "allow_on_submit", 1)
	frappe.db.commit()
	frappe.clear_cache(doctype="Interview")
	return {"status": "ok"}


@frappe.whitelist()
def diagnose_interview_time_edit():
	if not _doctype_exists("Interview"):
		return {"status": "skipped", "reason": "Interview doctype not found"}
	db_scheduled = frappe.db.get_value(
		"DocField",
		{"parent": "Interview", "fieldname": "scheduled_on"},
		["set_only_once", "allow_on_submit", "fieldtype", "read_only"],
		as_dict=True,
	)
	db_from = frappe.db.get_value(
		"DocField",
		{"parent": "Interview", "fieldname": "from_time"},
		["set_only_once", "allow_on_submit", "fieldtype", "read_only"],
		as_dict=True,
	)
	db_to = frappe.db.get_value(
		"DocField",
		{"parent": "Interview", "fieldname": "to_time"},
		["set_only_once", "allow_on_submit", "fieldtype", "read_only"],
		as_dict=True,
	)
	meta = frappe.get_meta("Interview", cached=False)
	meta_scheduled = meta.get_field("scheduled_on")
	meta_from = meta.get_field("from_time")
	meta_to = meta.get_field("to_time")
	ps = frappe.get_all(
		"Property Setter",
		filters={
			"doc_type": "Interview",
			"field_name": ["in", ["scheduled_on", "from_time", "to_time"]],
		},
		fields=[
			"name",
			"doctype_or_field",
			"doc_type",
			"field_name",
			"property",
			"value",
			"property_type",
		],
	)
	return {
		"status": "ok",
		"db_scheduled": db_scheduled,
		"db_from": db_from,
		"db_to": db_to,
		"meta_scheduled": {
			"set_only_once": meta_scheduled.set_only_once if meta_scheduled else None,
			"allow_on_submit": meta_scheduled.allow_on_submit if meta_scheduled else None,
			"read_only": meta_scheduled.read_only if meta_scheduled else None,
			"fieldtype": meta_scheduled.fieldtype if meta_scheduled else None,
		},
		"meta_from": {
			"set_only_once": meta_from.set_only_once if meta_from else None,
			"allow_on_submit": meta_from.allow_on_submit if meta_from else None,
			"read_only": meta_from.read_only if meta_from else None,
			"fieldtype": meta_from.fieldtype if meta_from else None,
		},
		"meta_to": {
			"set_only_once": meta_to.set_only_once if meta_to else None,
			"allow_on_submit": meta_to.allow_on_submit if meta_to else None,
			"read_only": meta_to.read_only if meta_to else None,
			"fieldtype": meta_to.fieldtype if meta_to else None,
		},
		"property_setters": ps,
	}


@frappe.whitelist()
def fix_leave_allocations(
	from_date: str | None = None,
	to_date: str | None = None,
	leaves_allocated: float | None = None,
):
	"""Ensure leave allocations cover a wide date range for all employees."""
	if not _doctype_exists("Leave Allocation") or not _doctype_exists("Employee"):
		return {"status": "skipped", "reason": "Leave Allocation or Employee doctype not found"}

	from_date = from_date or "2000-01-01"
	to_date = to_date or "2099-12-31"
	leaves_allocated = float(leaves_allocated or 365)

	leave_types = frappe.get_all("Leave Type", pluck="name")
	if not leave_types:
		leave_types = [_ensure_simple("Leave Type", "leave_type_name", "Annual Leave")]

	employees = frappe.get_all("Employee", filters={"status": ["!=", "Left"]}, pluck="name")
	updated = {"created": 0, "updated": 0, "submitted": 0}

	for employee in employees:
		for leave_type in leave_types:
			alloc_name = frappe.db.get_value(
				"Leave Allocation",
				{"employee": employee, "leave_type": leave_type, "docstatus": ["!=", 2]},
				"name",
			)
			if alloc_name:
				alloc = frappe.get_doc("Leave Allocation", alloc_name)
				changed = False
				if str(alloc.from_date) > from_date:
					alloc.from_date = from_date
					changed = True
				if str(alloc.to_date) < to_date:
					alloc.to_date = to_date
					changed = True
				if (alloc.new_leaves_allocated or 0) < leaves_allocated:
					alloc.new_leaves_allocated = leaves_allocated
					changed = True
				if changed:
					alloc.save(ignore_permissions=True)
					updated["updated"] += 1
				if alloc.docstatus == 0:
					_safe_submit(alloc, ignore_validate=True)
					updated["submitted"] += 1
				continue

			alloc_doc = frappe.get_doc(
				{
					"doctype": "Leave Allocation",
					"employee": employee,
					"leave_type": leave_type,
					"from_date": from_date,
					"to_date": to_date,
					"new_leaves_allocated": leaves_allocated,
				}
			)
			_safe_insert(alloc_doc, ignore_mandatory=True, ignore_validate=True)
			_safe_submit(alloc_doc, ignore_validate=True)
			updated["created"] += 1
			updated["submitted"] += 1

	frappe.db.commit()
	return {"status": "ok", "updated": updated}
