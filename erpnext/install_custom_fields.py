# -*- coding: utf-8 -*-
# Cai 4 custom field cho Sales Order — chay 1 lan, KHONG can dong app.
#
# Cach chay (thay <site> bang ten site cua ban):
#
#   bench --site <site> console
#   >>> exec(open("apps/frappe/../../install_custom_fields.py").read())
#
# Hoac tien hon — copy toan bo noi dung ham ben duoi va dan vao:
#   bench --site <site> console
#
# Hoac chay thang tu file:
#   bench --site <site> execute install_custom_fields.run
#
# (Neu dung frappe_docker: `docker compose exec backend bench --site <site> console`)

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def run():
    create_custom_fields(
        {
            "Sales Order": [
                {
                    "fieldname": "custom_contact_phone",
                    "label": "Contact Phone",
                    "fieldtype": "Data",
                    "insert_after": "customer",
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "custom_delivery_address",
                    "label": "Delivery Address",
                    "fieldtype": "Small Text",
                    "insert_after": "custom_contact_phone",
                },
                {
                    "fieldname": "custom_order_note",
                    "label": "Order Note",
                    "fieldtype": "Small Text",
                    "insert_after": "custom_delivery_address",
                },
                {
                    "fieldname": "custom_printed",
                    "label": "Printed (Tem)",
                    "fieldtype": "Check",
                    "default": "0",
                    "read_only": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                    "insert_after": "custom_order_note",
                    "description": "Ban in tu dong tick sau khi in tem. Chong in trung.",
                },
            ]
        },
        ignore_validate=True,
    )
    frappe.db.commit()
    print("OK: da tao 4 custom field tren Sales Order.")


# Cho phep `exec(open(...).read())` trong console cung chay ngay:
if __name__ == "__main__" or frappe.local.site:
    try:
        run()
    except Exception as e:  # console: in loi ro rang
        print("Loi khi tao custom field:", e)
