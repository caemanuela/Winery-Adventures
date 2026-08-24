import time

import numpy as np
import polars as pl

# Import the HPC implementations from the project package
from winery_adventures.computations import (
    WineryHPCComputations,
    pairwise_stress_function,
)


# Pure Python version used as a baseline for comparison
def pairwise_stress_pure(
    pH_vals: np.ndarray,
    temp_vals: np.ndarray,
    quantity_vals: np.ndarray,
) -> float:
    n = len(pH_vals)
    if n == 0:
        return 0.0

    stress_sum = 0.0

    for i in range(n):
        for j in range(n):
            pH_dev = abs(pH_vals[i] - pH_vals[j])
            t_dev = abs(temp_vals[i] - temp_vals[j]) * 2.0
            quantity_factor = (500.0 / quantity_vals[i]) + (500.0 / quantity_vals[j])
            stress_sum += (pH_dev + t_dev) * quantity_factor

    return stress_sum / (n * n)


def run_benchmarks(data_path: str = "sensors.tsv"):
    print(f"Loading dataset: {data_path}...")
    df = pl.read_csv(data_path, separator="\t")
    print(f"Dataset loaded: {df.shape[0]} rows.\n")

    # Use one large tank to compare Numba with the Python version
    tank_id_sample = df["tank_id"][0]
    tank_df = df.filter(pl.col("tank_id") == tank_id_sample)

    pH = tank_df["pH"].to_numpy()
    temp = tank_df["temp"].to_numpy()
    quantity = (
        tank_df.get_column("quantity_liters").to_numpy()
        if "quantity_liters" in tank_df.columns
        else np.full(len(pH), 500.0)
    )

    print(f"--- PHASE 1: Pure Python vs Numba ({len(pH)} readings, O(N^2)) ---")

    # Warm up Numba so the compilation time is not included
    pairwise_stress_function(pH[:10], temp[:10], quantity[:10])

    start = time.perf_counter()
    pairwise_stress_function(pH, temp, quantity)
    numba_time = time.perf_counter() - start

    print(f"Numba time (JIT)    : {numba_time:.4f} seconds")

    print("Running Pure Python (this may take a few seconds)...")
    start = time.perf_counter()
    pairwise_stress_pure(pH, temp, quantity)
    python_time = time.perf_counter() - start

    print(f"Pure Python time    : {python_time:.4f} seconds")
    print(f"Numba speedup       : {python_time / numba_time:.2f}x faster\n")

    print("--- PHASE 2: Joblib scaling (full dataset) ---")
    core_configs = [1, 2, 4, -1]

    for cores in core_configs:
        hpc = WineryHPCComputations(n_jobs=cores)

        start = time.perf_counter()
        _ = hpc.analyze_data(df)
        elapsed = time.perf_counter() - start

        core_label = "all cores" if cores == -1 else f"{cores} cores"
        print(f"Joblib with {core_label:<12} : {elapsed:.4f} seconds")


if __name__ == "__main__":
    run_benchmarks("data/full_sensors.tsv")
