from __future__ import annotations

import frappe


def hide_non_hr_workspaces(keep_modules: tuple[str, ...] = ("HR",)) -> dict:
	"""Hide all workspaces except those whose module is in keep_modules."""
	updated = 0
	kept = 0

	workspaces = frappe.get_all(
		"Workspace",
		fields=["name", "module", "is_hidden"],
	)
	for ws in workspaces:
		module = (ws.module or "").strip()
		should_hide = module not in keep_modules
		if should_hide and not ws.is_hidden:
			frappe.db.set_value("Workspace", ws.name, "is_hidden", 1)
			updated += 1
		elif not should_hide:
			kept += 1
			if ws.is_hidden:
				frappe.db.set_value("Workspace", ws.name, "is_hidden", 0)
				updated += 1

	frappe.db.commit()
	frappe.clear_cache()
	return {"updated": updated, "kept": kept, "keep_modules": list(keep_modules)}
