# Server Script: juice.find_order  (Allow Guest)
#
# Loại: API | API Method: juice.find_order | Allow Guest: TICK
# Nhận mã NGẮN khách nhìn thấy ("#18", "18") hoặc tên đầy đủ
# ("SAL-ORD-2026-00018") -> trả về TÊN ĐẦY ĐỦ của Sales Order webshop.
# Dùng để trang theo dõi cho khách gõ mã ngắn.
#
# RestrictedPython: KHONG import (co san json), KHONG frappe._dict.

code = (frappe.form_dict.get("code") or "").strip()
if frappe.request and frappe.request.data:
    try:
        body = json.loads(frappe.request.data)
        code = (body.get("code") or code or "").strip()
    except Exception:
        pass

if not code:
    frappe.throw("Thiếu mã đơn.")

result = None

if code.upper().startswith("SAL-ORD"):
    row = frappe.db.get_value("Sales Order", code, ["name", "source"], as_dict=True)
    if row and row.source == "Shopping Cart":
        result = row.name
else:
    digits = "".join([c for c in code if c in "0123456789"])
    if not digits:
        frappe.throw("Mã đơn không hợp lệ. Nhập số (vd 18) hoặc dùng số điện thoại.")
    padded = digits.zfill(5) if len(digits) < 5 else digits
    rows = frappe.get_all(
        "Sales Order",
        filters={"source": "Shopping Cart", "name": ["like", "%-" + padded]},
        fields=["name"], order_by="creation desc", limit_page_length=1,
    )
    if not rows:
        rows = frappe.get_all(
            "Sales Order",
            filters={"source": "Shopping Cart", "name": ["like", "%" + digits]},
            fields=["name"], order_by="creation desc", limit_page_length=1,
        )
    if rows:
        result = rows[0]["name"]

if not result:
    frappe.throw("Không tìm thấy đơn: " + code)

frappe.response["message"] = {"name": result}
