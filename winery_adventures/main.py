"""
Main entry point for the Winery Adventures data processing pipeline.

This module loads the sensor data, optionally adds tank information, runs the
feature transformations and HPC computations, and saves the final results.
"""

from pathlib import Path
from typing import Optional

import polars as pl

from winery_adventures.computations import WineryHPCComputations
from winery_adventures.pipeline import WineryPipeline
from winery_adventures.transformations import WineryTransformer


def run_full_pipeline(
    input_csv: Path | str,
    output_csv: Path | str,
    tank_info_csv: Optional[Path | str] = None,
    project_name: str = "WineryAdventures",
    log_to_wandb: bool = True,
) -> pl.DataFrame:
    """
    Run the complete Winery Adventures processing pipeline.

    The function loads the sensor data and, if provided, the tank metadata.
    It then applies the transformations and HPC computations before saving
    the processed data to the specified output file.

    Args:
        input_csv: Path to the raw sensor data file.
        output_csv: Path where the processed data will be saved.
        tank_info_csv: Optional path to the tank metadata file.
        project_name: Name of the WandB project used for logging.
        log_to_wandb: Whether to log the pipeline results to WandB.

    Returns:
        The processed DataFrame containing the original data, derived
        features, and HPC computation results.

    Raises:
        FileNotFoundError: If the input sensor data file does not exist.
    """
    # Load the main sensor dataset.
    df = pl.read_csv(str(input_csv), separator="\t")

    # Load tank information only when a metadata file was provided.
    tank_info_df = None
    if tank_info_csv:
        tank_info_path = Path(tank_info_csv)
        if tank_info_path.exists():
            tank_info_df = pl.read_csv(str(tank_info_path), separator="\t")

    # Set up the transformations and HPC computations.
    transformer = WineryTransformer(tank_info_df=tank_info_df)
    computations = WineryHPCComputations()

    # Run the different processing steps in sequence.
    pipeline = WineryPipeline(
        [transformer, computations],
        project_name=project_name,
    )

    df_result = pipeline.run(df, log_to_wandb=log_to_wandb)

    # Create the output directory if needed and save the results.
    out_path = Path(output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_result.write_csv(str(out_path))

    return df_result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Process fermentation sensor data and calculate HPC stress metrics."
    )
    parser.add_argument(
        "--input-csv",
        type=str,
        required=True,
        help="Path to the raw sensor data file.",
    )
    parser.add_argument(
        "--tank-info-csv",
        type=str,
        default=None,
        help="Optional path to the tank metadata file.",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="./results.csv",
        help="Path for the final processed CSV file (default: ./results.csv).",
    )
    parser.add_argument(
        "--project-name",
        type=str,
        default="WineryAdventures",
        help="WandB project name used for experiment tracking (default: WineryAdventures).",
    )
    args = parser.parse_args()

    run_full_pipeline(
        input_csv=args.input_csv,
        tank_info_csv=args.tank_info_csv,
        output_csv=args.output_csv,
        project_name=args.project_name,
    )
