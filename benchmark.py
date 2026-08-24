from pathlib import Path
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


def run_benchmarks(data_path: str = "sensors.tsv") -> None:
    output_dir = Path("docs/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

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

    print(f"PHASE 1: Pure Python vs Numba ({len(pH)} readings, O(N^2))")

    # Warm up Numba so the compilation time is not included
    pairwise_stress_function(pH[:10], temp[:10], quantity[:10])

    start = time.perf_counter()
    pairwise_stress_function(pH, temp, quantity)
    numba_time = time.perf_counter() - start

    print(f"Numba time (JIT): {numba_time:.4f} seconds")

    print("Running Pure Python (this may take a few seconds)...")
    start = time.perf_counter()
    pairwise_stress_pure(pH, temp, quantity)
    python_time = time.perf_counter() - start

    speedup = python_time / numba_time if numba_time > 0 else 0.0
    print(f"Pure Python time     : {python_time:.4f} seconds")
    print(f"Numba speedup        : {speedup:.2f}x faster\n")

    # Save Phase 1 benchmark results
    phase1_df = pl.DataFrame({
        "implementation": ["Pure Python", "Numba (JIT)"],
        "readings_count": [len(pH), len(pH)],
        "execution_time_seconds": [python_time, numba_time],
        "speedup_vs_python": [1.0, speedup],
    })
    phase1_df.write_csv(output_dir / "benchmark_numba_vs_python.csv")

    print("PHASE 2: Joblib scaling (full dataset)")
    core_configs = [1, 2, 4, -1]
    scaling_records = []
    base_time_1_core: float | None = None

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

        scaling_records.append({
            "n_jobs": core_label,
            "total_dataset_rows": df.shape[0],
            "execution_time_seconds": elapsed,
            "speedup_vs_1_core": scaling_speedup,
        })

    # Save Phase 2 benchmark results
    phase2_df = pl.DataFrame(scaling_records)
    phase2_df.write_csv(output_dir / "benchmark_joblib_scaling.csv")
    print(f"\nResults saved to '{output_dir}/'.")


if __name__ == "__main__":
    run_benchmarks("data/full_sensors.tsv")