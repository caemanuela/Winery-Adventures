"""
Script to generate benchmark charts for Winery Adventures.
Visualizes performance for Joblib (CPU parallelism) and Numba (JIT compilation).
High-contrast, colorblind-friendly feminine palette.
"""

import platform
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_joblib_benchmark(csv_path: Path | str, output_path: Path | str) -> None:
    """Generates the plot for Joblib performance benchmarks.

    Args:
        csv_path (Path | str): Path to the CSV containing Joblib benchmark metrics.
        output_path (Path | str): Destination path for the generated PNG chart.
    """
    df = pd.read_csv(csv_path)

    sns.set_theme(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(8, 5))

    # High-contrast color choices: Dark Plum bars vs Bright Hot Pink line
    color_bar = "#4A154B"  # Dark Plum (High density, very dark)
    color_line = "#FF1493"  # Deep Hot Pink / Vibrant Magenta (Bright, high visibility)

    # Primary Y-axis: Execution Time (seconds)
    ax1.set_xlabel("CPU Configuration (n_jobs)", fontweight="bold", fontsize=11)
    ax1.set_ylabel(
        "Execution Time (seconds)", color=color_bar, fontweight="bold", fontsize=11
    )
    bars = ax1.bar(
        df["n_jobs"].astype(str),  # Cast to string for categorical plotting
        df["execution_time_seconds"],
        color=color_bar,
        alpha=0.9,
        width=0.4,
    )
    ax1.tick_params(axis="y", labelcolor=color_bar)

    # Secondary Y-axis: Speedup vs 1 core
    ax2 = ax1.twinx()
    ax2.set_ylabel(
        "Speedup (vs 1 core)", color=color_line, fontweight="bold", fontsize=11
    )
    ax2.plot(
        df["n_jobs"].astype(str),
        df["speedup_vs_1_core"],
        color=color_line,
        marker="o",
        markersize=8,
        linewidth=3.0,
    )
    ax2.tick_params(axis="y", labelcolor=color_line)

    # Add numeric data labels above bars (Dark color for high readability)
    for bar in bars:
        yval = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 0.1,
            f"{yval:.2f}s",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#222222",
        )

    plt.title(
        "Joblib Benchmark: Execution time & Speedup",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_numba_benchmark(csv_path: Path | str, output_path: Path | str) -> None:
    """Generates the plot for Numba JIT performance benchmarks.

    Args:
        csv_path (Path | str): Path to the CSV containing Numba benchmark metrics.
        output_path (Path | str): Destination path for the generated PNG chart.
    """
    df = pd.read_csv(csv_path)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(7, 5))

    # Colorblind-safe palette: Light Soft Pink vs Very Dark Wine/Plum
    # Extreme contrast in lightness and color saturation
    color_python = "#F4C2C2"  # Soft Baby Pink / Rose (Very Light)
    color_numba = "#581845"  # Deep Wine / Burgundy (Very Dark)

    bars = ax.bar(
        df["implementation"],
        df["execution_time_seconds"],
        color=[color_python, color_numba],
        width=0.45,
        edgecolor="#333333",  # Dark border to enhance shape definition
        linewidth=1.2,
    )

    ax.set_yscale("log")
    ax.set_ylabel(
        "Execution time in seconds (log scale)", fontweight="bold", fontsize=11
    )
    ax.set_title(
        "Numba JIT vs Pure Python Benchmark",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )

    # Add text labels above bars
    for bar in bars:
        yval = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval * 1.3,
            f"{yval:.4f}s",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#111111",
        )

    # High-contrast annotation box (Safe extraction)
    if "speedup_vs_python" in df.columns:
        speedup_series = df.loc[
            df["implementation"].str.contains("Numba", case=False, na=False),
            "speedup_vs_python",
        ]
        speedup_val = speedup_series.values[0] if not speedup_series.empty else 0.0
    else:
        speedup_val = 0.0

    ax.text(
        0.5,
        0.5,
        f"Numba Speedup: ~{speedup_val:.0f}x",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color="#33001B",
        bbox=dict(
            boxstyle="round,pad=0.6",
            facecolor="#FFE6F0",
            edgecolor="#900C3F",
            linewidth=1.5,
            alpha=0.9,
        ),
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


if __name__ == "__main__":
    # Dynamically locate the project root directory relative to this script's location
    base_dir = Path(__file__).resolve().parent

    # Detect the operating system (e.g., 'darwin', 'windows', 'linux')
    os_name = platform.system().lower()

    # Input CSV file paths
    reports_dir = base_dir / "docs" / "reports"
    joblib_csv = reports_dir / f"benchmark_joblib_scaling_{os_name}.csv"
    numba_csv = reports_dir / f"benchmark_numba_vs_python_{os_name}.csv"

    # Output directory path
    output_dir = base_dir / "docs" / "data_visualization"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate Joblib plot appending OS name
    if joblib_csv.exists():
        out_file = output_dir / f"joblib_benchmark_{os_name}.png"
        plot_joblib_benchmark(joblib_csv, output_path=out_file)
        print(f"Joblib chart successfully saved to: {out_file}")
    else:
        print(f"ERROR: Could not find file {joblib_csv}")

    # Generate Numba plot appending OS name
    if numba_csv.exists():
        out_file = output_dir / f"numba_benchmark_{os_name}.png"
        plot_numba_benchmark(numba_csv, output_path=out_file)
        print(f"Numba chart successfully saved to: {out_file}")
    else:
        print(f"ERROR: Could not find file {numba_csv}")
