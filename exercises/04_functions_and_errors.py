"""Task 04: a reusable function, a docstring and specific exception handling."""


def inventory_value(units: int, price: float) -> float:
    """Return INR stock value for non-negative units and unit price."""
    if units < 0 or price < 0:
        raise ValueError("Units and price cannot be negative.")
    return units * price


print(f"Valid value: INR {inventory_value(120, 2.5):.2f}")
try:
    inventory_value(-5, 2.5)
except ValueError as error:
    print("Handled validation error:", error)

try:
    units = int("twelve")
except ValueError:
    print("Handled conversion error: enter a whole number, for example 12.")
finally:
    print("Input check completed.")
