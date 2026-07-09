# Juice Shop — Web menu đặt nước ép + ERPNext + tự in tem (QZ Tray)

Hệ thống đặt nước ép tự phục vụ: khách chọn món trên web → tạo Sales Order
Draft trong ERPNext → chủ quán xác nhận (Submit) → **Bàn in (QZ Tray)** tự in
tem cốc ra máy in tem 50×30mm đã cài trong Windows.

## Luồng nghiệp vụ

```
Khách quét QR → chọn món trên web menu (URL công khai GitHub Pages)
   → Sales Order (Draft, docstatus=0) trong ERPNext
   → Chủ quán bấm Submit (xác nhận thủ công)
   → Bàn in phát hiện đơn đã Submit → in mỗi cốc 1 tem 50×30mm qua QZ Tray
   → tự đánh dấu custom_printed=1 (chống in trùng)
```

## Cấu trúc

```
juice/
├── web/                          # Trang menu công khai cho khách
│   ├── index.html                #   giao diện + logic (đã xong)
│   ├── config.js                 #   SỬA BASE_URL cho đúng ERPNext của bạn
│   ├── make-qr.html              #   tạo QR menu để dán tại quán
│   ├── deploy-github-pages.ps1   #   script đẩy lên GitHub Pages
│   └── README.md                 #   hướng dẫn deploy + CORS
├── erpnext/                      # Phần server-side ERPNext
│   ├── server_script_create_order.py   # tạo SO Draft (Allow Guest)
│   ├── server_script_get_menu.py       # trả menu an toàn (Allow Guest)
│   ├── install_custom_fields.py        # tạo 4 custom field (chạy 1 lần)
│   ├── fixtures/custom_field.json      # cùng nội dung, dạng fixtures
│   └── HUONG_DAN_ERPNEXT.md            # hướng dẫn server script + CORS
├── print-console/                # BÀN IN (QZ Tray) — chạy trên PC quán
│   ├── index.html                #   tự lấy đơn + in tem 50×30 + đánh dấu
│   └── README.md                 #   cài QZ Tray, API key, chạy
├── print-agent/                  # (Dự phòng) bản Python/ESC-POS — không dùng
└── docs/PROMPT_BAN_GIAO.md       # prompt bàn giao gốc
```

## Trạng thái

| Phần | Trạng thái |
|------|-----------|
| Web menu (chọn món, giỏ, form khách) | ✅ Xong |
| Server Script tạo đơn / lấy menu | ✅ Xong |
| Custom fields trên Sales Order (4 field) | ✅ Có script + fixtures — chạy 1 lần |
| Bàn in tem QZ Tray (50×30, 1 tem/cốc) | ✅ Xong |
| Deploy web ra URL công khai | ✅ Có hướng dẫn + script GitHub Pages |

## Làm theo thứ tự (từ đầu đến khi có URL gửi khách)

1. **ERPNext — custom field:** chạy `erpnext/install_custom_fields.py` (xem đầu file).
2. **ERPNext — server script:** tạo 2 Server Script Allow Guest từ
   `erpnext/server_script_*.py` (xem `HUONG_DAN_ERPNEXT.md`). Bật `allow_cors`.
3. **ERPNext — dữ liệu:** tạo Item Group `Nước Ép`, thêm các món (Item, is_sales_item)
   và giá (Item Price / Standard Selling).
4. **Bàn in:** cài QZ Tray trên PC quán, mở `print-console/index.html`, điền
   BASE_URL + API key, chọn máy in, In thử, rồi **Bắt đầu tự in**
   (xem `print-console/README.md`).
5. **Web công khai:** sửa `web/config.js` (BASE_URL) → deploy `web/` lên GitHub
   Pages (xem `web/README.md`) → có URL `https://<user>.github.io/juice-menu/`.
6. **QR:** mở `web/make-qr.html`, dán URL trên, in QR dán tại quán.

## Bảo mật

- Web công khai KHÔNG chứa API key — mọi thao tác ghi qua server script Guest có validate.
- Server script whitelist Item Group `Nước Ép` → khách không đặt được món ngoài menu.
- API key chỉ nằm trong Bàn in (localStorage của PC quán), chạy nội bộ.
- Sales Order luôn tạo ở Draft — Submit là thao tác người.
