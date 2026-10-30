"""Task 02: list, tuple, set and dictionary; print sets in a stable order."""

medicines = ["Antacid", "ORS", "Antacid"]
medicines.append("Bandage")
storage_range_c = (15, 25)  # A fictional tuple, not storage advice.
unique_items = set(medicines)
stock = {"Antacid": 50, "ORS": 30, "Bandage": 20}
print("List:", medicines)
print("Tuple:", storage_range_c)
print("Unique items:", sorted(unique_items))
print("ORS stock:", stock["ORS"])
print("Dictionary keys:", sorted(stock))
print("List slice:", medicines[:2])
