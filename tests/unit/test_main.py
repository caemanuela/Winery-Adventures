"""
Tests for the CLI runner and the main data processing pipeline.
"""

import runpy
import sys
from unittest.mock import patch

from winery_adventures.main import run_full_pipeline


def test_run_full_pipeline_without_tank_info(tmp_path, monkey_wandb_run, sensors_df):
    """
    Check that the pipeline runs correctly without tank metadata.

    The test verifies that the output file is created and that the main
    transformation and stress score columns are added to the data.
    """
    sensor_tsv = tmp_path / "sensors.tsv"
    sensor_tsv.write_text(sensors_df.write_csv(separator="\t"))

    output_csv = tmp_path / "results.csv"

    df_out = run_full_pipeline(
        input_csv=str(sensor_tsv),
        output_csv=str(output_csv),
        tank_info_csv=None,
        project_name="TestNoInfo",
        log_to_wandb=False,
    )

    assert output_csv.exists(), "Output CSV file was not created"
    assert "avg_pH_per_tank" in df_out.columns
    assert "stress_score" in df_out.columns
    assert df_out.shape[0] == sensors_df.shape[0]


def test_run_full_pipeline_with_path_objects(
    tmp_path, monkey_wandb_run, sensors_df, tank_info_df
):
    """
    Check that the pipeline accepts Path objects and tank metadata.

    The test also checks that the output file is created inside a directory
    that does not exist yet.
    """
    sensor_tsv = tmp_path / "sensors.tsv"
    sensor_tsv.write_text(sensors_df.write_csv(separator="\t"))

    info_tsv = tmp_path / "tank_info.tsv"
    info_tsv.write_text(tank_info_df.write_csv(separator="\t"))

    output_csv = tmp_path / "subdir" / "results.csv"

    df_out = run_full_pipeline(
        input_csv=sensor_tsv,
        output_csv=output_csv,
        tank_info_csv=info_tsv,
        project_name="TestPathObj",
        log_to_wandb=True,
    )

    assert output_csv.exists(), "Nested output CSV was not created"
    assert df_out.shape[0] == 9


def test_main_cli_execution_with_tank_info(
    tmp_path, monkey_wandb_run, sensors_df, tank_info_df
):
    """
    Check that the CLI accepts the input, tank metadata, output, and project
    name arguments and produces the expected output file.
    """
    sensor_tsv = tmp_path / "cli_sensors.tsv"
    sensor_tsv.write_text(sensors_df.write_csv(separator="\t"))

    info_tsv = tmp_path / "cli_tank_info.tsv"
    info_tsv.write_text(tank_info_df.write_csv(separator="\t"))

    output_csv = tmp_path / "cli_results.csv"

    test_args = [
        "main.py",
        "--input-csv",
        str(sensor_tsv),
        "--tank-info-csv",
        str(info_tsv),
        "--output-csv",
        str(output_csv),
        "--project-name",
        "CliTestProject",
    ]

    with patch.object(sys, "argv", test_args):
        sys.modules.pop("winery_adventures.main", None)
        runpy.run_module("winery_adventures.main", run_name="__main__")

    assert output_csv.exists()


def test_main_cli_execution_defaults(tmp_path, monkey_wandb_run, sensors_df):
    """
    Check that the CLI works when only the required input argument is given.

    The test verifies that the output file is created using the provided
    output path.
    """
    sensor_tsv = tmp_path / "cli_sensors_default.tsv"
    sensor_tsv.write_text(sensors_df.write_csv(separator="\t"))
    default_out = tmp_path / "results.csv"

    test_args = [
        "main.py",
        "--input-csv",
        str(sensor_tsv),
        "--output-csv",
        str(default_out),
    ]

    with patch.object(sys, "argv", test_args):
        sys.modules.pop("winery_adventures.main", None)
        runpy.run_module("winery_adventures.main", run_name="__main__")

    assert default_out.exists()
