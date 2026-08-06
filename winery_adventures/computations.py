import polars as pl
import numpy as np
from numba import jit
from winery_adventures.base import BaseWineryAnalyzer

@jit(nopython=True)
def pairwise_stress_function(
    pH_vals: np.ndarray, temp_vals: np.ndarray, quantity_vals: np.ndarray
) -> float:
    """Compute stress score with O(n^2) complexity"""
    n = len(pH_vals)
    if n == 0:
        return 0.0

    stress_sum = 0.0

    # Compute pairwise stress
    for i in range(n):
        for j in range(n):
            pH_dev = abs(pH_vals[i] - pH_vals[j])
            t_dev = abs(temp_vals[i] - temp_vals[j]) * 2.0
            quantity_factor = (500.0 / quantity_vals[i]) + (500.0 / quantity_vals[j])

            stress_sum += (pH_dev + t_dev) * quantity_factor

    # Final stress score is the average of all pairwise stress values
    return stress_sum / (n * n)

class WineryHPCComputations(BaseWineryAnalyzer):
    
    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Reads DataFrame and creates a new column with stress score for each row"""
        ph_vals = df["pH"].to_numpy()
        temp_vals = df["temp"].to_numpy()

        # Handle missing quantity or capacity values
        if "quantity_liters" in df.columns:
            quantity_vals = df["quantity_liters"].fill_null(500.0).to_numpy()
        elif "capacity_liters" in df.columns:
            quantity_vals = df["capacity_liters"].fill_null(500.0).to_numpy()
        else:
            quantity_vals = np.full(len(df), 500.0)  # Default quantity if not provided
        # Convert to float64 for Numba compatibility
        ph_vals = ph_vals.astype(np.float64)
        temp_vals = temp_vals.astype(np.float64)
        quantity_vals = quantity_vals.astype(np.float64)
        # Compute the stress score using the pairwise_stress_function
        score = pairwise_stress_function(ph_vals, temp_vals, quantity_vals)
        # Add the stress score as a new column to the DataFrame
        return df.with_columns(pl.lit(score).alias("stress_score"))