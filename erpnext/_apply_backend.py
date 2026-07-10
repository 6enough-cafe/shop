# -*- coding: utf-8 -*-
# Ap dung backend cho site hien tai. Chay trong bench console:
#   exec(open("/tmp/juice_erpnext/_apply_backend.py").read())
# Yeu cau: server_script_enabled=1 da bat (de save duoc Server Script).

import os
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

HERE = "/tmp/juice_erpnext"


def _read(fn):
    with open(os.path.join(HERE, fn), encoding="utf-8") as f:
        return f.read()


# ---- 1) Custom fields tren Sales Order ----
create_custom_fields(
    {
        "Sales Order": [
            {"fieldname": "custom_contact_phone", "label": "Contact Phone",
             "fieldtype": "Data", "insert_after": "customer", "in_standard_filter": 1},
            {"fieldname": "custom_delivery_address", "label": "Delivery Address",
             "fieldtype": "Small Text", "insert_after": "custom_contact_phone"},
            {"fieldname": "custom_order_note", "label": "Order Note",
             "fieldtype": "Small Text", "insert_after": "custom_delivery_address"},
            {"fieldname": "custom_fulfillment", "label": "Hinh thuc nhan", "fieldtype": "Data",
             "insert_after": "custom_order_note", "in_standard_filter": 1,
             "description": "Toi lay / Giao tan noi"},
            {"fieldname": "custom_printed", "label": "Printed (Tem)", "fieldtype": "Check",
             "default": "0", "read_only": 1, "in_list_view": 1, "in_standard_filter": 1,
             "insert_after": "custom_order_note",
             "description": "Ban in tu dong tick sau khi in tem. Chong in trung."},
        ],
        # Ghi chu theo tung coc (moi dong = 1 coc)
        "Sales Order Item": [
            {"fieldname": "custom_note", "label": "Ghi chu (coc)", "fieldtype": "Data",
             "insert_after": "qty", "in_list_view": 1},
        ],
    },
    ignore_validate=True,
)
print("custom fields: OK")


# ---- 2) Server Scripts (Allow Guest, type API) ----
def ensure_ss(docname, method, script, allow_guest=1):
    if frappe.db.exists("Server Script", docname):
        d = frappe.get_doc("Server Script", docname)
    else:
        d = frappe.new_doc("Server Script")
        d.name = docname
    d.script_type = "API"
    d.api_method = method
    d.allow_guest = allow_guest
    d.disabled = 0
    d.script = script
    d.save(ignore_permissions=True)
    return d.name


ensure_ss("juice_get_menu", "juice.get_menu", _read("server_script_get_menu.py"))
ensure_ss("juice_create_order", "juice.create_order", _read("server_script_create_order.py"))
ensure_ss("juice_get_orders_by_phone", "juice.get_orders_by_phone", _read("server_script_orders_by_phone.py"))
ensure_ss("juice_find_order", "juice.find_order", _read("server_script_find_order.py"))
# Chi cho user da dang nhap (Ban don web dung API key) — KHONG allow guest
ensure_ss("juice_mark_printed", "juice.mark_printed", _read("server_script_mark_printed.py"), allow_guest=0)
frappe.db.commit()
print("server scripts: OK -> juice.get_menu, juice.create_order")
print("BACKEND SETUP DONE")
