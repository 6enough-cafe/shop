# Web menu — Deploy lên GitHub Pages (URL công khai gửi khách)

Thư mục này là trang tĩnh cho khách chọn món. Chỉ có 2 file cần lên web:
`index.html` và `config.js`. Không chứa API key.

## Bước 0 — Sửa `config.js` (BẮT BUỘC)

Mở [config.js](config.js) và sửa **1 dòng** duy nhất:

```js
BASE_URL: "https://erp.quancuaban.com",   // ← URL gốc ERPNext CÔNG KHAI của bạn
```

`ITEM_GROUP` để `"Nước Ép"` cho khớp server script. `MENU_MODE: "method"` (đã sẵn)
gọi `juice.get_menu` — an toàn, không cần mở quyền Guest đọc Item.

## Bước 1 — Đưa lên GitHub Pages

Cách đơn giản nhất: **1 repo public chứa nội dung của thư mục `web/` ở gốc repo.**

```powershell
# Chay trong thu muc web/  (PowerShell)
cd C:\ERPNext\files\juice\web
git init -b main
git add index.html config.js .nojekyll
git commit -m "Juice menu"
# Tao repo tren github.com truoc (vd: juice-menu, Public), roi:
git remote add origin https://github.com/<USER>/juice-menu.git
git push -u origin main
```

Rồi trên GitHub: **Settings → Pages → Source: Deploy from a branch →
Branch: `main` / folder `/ (root)` → Save.**

Sau ~1 phút, URL công khai của bạn là:

```
https://<USER>.github.io/juice-menu/
```

> Có sẵn script `deploy-github-pages.ps1` làm giúp các lệnh git ở trên —
> sửa biến `$USER`/`$REPO` bên trong rồi chạy.

## Bước 2 — Bật CORS trên ERPNext (BẮT BUỘC)

Trang chạy ở domain `github.io` khác domain ERPNext → phải cho phép CORS.
Trong `site_config.json` của site (hoặc `common_site_config.json`):

```json
{ "allow_cors": "*" }
```

An toàn hơn: chỉ cho đúng origin GitHub Pages:

```json
{ "allow_cors": "https://<USER>.github.io" }
```

Rồi `bench restart` (frappe_docker: `docker compose restart backend`).
Đảm bảo Nginx/Cloudflare trước ERPNext **không chặn preflight `OPTIONS`**.

## Bước 3 — Kiểm tra

1. Mở `https://<USER>.github.io/juice-menu/` → menu phải load được các món.
   Nếu trắng trơn: mở DevTools (F12) → Console xem lỗi CORS hay 403.
2. Đặt thử 1 đơn → vào ERPNext kiểm tra có **Sales Order Draft** mới.
3. Submit đơn đó → **Bàn in** (print-console) tự in tem.

## Bước 4 — Tạo QR dán tại quán

Mở [make-qr.html](make-qr.html) bằng trình duyệt, dán URL menu ở trên →
tải ảnh QR về in ra dán tại quầy cho khách quét đặt món.

---

### Vì sao GitHub Pages không cần lo lộ khóa?
`config.js` chỉ chứa `BASE_URL` công khai và tên method. Mọi thao tác ghi đều đi
qua server script Guest **có validate + whitelist Item Group**. API key chỉ nằm
trong Bàn in chạy nội bộ. Đây đúng mô hình bảo mật trong README gốc.
