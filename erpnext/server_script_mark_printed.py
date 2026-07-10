# Server Script: juice.mark_printed  (KHÔNG tick Allow Guest — cần đăng nhập/API key)
#
# Loại: API | API Method: juice.mark_printed
# Đánh dấu đơn web đã in tem. Dùng frappe.db.set_value nên KHÔNG chạy lại
# validate() của Sales Order -> user chỉ cần quyền tối thiểu, không cần đọc
# Item/Customer/Price List như khi PUT /api/resource.
#
# RestrictedPython: KHONG import (co san global json), KHONG frappe._dict.

order_id = (frappe.form_dict.get("order_id") or "").strip()
if frappe.request and frappe.request.data:
    try:
        body = json.loads(frappe.request.data)
        order_id = (body.get("order_id") or order_id or "").strip()
    except Exception:
        pass

if not order_id:
    frappe.throw("Thiếu order_id.")

row = frappe.db.get_value("Sales Order", order_id, ["name", "source"], as_dict=True)
if not row:
    frappe.throw("Không tìm thấy đơn: " + order_id)
if row.source != "Shopping Cart":
    frappe.throw("Chỉ đánh dấu được đơn đặt từ web.")

frappe.db.set_value("Sales Order", order_id, "custom_printed", 1)
frappe.db.commit()

frappe.response["message"] = {"order_id": order_id, "custom_printed": 1}
