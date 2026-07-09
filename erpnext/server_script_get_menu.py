# Server Script: juice.get_menu (Allow Guest)
#
# Loại: API | API Method: juice.get_menu | Allow Guest: TICK
# Trả menu = ĐÚNG bộ hàng của POS Next: các Item Group cho phép trong POS Profile,
# giá lấy từ bảng giá của chính POS Profile. KHÔNG mở quyền đọc Item cho Guest.
#
# RestrictedPython: KHONG import, KHONG frappe._dict, KHONG set().

POS_PROFILE = "Quan Cafe - POS Chinh"

profile = frappe.get_doc("POS Profile", POS_PROFILE)
PRICE_LIST = profile.selling_price_list or "Standard Selling"

# Nhóm hàng cho phép (theo POS Profile). Rỗng => cho tất cả nhóm.
groups = []
for r in (profile.item_groups or []):
    if r.item_group and r.item_group not in groups:
        groups.append(r.item_group)

filters = {"is_sales_item": 1, "disabled": 0, "has_variants": 0}
if groups:
    filters["item_group"] = ["in", groups]

items = frappe.get_all(
    "Item",
    filters=filters,
    fields=["item_code", "item_name", "description", "image", "item_group", "standard_rate"],
    order_by="item_group asc, item_name asc",
    limit_page_length=0,
)

# Giá từ Item Price của bảng giá POS
codes = []
for i in items:
    codes.append(i["item_code"])

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
