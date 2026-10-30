"""Task 03: if/elif/else, for and while loops with explicit stopping rules."""

stock = {"Antacid": 50, "ORS": 12, "Bandage": 0}
for item, units in stock.items():
    if units == 0:
        status = "Out of stock"
    elif units < 20:
        status = "Reorder"
    else:
        status = "Adequate"
    print(f"{item}: {status}")

remaining = 12
steps = 0
while remaining > 0:
    remaining -= min(5, remaining)
    steps += 1
print(f"While loop: {steps} steps; {remaining} units remaining")
print("Low-stock items:", [item for item, units in stock.items() if units < 20])
