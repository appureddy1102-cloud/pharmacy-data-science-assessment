"""Task 06: DataFrame, Series, filtering, .loc, derived columns and groupby."""

import pandas as pd

stock = pd.DataFrame(
    {
        "item": ["Antacid", "ORS", "Bandage"],
        "category": ["Medicine", "Medicine", "Supply"],
        "units": [50, 12, 20],
        "unit_price_inr": [3.0, 5.0, 8.0],
    }
)
stock["value_inr"] = stock["units"] * stock["unit_price_inr"]
print("Shape:", stock.shape)
print("Units Series:", stock["units"].tolist())
print("Filtered rows:")
print(stock.loc[stock["units"] < 20, ["item", "units"]].to_string(index=False))
print("Value by category:")
print(stock.groupby("category")["value_inr"].sum().to_string())
