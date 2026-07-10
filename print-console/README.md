# Bàn đơn web (Order Station) — QZ Tray

Trang này chạy trên **máy POS của quán**, mở 1 tab **cạnh POS Next**. Nó là nơi
quán **nhận — xử lý — in tem** đơn đặt từ web.

## Làm được gì

- 🔔 **Chuông + nhấp nháy + thông báo hệ thống** khi có đơn web mới.
- Thẻ đơn hiện: món, **ghi chú riêng từng cốc**, **Tới lấy / Giao tận nơi**,
  địa chỉ, SĐT, tổng tiền, cờ *đã in tem*.
- Nút trạng thái ✅ Đã nhận · 👨‍🍳 Đang làm · 🎉 Sẵn hàng · ✔️ Hoàn thành · ❌ Hủy đơn.
  Bấm là gọi **đúng API mà POS Next dùng** (`update_order_prep_status`) → **POS Next
  và trang theo dõi của khách đều cập nhật ngay**.
- 🖨️ **In tem 50×30mm, mỗi cốc 1 tem** qua QZ Tray (máy in đã cài trong Windows).
  Tuỳ chọn **tự in** khi đơn mới về.

> **KHÔNG** đưa trang này lên internet công khai: nó giữ API key. Chỉ mở trên máy quán.
> (Mã nguồn trong repo không chứa key — key bạn nhập vào form, lưu ở `localStorage` của máy đó.)

---

## 1. Cài QZ Tray (một lần)

1. Tải & cài: <https://qz.io/download/> (bản Windows).
2. Mở QZ Tray (icon ở khay hệ thống). Nó mở `wss://localhost:8181`.
3. Máy in tem phải xuất hiện trong **Windows → Printers**, khổ **50×30mm** đã cấu hình
   trong driver.

> Lần in đầu QZ Tray hiện hộp thoại “Allow…”. Tích **“Remember this decision”** → **Allow**.

## 2. Tạo API key cho ERPNext

Tạo user riêng (vd `banhang@…`) có role đọc/ghi **Sales Order**, rồi
**User → Settings → API Access → Generate Keys** → lưu **API Key** + **API Secret**.

Quyền cần: đọc/ghi `Sales Order` (đổi `custom_printed`) và gọi được
`pos_next.api.webshop.update_order_prep_status`.

## 3. Bật CORS

Trang mở bằng `file://` nên ERPNext phải cho phép CORS. Trong `site_config.json`:

```json
{ "allow_cors": "*" }
```
rồi `bench restart` (frappe_docker: `docker compose restart backend`).

## 4. Chạy

1. Mở `index.html` bằng trình duyệt trên máy POS (double-click được).
2. Điền **BASE_URL** (vd `https://book3.tail030e1.ts.net`), **API Key/Secret**.
3. **Kết nối QZ Tray** → chọn **máy in** → **In thử 1 tem** để canh khổ.
4. **Lưu** cấu hình.
5. Bấm **▶ Bắt đầu theo dõi**. Từ đây, đơn web về là **chuông reo**, thẻ đơn
   nhấp nháy, bạn bấm trạng thái và **In tem**.

### Tuỳ chọn
- **🔔 Chuông** / **🖥️ Thông báo hệ thống** (cần cho phép Notification).
- **🖨️ Tự in tem khi đơn mới về** — bỏ bước bấm tay.
- **Hiện cả đơn đã xong/đã hủy** — mặc định ẩn để hàng chờ gọn.

---

## Quan hệ với POS Next

| Việc | Làm ở đâu |
|---|---|
| Nhận đơn, đổi trạng thái, in tem | **Bàn đơn web** (trang này) |
| Thu tiền, chốt hóa đơn | **POS Next** → Invoice Management → tab **Drafts** → *Webshop / Online Orders* |

Đơn web tự sinh **hóa đơn POS Draft** (`ACC-SINV-…`). Trạng thái đổi ở đâu cũng
đồng bộ, vì cả hai gọi chung một API.

## Xử lý sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| Chấm đỏ, không kết nối QZ Tray | QZ Tray chưa chạy → mở app. |
| Danh sách máy in trống | Máy in chưa cài trong Windows. |
| `HTTP 403` khi đổi trạng thái | API key sai, hoặc user thiếu quyền. |
| `HTTP 0` / lỗi CORS | Chưa bật `allow_cors`, hoặc Nginx chặn `OPTIONS`. |
| Không có chuông | Bấm **▶ Bắt đầu theo dõi** một lần (trình duyệt cần thao tác người để mở âm thanh). |
| Tem lệch / mất chữ | Chỉnh khổ 50×30mm + gap trong driver; bật **Bỏ dấu tiếng Việt**. |
| In trùng | Cờ `custom_printed` chưa tạo, hoặc PUT bị 403. |

## Bản Python cũ

`../print-agent/agent.py` là bản thay thế bằng Python (polling + ESC/POS).
Bạn dùng QZ Tray nên **không cần**; giữ lại chỉ để tham khảo.
