"""Script to run performance benchmarks for Winery Adventures.

Evaluates execution times and memory peaks for Numba JIT vs Pure Python,
and scales across multiple CPU cores using Joblib.
"""

import platform
import time
import tracemalloc
from pathlib import Path
from typing import Union

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
    """Pure Python implementation of the pairwise stress function (O(n^2)).

    Args:
        pH_vals (np.ndarray): Array of pH measurements.
        temp_vals (np.ndarray): Array of temperature measurements.
        quantity_vals (np.ndarray): Array of quantity (liters) measurements.

    Returns:
        float: The calculated fermentation stress index.
    """
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


def run_benchmarks(data_path: Union[Path, str] = "data/full_sensors.tsv") -> None:
    """Runs the benchmark suite and saves results to CSV files.

    Args:
        data_path (Union[Path, str]): Path to the dataset used for testing.
    """
    # Dynamic paths and OS detection
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "docs" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    os_name = platform.system().lower()

    dataset_file = base_dir / data_path
    print(f"Loading dataset: {dataset_file}...")
    df = pl.read_csv(dataset_file, separator="\t")
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

    print(f"PHASE 1: Pure Python vs Numba ({len(pH)} readings, O(N^2))")

    # Warm up Numba so the compilation time is not included
    pairwise_stress_function(pH[:10], temp[:10], quantity[:10])

    # Benchmark Numba (time + memory)
    tracemalloc.start()
    start = time.perf_counter()
    pairwise_stress_function(pH, temp, quantity)
    numba_time = time.perf_counter() - start
    _, peak_numba = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(
        f"Numba time (JIT): {numba_time:.4f} seconds | Peak RAM: {peak_numba / 10**6:.2f} MB"
    )

    print("Running Pure Python (this may take a few seconds)...")
    # Benchmark Pure Python (time + memory)
    tracemalloc.start()
    start = time.perf_counter()
    pairwise_stress_pure(pH, temp, quantity)
    python_time = time.perf_counter() - start
    _, peak_python = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    speedup = python_time / numba_time if numba_time > 0 else 0.0
    print(
        f"Pure Python time  : {python_time:.4f} seconds | Peak RAM: {peak_python / 10**6:.2f} MB"
    )
    print(f"Numba speedup     : {speedup:.2f}x faster\n")

    # Save Phase 1 benchmark results
    phase1_df = pl.DataFrame(
        {
            "implementation": ["Pure Python", "Numba (JIT)"],
            "readings_count": [len(pH), len(pH)],
            "execution_time_seconds": [python_time, numba_time],
            "speedup_vs_python": [1.0, speedup],
            "peak_memory_mb": [peak_python / 10**6, peak_numba / 10**6],
        }
    )
    phase1_csv = output_dir / f"benchmark_numba_vs_python_{os_name}.csv"
    phase1_df.write_csv(phase1_csv)

    print("PHASE 2: Joblib scaling (full dataset)")
    core_configs = [1, 2, 4, -1]
    scaling_records = []
    base_time_1_core = None

    for cores in core_configs:
        hpc = WineryHPCComputations(n_jobs=cores)

        start = time.perf_counter()
        _ = hpc.analyze_data(df)
        elapsed = time.perf_counter() - start

        if cores == 1:
            base_time_1_core = elapsed

        scaling_speedup = (base_time_1_core / elapsed) if base_time_1_core else 1.0
        core_label = "all cores" if cores == -1 else f"{cores} cores"
        print(f"Joblib with {core_label:<12} : {elapsed:.4f} seconds")

        scaling_records.append(
            {
                "n_jobs": core_label,
                "total_dataset_rows": df.shape[0],
                "execution_time_seconds": elapsed,
                "speedup_vs_1_core": scaling_speedup,
            }
        )

    # Save Phase 2 benchmark results
    phase2_df = pl.DataFrame(scaling_records)
    phase2_csv = output_dir / f"benchmark_joblib_scaling_{os_name}.csv"
    phase2_df.write_csv(phase2_csv)
    print(f"\nResults saved to '{output_dir}/'.")


if __name__ == "__main__":
    run_benchmarks("data/full_sensors.tsv")
