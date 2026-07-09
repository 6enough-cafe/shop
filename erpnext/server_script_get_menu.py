# Server Script: juice.get_menu (Allow Guest)
#
# Loại: API | API Method: juice.get_menu | Allow Guest: TICK
# Trả về danh sách món + giá đã lọc sẵn, KHÔNG mở quyền đọc Item cho Guest.

ALLOWED_GROUP = "Nước Ép"
PRICE_LIST = "Standard Selling"

items = frappe.get_all(
    "Item",
    filters={
        "item_group": ALLOWED_GROUP,
        "is_sales_item": 1,
        "disabled": 0,
    },
    fields=["item_code", "item_name", "description", "image", "item_group", "standard_rate"],
    limit_page_length=0,
)

# Lấy giá từ Item Price
codes = [i["item_code"] for i in items]
price_map = {}
if codes:
    prices = frappe.get_all(
        "Item Price",
        filters={"price_list": PRICE_LIST, "item_code": ["in", codes]},
        fields=["item_code", "price_list_rate"],
        limit_page_length=0,
    )
    for p in prices:
        price_map[p["item_code"]] = p["price_list_rate"]

result = []
for i in items:
    result.append({
        "item_code": i["item_code"],
        "item_name": i["item_name"],
        "description": i.get("description"),
        "image": i.get("image"),
        "item_group": i["item_group"],
        "price": price_map.get(i["item_code"], i.get("standard_rate") or 0),
    })

frappe.response["message"] = result
