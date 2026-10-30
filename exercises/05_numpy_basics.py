"""Task 05: array construction, slicing, vectorization, axes and ddof."""

import numpy as np

sales = np.array([10, 12, 8, 15, 5])
print("Array:", sales.tolist())
print("First three:", sales[:3].tolist())
print("After adding 2:", (sales + 2).tolist())
print(f"Mean={sales.mean():.2f}; sample SD={sales.std(ddof=1):.3f}")
matrix = np.array([[10, 12], [8, 15], [5, 10]])
print("Shape:", matrix.shape)
print("Column totals (axis=0):", matrix.sum(axis=0).tolist())
