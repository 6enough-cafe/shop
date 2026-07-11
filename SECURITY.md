# Bảo mật — hệ thống đặt món 6 Enough

## Kiến trúc THẬT (đề xuất bảo mật gốc đã đoán sai)

Tài liệu `security-fix-prompt-6enough.md` giả định backend là **Supabase / Firebase /
Google Sheets** với API key lộ trong frontend. **Thực tế KHÔNG phải vậy:**

| Thành phần | Thực tế |
|---|---|
| Frontend | Static trên GitHub Pages (`6enough-cafe.github.io/shop/`) — **KHÔNG chứa API key** |
| Backend | **ERPNext (Frappe)** qua Tailscale Funnel `book3.tail030e1.ts.net` |
| Ghi đơn / tra cứu | **Server Script "Allow Guest"** (`juice.*`) — có validate, không cần key |
| Bàn đơn (máy quán) | Dùng API key của user **`banhang@6enough.local`** role **`Ban Don Web`** (chỉ read/write Sales Order). Key ở `config.local.js` (đã .gitignore), KHÔNG lên repo |

Vì vậy các mục Supabase RLS / Firebase Rules / Google Sheets **không áp dụng**.
Tương đương của RLS ở đây = **quyền Frappe + phạm vi các Server Script Guest**.

---

## Đã làm (fix có hiệu lực thật)

### Server-side (Server Script — không thể bypass)
- **Validate SĐT VN**: đúng 10 số, bắt đầu `0`, số thứ 2 ∈ 3–9. Sai → từ chối.
- **Giới hạn**: ≤ 30 món/đơn, ≤ 20/món; cắt tên ≤ 80, địa chỉ/ghi chú ≤ 255 ký tự.
- **Whitelist Item Group** theo POS Profile — khách không đặt được món ngoài menu.
- **Đơn luôn ở Draft** — không tự ghi doanh thu.
- `juice.mark_printed` (đổi cờ đã in) **KHÔNG allow guest** — cần API key role tối thiểu.
- User Bàn đơn là **Website User** role `Ban Don Web`: không xem được Customer/User khác
  (đã kiểm chứng: GET Customer → 403, tạo SO → 403, liệt kê User → chỉ thấy chính nó).

### Client-side (lớp phụ / UX)
- Escape (`esc`/`escAttr`) mọi dữ liệu người dùng render vào DOM (tên, SĐT, ghi chú) —
  chống XSS. Đã hardening cả tên món (dữ liệu admin) và thông báo lỗi.
- Validate SĐT phía client trước khi gửi.
- Rate-limit **mềm** khi tra theo SĐT (10 lần/phút, localStorage) — **dễ bypass**, chỉ chống spam vô ý.
- Privacy notice cạnh ô SĐT.

---

## ⚠️ Rate-limit server-side: giới hạn nền tảng

Đề xuất muốn rate-limit chống quét dữ liệu. **Không làm được sạch trong Server Script**:
`safe_exec` của Frappe **chặn `frappe.cache`** và không cấp kho đếm theo-IP nào
(chỉ có `db.get_value/set_value`, `request`, `throw`…). Rate-limit **phía client vô dụng**
với kẻ tấn công vì họ gọi thẳng API.

**Rủi ro còn lại:** endpoint Guest (`get_order_status`, `get_orders_by_phone`, `find_order`)
có thể bị **quét tuần tự** để thu thập tên KH + món (không lộ mật khẩu/thanh toán/địa chỉ
qua tra cứu). Mã đơn tuần tự `SAL-ORD-…` **không đổi ngẫu nhiên được** vì POS Next
hard-code regex `SAL-ORD-[\d-]+` để nhận diện đơn online (đổi sẽ hỏng nút trạng thái POS).

### Phương án rate-limit THẬT (chọn 1 — cần hạ tầng, làm sau)
1. **Nginx `limit_req`** ở frappe_docker `frontend`: thêm zone giới hạn cho
   `location ~ ^/api/method/juice\.` — chặn theo IP tại proxy. Cần compose override mount
   nginx conf tùy biến. *(Khuyến nghị — ít xâm lấn nhất.)*
2. **Cloudflare** trước ERPNext (đổi Tailscale Funnel → Cloudflare Tunnel) → WAF + Rate
   Limiting Rules. Mạnh nhất nhưng đổi hạ tầng nhiều.
3. **Đóng Frappe App riêng** với `@frappe.whitelist(allow_guest=True)` + `@rate_limit(...)`
   thay cho Server Script — chuẩn Frappe nhưng cần rebuild image.
4. **Cloudflare Turnstile** ở form đặt món (chống bot tạo đơn) — cần verify token phía server
   (làm được nếu theo phương án 1/3).

Nói mình biết nếu muốn triển khai phương án 1 (mình dựng nginx `limit_req` + compose override).

---

## Việc vận hành nên làm
- **Revoke** token GitHub đã dùng khi deploy xong.
- Đổi **PIN** Bàn đơn (`window.STATION_PIN` trong `config.local.js`).
- Đảm bảo `allow_cors` chỉ mở cho origin cần (`https://6enough-cafe.github.io`) thay vì `*`
  nếu không dùng Bàn đơn từ `file://` nữa.
