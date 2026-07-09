/* ====================================================================
   CẤU HÌNH TRANG MENU — sửa file này cho đúng site của bạn.
   Nạp trước index.html qua <script src="config.js"></script>
   ==================================================================== */
window.CONFIG = {
  // URL gốc ERPNext (KHÔNG dấu / cuối) — qua Tailscale Funnel công khai
  BASE_URL: "https://book3.tail030e1.ts.net",

  // Item Group chứa món nước ép. Phải khớp ALLOWED_GROUP trong server script.
  ITEM_GROUP: "Nước Ép",

  // Bảng giá bán
  PRICE_LIST: "Standard Selling",

  // Cách lấy menu: "direct" đọc thẳng Item (cần mở quyền Guest),
  // hoặc "method" gọi juice.get_menu (an toàn hơn — đã có sẵn server script).
  MENU_MODE: "method",

  // Method tạo đơn và lấy menu
  CREATE_METHOD: "juice.create_order",
  MENU_METHOD:   "juice.get_menu",

  // Method theo dõi đơn (có sẵn trong POS Next)
  TRACK_METHOD:  "pos_next.api.webshop.get_order_status"
};
