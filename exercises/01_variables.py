"""Task 01: variables, basic types and pharmacy stock arithmetic."""

medicine = "Paracetamol (fictional stock item)"
stock_units = 120
unit_price_inr = 2.50
requires_cold_chain = False
print(f"Medicine: {medicine}")
print(
    f"Types: {type(medicine).__name__}, {type(stock_units).__name__}, "
    f"{type(unit_price_inr).__name__}, {type(requires_cold_chain).__name__}"
)
print(f"Inventory value: INR {stock_units * unit_price_inr:.2f}")
print(f"After selling 15 units: {stock_units - 15} units")
