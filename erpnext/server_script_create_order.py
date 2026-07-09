# Server Script: juice.create_order (Allow Guest)
#
# Loại: API | API Method: juice.create_order | Allow Guest: TICK
# Tạo Sales Order ở Draft (docstatus=0) chờ chủ quán Submit.
# Luu y: Server Script chay trong RestrictedPython — KHONG "import json"
# (frappe da cap san "json" nhu global). Cung khong dung frappe._dict.

data = frappe.form_dict
if frappe.request and frappe.request.data:
    try:
        # Server Script chay trong RestrictedPython -> khong dung frappe._dict
        # (thuoc tinh bat dau bang "_" bi cam). Dung thang dict tu json.loads.
        data = json.loads(frappe.request.data)
    except Exception:
        pass

cust_name = (data.get("customer_name") or "").strip()
phone     = (data.get("phone") or "").strip()
address   = (data.get("address") or "").strip()
note      = (data.get("note") or "").strip()
items     = data.get("items") or []

if not cust_name or not phone or not address:
    frappe.throw("Thiếu thông tin khách (tên/SĐT/địa chỉ).")
if not items:
    frappe.throw("Giỏ hàng trống.")

ALLOWED_GROUP = "Nước Ép"
clean_items = []
for it in items:
    code = it.get("item_code")
    qty  = float(it.get("qty") or 0)
    if not code or qty <= 0:
        continue
    doc_item = frappe.db.get_value(
        "Item", code, ["item_group", "is_sales_item", "disabled"], as_dict=True
    )
    if not doc_item or doc_item.disabled or not doc_item.is_sales_item:
        frappe.throw(f"Món không hợp lệ: {code}")
    if ALLOWED_GROUP and doc_item.item_group != ALLOWED_GROUP:
        frappe.throw(f"Món không nằm trong thực đơn: {code}")
    it_note = (it.get("note") or "").strip()[:140]   # ghi chú riêng cốc này
    clean_items.append({"item_code": code, "qty": qty, "note": it_note})

if not clean_items:
    frappe.throw("Không có món hợp lệ.")

existing = frappe.db.get_value("Customer", {"mobile_no": phone}, "name")
if existing:
    customer = existing
else:
    cust = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": f"{cust_name} ({phone})",
        "customer_type": "Individual",
        "customer_group": frappe.db.get_single_value("Selling Settings", "customer_group") or "Individual",
        "territory": frappe.db.get_single_value("Selling Settings", "territory") or "Vietnam",
        "mobile_no": phone,
    })
    cust.insert(ignore_permissions=True)
    customer = cust.name

so = frappe.get_doc({
    "doctype": "Sales Order",
    "customer": customer,
    "order_type": "Sales",
    "transaction_date": frappe.utils.nowdate(),
    "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 1),
    "custom_contact_phone": phone,
    "custom_delivery_address": address,
    "custom_order_note": note,
    "items": [
        {"item_code": ci["item_code"], "qty": ci["qty"], "custom_note": ci["note"]}
        for ci in clean_items
    ],
})
so.flags.ignore_permissions = True
so.insert(ignore_permissions=True)

frappe.db.commit()
frappe.response["message"] = {"order_id": so.name, "name": so.name}
