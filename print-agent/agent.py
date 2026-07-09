#!/usr/bin/env python3
"""
Print Agent — polling Sales Order đã Submit trong ERPNext,
in tem cốc ra máy in nhiệt ESC/POS (Xprinter/Gprinter) qua LAN.

TRẠNG THÁI: SKELETON — cần IDE hoàn thiện các phần đánh dấu [TODO].
Xem docs/PROMPT_BAN_GIAO.md để biết yêu cầu đầy đủ.

Chạy:
    pip install python-escpos requests
    python agent.py

Cơ chế chống in trùng: dùng custom field `custom_printed` (Check) trên
Sales Order. Agent chỉ in đơn có docstatus=1 và custom_printed=0, in xong set =1.
"""

import time
import requests

# ==================== CẤU HÌNH ====================
CONFIG = {
    "BASE_URL": "https://your-erpnext-site.com",
    "API_KEY": "xxxxxxxxxxxxxxx",       # API key user in-agent (Role: Sales User)
    "API_SECRET": "xxxxxxxxxxxxxxx",
    "PRINTER_HOST": "192.168.1.50",     # IP máy in ESC/POS trên LAN
    "PRINTER_PORT": 9100,
    "POLL_SECONDS": 3,
}


def auth_headers():
    return {
        "Authorization": f"token {CONFIG['API_KEY']}:{CONFIG['API_SECRET']}",
        "Accept": "application/json",
    }


def fetch_pending_orders():
    """
    Lấy các Sales Order docstatus=1 (Submitted) và custom_printed=0.
    [TODO] Hoàn thiện: gọi /api/resource/Sales Order với filters + fields,
    trả về list dict gồm name, customer, items, custom_* fields.
    """
    raise NotImplementedError


def get_order_detail(name):
    """[TODO] GET /api/resource/Sales Order/{name} → full doc kèm items."""
    raise NotImplementedError


def print_label(order):
    """
    [TODO] In tem cốc bằng python-escpos.
    Gợi ý bố cục tem (khổ hẹp ~58mm):
      - Tên quán
      - Mã đơn (order.name) + QR
      - Từng item: tên món x SL
      - Ghi chú (custom_order_note)
      - Tên KH + SĐT
    Ví dụ khung:

        from escpos.printer import Network
        p = Network(CONFIG["PRINTER_HOST"], port=CONFIG["PRINTER_PORT"], timeout=10)
        p.set(align="center", bold=True, width=2, height=2)
        p.text("NUOC EP TUOI\n")
        ...
        p.qr(order["name"], size=6)
        p.cut()

    Lưu ý: mỗi item có thể in 1 tem riêng (mỗi cốc 1 tem) — lặp theo qty.
    Xử lý lỗi kết nối máy in: bắt exception, KHÔNG set printed nếu in fail.
    """
    raise NotImplementedError


def mark_printed(name):
    """[TODO] PUT /api/resource/Sales Order/{name} set custom_printed=1."""
    raise NotImplementedError


def main_loop():
    print(f"Print Agent khởi động — máy in {CONFIG['PRINTER_HOST']}")
    while True:
        try:
            orders = fetch_pending_orders()
            for o in orders:
                detail = get_order_detail(o["name"])
                print_label(detail)          # in trước
                mark_printed(o["name"])       # in xong mới đánh dấu
                print(f"Đã in đơn {o['name']}")
        except NotImplementedError:
            print("Skeleton chưa hoàn thiện — xem PROMPT_BAN_GIAO.md")
            break
        except Exception as e:
            print(f"Lỗi vòng lặp: {e}")
        time.sleep(CONFIG["POLL_SECONDS"])


if __name__ == "__main__":
    main_loop()
