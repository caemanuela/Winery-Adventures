"""
HPC computations for fermentation stress analysis.

This module calculates a stress score for each fermentation tank. Numba is
used to speed up the pairwise calculations, while Joblib allows the tanks
to be processed in parallel.
"""

import joblib
import numpy as np
import polars as pl
from numba import jit

from winery_adventures.base import BaseWineryAnalyzer


@jit(nopython=True)
def pairwise_stress_function(
    pH_vals: np.ndarray, temp_vals: np.ndarray, quantity_vals: np.ndarray
) -> float:
    """
    Calculate a stress score from the sensor readings of a tank.

    The score is based on the differences in pH and temperature between all
    pairs of observations. Temperature differences have a higher weight,
    while smaller batch volumes increase the contribution to the score.

    The calculation has O(n²) complexity because every observation is
    compared with every other observation.

    Args:
        pH_vals: Array of pH readings.
        temp_vals: Array of temperature readings in °C.
        quantity_vals: Array of batch volumes in liters.

    Returns:
        The calculated stress score, or 0.0 if there are no observations.
    """
    n = len(pH_vals)
    if n == 0:
        return 0.0

    stress_sum = 0.0

    # Compare every pair of observations.
    for i in range(n):
        for j in range(n):
            pH_dev = abs(pH_vals[i] - pH_vals[j])
            t_dev = abs(temp_vals[i] - temp_vals[j]) * 2.0
            quantity_factor = (500.0 / quantity_vals[i]) + (500.0 / quantity_vals[j])

            stress_sum += (pH_dev + t_dev) * quantity_factor

    # Average the result over all pairs.
    return stress_sum / (n * n)


def _compute_tank_stress_score(df_tank: pl.DataFrame) -> float:
    """
    Calculate the stress score for one tank.

    The sensor values are converted to NumPy arrays so they can be passed
    to the Numba-compiled function. If the batch volume is missing, a
    default value of 500 liters is used.

    Args:
        df_tank: DataFrame containing the readings for one tank.

    Returns:
        The stress score calculated for the tank.
    """
    ph_vals = df_tank["pH"].to_numpy().astype(np.float64)
    temp_vals = df_tank["temp"].to_numpy().astype(np.float64)

    if "quantity_liters" in df_tank.columns:
        quantity_vals = (
            df_tank["quantity_liters"].fill_null(500.0).to_numpy().astype(np.float64)
        )
    elif "capacity_liters" in df_tank.columns:
        quantity_vals = (
            df_tank["capacity_liters"].fill_null(500.0).to_numpy().astype(np.float64)
        )
    else:
        quantity_vals = np.full(len(df_tank), 500.0, dtype=np.float64)

    return float(pairwise_stress_function(ph_vals, temp_vals, quantity_vals))


class WineryHPCComputations(BaseWineryAnalyzer):
    """
    Calculate fermentation stress scores for each tank.

    Each tank is processed separately and the calculations are distributed
    across multiple CPU workers using Joblib.

    Attributes:
        n_jobs: Number of parallel workers. A value of -1 uses all available
            CPU cores.
    """

    def __init__(self, n_jobs: int = -1) -> None:
        """
        Create a new HPC computation analyzer.

        Args:
            n_jobs: Number of jobs that can run at the same time.
                Defaults to -1, which uses all available CPU cores.
        """
        self.n_jobs = n_jobs

    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Calculate a stress score for each tank and add it to the data.

        The data is split by tank, each tank is processed independently,
        and the resulting scores are joined back to the original DataFrame.

        Args:
            df: DataFrame containing sensor readings and a `tank_id` column.

        Returns:
            DataFrame with an additional `stress_score` column.
        """
        if df.is_empty():
            return df.with_columns(pl.lit(0.0).alias("stress_score"))

        unique_tanks = df["tank_id"].unique().to_list()
        tank_dfs = [df.filter(pl.col("tank_id") == tid) for tid in unique_tanks]

        # Process the tanks in parallel.
        parallel_out = joblib.Parallel(n_jobs=self.n_jobs)(
            joblib.delayed(_compute_tank_stress_score)(t_df) for t_df in tank_dfs
        )

        # Use the sequential version if the parallel call did not return results.
        if parallel_out is not None and len(parallel_out) == len(unique_tanks):
            scores = list(parallel_out)
        else:
            scores = [_compute_tank_stress_score(t_df) for t_df in tank_dfs]

        # Create a small table that maps each tank to its stress score.
        stress_mapping_df = pl.DataFrame(
            {
                "tank_id": unique_tanks,
                "stress_score": scores,
            },
            schema={"tank_id": df["tank_id"].dtype, "stress_score": pl.Float64},
        )

        return df.join(stress_mapping_df, on="tank_id", how="left")
