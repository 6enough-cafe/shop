# PROMPT BÀN GIAO — Hệ thống đặt nước ép qua web menu + ERPNext + tự in tem

> Dán prompt này vào IDE local (Cursor / VS Code + Claude / Copilot) để agent
> làm tiếp. Kèm theo toàn bộ thư mục project này làm context.

---

## Bối cảnh

Tôi tự host **ERPNext + POSNext** làm website bán nước ép, in tem dán cốc.
Đã có sẵn:
- `web/index.html` + `web/config.js` — trang menu tĩnh cho khách chọn món,
  nhập tên/SĐT/địa chỉ, gửi tạo **Sales Order Draft** qua REST API.
- `erpnext/server_script_create_order.py` — Server Script (Allow Guest) tạo SO.
- `erpnext/server_script_get_menu.py` — Server Script (Allow Guest) trả menu.
- `print-agent/agent.py` — **SKELETON** in tem ESC/POS, cần hoàn thiện.

Luồng nghiệp vụ:
```
Khách chọn món trên web  →  Sales Order (Draft, docstatus=0)
   →  Chủ quán bấm Submit trên app ERPNext (xác nhận thủ công)
   →  Print Agent phát hiện SO đã Submit  →  in tem cốc ESC/POS qua LAN
```

Môi trường: máy in nhiệt **ESC/POS (Xprinter/Gprinter)**, **cùng LAN** với server ERPNext.

---

## Việc cần làm

### 1. Hoàn thiện `print-agent/agent.py` (ưu tiên cao nhất)
Điền toàn bộ hàm `[TODO]`:

- `fetch_pending_orders()`: GET `/api/resource/Sales Order` với
  `filters=[["docstatus","=",1],["custom_printed","=",0]]`,
  `fields=["name","customer","custom_contact_phone","custom_delivery_address","custom_order_note"]`,
  `limit_page_length=20`, sort theo `creation asc`. Dùng token auth.
- `get_order_detail(name)`: GET `/api/resource/Sales Order/{name}` lấy đủ `items`
  (item_code, item_name, qty). Có thể cần join tên món.
- `print_label(order)`: dùng `escpos.printer.Network`. In **mỗi cốc 1 tem**
  (lặp theo qty của từng item). Bố cục tem khổ 58mm:
  - Dòng đầu: tên quán (in đậm, to)
  - Tên món + biến thể/ghi chú
  - Mã đơn + QR chứa `order.name`
  - Tên KH + SĐT (nhỏ)
  Hỗ trợ tiếng Việt: cân nhắc bỏ dấu (unidecode) vì nhiều máy ESC/POS
  không có font Unicode; hoặc set codepage phù hợp. Test cả 2.
- `mark_printed(name)`: PUT `/api/resource/Sales Order/{name}` với
  body `{"custom_printed": 1}`. CHỈ gọi sau khi in thành công.
- Xử lý lỗi: nếu máy in mất kết nối → log, KHÔNG mark printed, retry vòng sau.
- Thêm graceful shutdown (Ctrl+C), log ra file `agent.log`.

Yêu cầu phụ: viết `print-agent/agent.service` (systemd unit) để chạy nền,
và `print-agent/README.md` hướng dẫn cài trên Linux/Windows.

### 2. Bổ sung custom field ERPNext
Cần tạo trên Sales Order (Customize Form), viết fixtures hoặc hướng dẫn:
- `custom_contact_phone` (Data)
- `custom_delivery_address` (Small Text)
- `custom_order_note` (Small Text)
- `custom_printed` (Check, default 0)  ← agent dùng chống in trùng

Nếu làm được: xuất thành **fixtures JSON** (`erpnext/fixtures/custom_field.json`)
để `bench` import lại được, thay vì click tay.

### 3. Đóng gói thành Frappe App (tùy chọn, nếu có thời gian)
Gộp 2 server script + custom fields + hooks thành một app `juice_shop`
cài bằng `bench get-app`. `on_submit` hook của Sales Order có thể đẩy job in
thay cho polling (tối ưu độ trễ). Cân nhắc dùng `frappe.enqueue`.

### 4. Deploy web
- Viết `web/README.md`: deploy trang tĩnh (Cloudflare Pages / Nginx).
- Tạo QR trỏ tới URL menu để đặt tại quán.
- Kiểm tra CORS thực tế (preflight OPTIONS qua Nginx).

---

## Ràng buộc & tiêu chí

- **Không** hardcode API key trong web (chỉ trong print-agent, chạy nội bộ).
- Server script phải giữ **whitelist Item Group** để chặn đặt món ngoài menu.
- SO tạo ra luôn ở **Draft** — không tự submit; xác nhận là thao tác người.
- Tiếng Việt là ngôn ngữ chính trong UI và tem.
- Test bằng `curl` (có sẵn ví dụ trong `erpnext/HUONG_DAN_ERPNEXT.md`).

## Thứ tự đề xuất
1) Tạo custom fields → 2) Hoàn thiện agent.py → 3) Test end-to-end 1 đơn
→ 4) systemd/README → 5) (tùy chọn) đóng app + hook on_submit.

## Câu hỏi mở cho tôi (hỏi nếu cần)
- Máy in Xprinter model nào, cổng LAN (RJ45) hay chỉ USB?
- Khổ tem: 58mm hay 80mm? In 1 tem/đơn hay 1 tem/cốc?
- Có cần in kèm giá tiền / tổng đơn trên tem không?
