# Server Script: juice.get_orders_by_phone (Allow Guest)
#
# Loại: API | API Method: juice.get_orders_by_phone | Allow Guest: TICK
# Tra danh sách đơn webshop gần đây theo SỐ ĐIỆN THOẠI khách (dễ nhớ hơn mã đơn).
#
# RestrictedPython: KHONG "import json" (co san global json), KHONG frappe._dict.

phone = (frappe.form_dict.get("phone") or "").strip()
if frappe.request and frappe.request.data:
    try:
        body = json.loads(frappe.request.data)
        phone = (body.get("phone") or phone or "").strip()
    except Exception:
        pass

if not phone:
    frappe.throw("Thiếu số điện thoại.")

# Chỉ lấy đơn của đúng SĐT này (khách biết SĐT của mình)
customers = frappe.get_all("Customer", filters={"mobile_no": phone}, pluck="name")

result = []
if customers:
    orders = frappe.get_all(
        "Sales Order",
        filters={"customer": ["in", customers], "source": "Shopping Cart"},
        fields=["name", "creation", "grand_total", "custom_order_prep_status",
                "custom_fulfillment", "docstatus"],
        order_by="creation desc",
        limit_page_length=15,
    )
    for o in orders:
        if o.docstatus == 2:
            status = "Cancelled"
        else:
            inv = frappe.db.get_value(
                "Sales Invoice",
                {"docstatus": 1, "remarks": ["like", "%" + o.name + "%"]},
                "name",
            )
            status = "Completed" if inv else (o.custom_order_prep_status or "Pending")

        its = frappe.get_all(
            "Sales Order Item",
            filters={"parent": o.name},
            fields=["item_name", "qty"],
            order_by="idx",
        )
        summary = ", ".join([f"{i.item_name}×{int(i.qty)}" for i in its[:6]])

        result.append({
            "name": o.name,
            "creation": str(o.creation),
            "grand_total": o.grand_total,
            "status": status,
            "fulfillment": o.custom_fulfillment or "",
            "summary": summary,
        })

frappe.response["message"] = result
