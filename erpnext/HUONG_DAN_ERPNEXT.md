# Cài đặt phía ERPNext

## 1. Server Script `juice.create_order` (cho phép Guest tạo đơn)

Vào **Server Script → New**:

- **Script Type:** `API`
- **API Method:** `juice.create_order`  ← đúng với CONFIG.CREATE_METHOD
- **Allow Guest:** ✅ tích
- **Script:** dán đoạn dưới

```python
import json

data = frappe.form_dict
# Nếu gửi JSON body, đọc từ request
if frappe.request and frappe.request.data:
    try:
        body = json.loads(frappe.request.data)
        data = frappe._dict(body)
    except Exception:
        pass

# ---- Validate cơ bản ----
cust_name = (data.get("customer_name") or "").strip()
phone     = (data.get("phone") or "").strip()
address   = (data.get("address") or "").strip()
note      = (data.get("note") or "").strip()
items     = data.get("items") or []

if not cust_name or not phone or not address:
    frappe.throw("Thiếu thông tin khách (tên/SĐT/địa chỉ).")
if not items:
    frappe.throw("Giỏ hàng trống.")

# ---- Whitelist item: chỉ cho phép món trong Item Group "Nước Ép" ----
ALLOWED_GROUP = "Nước Ép"
clean_items = []
for it in items:
    code = it.get("item_code")
    qty  = float(it.get("qty") or 0)
    if not code or qty <= 0:
        continue
    doc_item = frappe.db.get_value(
        "Item", code,
        ["item_group", "is_sales_item", "disabled"],
        as_dict=True
    )
    if not doc_item or doc_item.disabled or not doc_item.is_sales_item:
        frappe.throw(f"Món không hợp lệ: {code}")
    if ALLOWED_GROUP and doc_item.item_group != ALLOWED_GROUP:
        frappe.throw(f"Món không nằm trong thực đơn: {code}")
    clean_items.append({"item_code": code, "qty": qty})

if not clean_items:
    frappe.throw("Không có món hợp lệ.")

# ---- Tìm/tạo Customer theo SĐT ----
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

# ---- Tạo Sales Order ở trạng thái Draft (KHÔNG submit) ----
so = frappe.get_doc({
    "doctype": "Sales Order",
    "customer": customer,
    "order_type": "Sales",
    "transaction_date": frappe.utils.nowdate(),
    "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 1),
    "custom_contact_phone": phone,        # tạo custom field nếu muốn (xem mục 3)
    "custom_delivery_address": address,   # tạo custom field
    "custom_order_note": note,
    "items": [
        {"item_code": ci["item_code"], "qty": ci["qty"]} for ci in clean_items
    ],
})
so.flags.ignore_permissions = True
so.insert(ignore_permissions=True)   # docstatus = 0 (Draft) → chờ chủ quán Submit

frappe.db.commit()
frappe.response["message"] = {"order_id": so.name, "name": so.name}
```

## 2. Bật CORS (bắt buộc vì trang tĩnh khác domain)

Trong file `site_config.json` của site (hoặc `common_site_config.json`):

```json
{
  "allow_cors": "*"
}
```

Hoặc chỉ định domain trang menu của bạn thay cho `*` (an toàn hơn):

```json
{
  "allow_cors": "https://menu.quancuaban.com"
}
```

Rồi `bench restart`.

> Nếu chạy sau Nginx/Cloudflare, đảm bảo không chặn header `OPTIONS` (preflight).

## 3. (Tuỳ chọn) Custom Field lưu địa chỉ/SĐT/ghi chú trên Sales Order

Vào **Customize Form → Sales Order**, thêm 3 field (Field Type = Data / Small Text):

| Label            | Fieldname (auto)          |
|------------------|---------------------------|
| Contact Phone    | custom_contact_phone      |
| Delivery Address | custom_delivery_address   |
| Order Note       | custom_order_note         |

Nếu không muốn custom field, xoá 3 dòng `custom_...` trong script và nhét địa chỉ/ghi chú vào một field có sẵn như `terms` hoặc tạo Address record riêng.

## 4. Cho Guest đọc Item / Item Price (để menu load được)

Trang tự đọc `Item` và `Item Price` qua REST bằng quyền Guest. Có 2 cách:

**Cách A — mở quyền đọc (nhanh):**
Role **Guest** → cấp `read` cho DocType `Item` và `Item Price` (Role Permission Manager). Chỉ nên áp field cần thiết; cân nhắc rủi ro lộ danh mục.

**Cách B — an toàn hơn (khuyên dùng):**
Viết thêm 1 Server Script API `juice.get_menu` (Allow Guest) trả về đúng danh sách món + giá, rồi sửa `loadMenu()` gọi method này thay vì đọc thẳng `Item`. Nói mình nếu bạn muốn bản này — mình viết luôn.

## 5. Kiểm thử nhanh

```bash
curl -X POST https://your-erpnext-site.com/api/method/juice.create_order \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Test","phone":"0900000000","address":"1 Test St","items":[{"item_code":"NUOC-EP-CAM","qty":2}]}'
```

Kỳ vọng trả về: `{"message":{"order_id":"SAL-ORD-2026-...","name":"..."}}`
và trong ERPNext xuất hiện 1 Sales Order **Draft**.
