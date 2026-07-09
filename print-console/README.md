# Bàn in tem (Print Console) — QZ Tray

Trang này chạy trên **máy tính của quán** (cùng LAN với máy in). Nó:

1. Kết nối **QZ Tray** đang chạy nền → in ra máy in tem **đã cài trong Windows**
   (tận dụng cấu hình khổ 50×30mm bạn đã set sẵn trong driver).
2. Tự lấy **Sales Order đã Submit** (`docstatus=1`, `custom_printed=0`) từ ERPNext.
3. In **mỗi cốc 1 tem** khổ 50×30mm, rồi đánh dấu `custom_printed=1` (chống in trùng).

Không cần cài Python. Không đưa trang này lên internet công khai — chỉ mở trên PC quán.

---

## 1. Cài QZ Tray (một lần)

1. Tải QZ Tray: <https://qz.io/download/> → cài bản Windows.
2. Mở QZ Tray (thấy icon ở khay hệ thống, khay đồng hồ). Nó chạy nền, mở cổng
   `wss://localhost:8181`.
3. Đảm bảo máy in tem đã xuất hiện trong **Windows → Settings → Printers** và
   in test page ra được (khổ 50×30mm đã cấu hình trong driver).

> **Chế độ chưa ký (unsigned):** lần in đầu QZ Tray hiện hộp thoại “Allow …”.
> Bấm chọn **“Remember this decision”** rồi **Allow** để lần sau không hỏi lại.
> Muốn bỏ hẳn hộp thoại (production) thì tạo certificate ký — xem mục 5.

## 2. Tạo API key cho ERPNext

1. ERPNext → User của bạn (nên tạo user riêng `print-agent@…`, Role **Sales User**
   có quyền đọc + ghi Sales Order).
2. Mở user → **Settings → API Access → Generate Keys** → lưu lại **API Key** và
   **API Secret**.

## 3. Bật CORS trên ERPNext

Trang này gọi ERPNext bằng token header. Nếu mở trang bằng `file://` hoặc khác
domain, ERPNext phải cho phép CORS. Trong `site_config.json` (hoặc
`common_site_config.json`) của site:

```json
{ "allow_cors": "*" }
```

Rồi `bench restart` (frappe_docker: `docker compose restart backend`).
Nếu chạy sau Nginx/Cloudflare, đừng chặn preflight `OPTIONS`.

## 4. Chạy Bàn in

1. Mở `index.html` bằng trình duyệt (double-click là được, hoặc kéo vào Chrome).
2. Điền:
   - **BASE_URL**: URL gốc ERPNext, ví dụ `https://erp.quancuaban.com` (không `/` cuối).
   - **API Key / API Secret** (mục 2).
   - **Tên quán**, khổ tem (mặc định 50×30).
3. Bấm **Kết nối QZ Tray** → chọn đúng **máy in** trong danh sách.
4. Bấm **Lưu cấu hình** (lưu vào máy này, an toàn — không nằm trong mã nguồn).
5. Bấm **In thử 1 tem** để canh khổ. Lệch thì chỉnh lại khổ giấy trong driver
   Windows hoặc số mm trong trang.
6. Bấm **▶ Bắt đầu tự in**. Từ giờ, cứ đơn nào bạn **Submit** trong ERPNext là
   tem tự nhả ra.

### Nút khác
- **Quét & in 1 lần**: quét thủ công 1 lượt (không lặp).
- **In lại theo mã đơn**: in lại tem 1 đơn bất kỳ (không đổi cờ đã in).
- **Bỏ dấu tiếng Việt**: bật nếu máy in ra ký tự lỗi — sẽ in `Nuoc ep cam`.

## 5. (Tùy chọn) Ký certificate để hết hộp thoại Allow

Xem hướng dẫn QZ Tray “Signing Messages”:
<https://qz.io/docs/signing>. Tự ký (self-signed) đủ dùng cho 1 máy nội bộ:
tạo `digital-certificate.txt` + `private-key.pem`, rồi sửa
`setCertificatePromise` / `setSignaturePromise` trong `index.html` để nạp chúng.
Với quán nhỏ 1 máy, chế độ unsigned + “Remember” là đủ.

## Xử lý sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| Chấm đỏ, “Không kết nối được QZ Tray” | QZ Tray chưa chạy → mở app QZ Tray. Trình duyệt chặn `localhost` wss → cho phép. |
| Kết nối OK nhưng danh sách máy in trống | Máy in chưa cài trong Windows, hoặc chưa là máy in mặc định. |
| `HTTP 403` khi lấy đơn | API key sai, hoặc user không có quyền đọc Sales Order. |
| `HTTP 0` / lỗi CORS | Chưa bật `allow_cors`, hoặc Nginx chặn OPTIONS. |
| Tem in lệch / mất chữ | Chỉnh khổ 50×30mm + gap trong driver Windows; giảm nội dung; bật “Bỏ dấu”. |
| In trùng | Cờ `custom_printed` chưa được tạo hoặc PUT bị 403 → kiểm tra quyền ghi. |

## So với `print-agent/agent.py`

`print-agent/agent.py` là bản **thay thế bằng Python** (polling + python-escpos,
in TCP thẳng tới máy in). Bạn đã chọn **QZ Tray** nên dùng thư mục này. Giữ
`print-agent/` lại chỉ để tham khảo/dự phòng.
