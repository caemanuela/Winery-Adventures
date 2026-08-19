"""
Pipeline for running the different processing steps of the project.

This module contains the WineryPipeline class, which applies the analysis
and transformation steps in order and can optionally log results to WandB.
"""

from typing import List, Optional

import polars as pl

import wandb
from winery_adventures.base import BaseWineryAnalyzer


class WineryPipeline:
    """
    Run the analysis and transformation steps of the project.

    Each analyzer receives the DataFrame produced by the previous step.
    The pipeline can also send the final results to WandB for tracking.

    Attributes:
        analyzers: List of processing steps to run.
        project_name: Name of the WandB project used for logging.
    """

    def __init__(
        self,
        analyzers: Optional[List[BaseWineryAnalyzer]] = None,
        project_name: str = "WineryProj",
    ) -> None:
        """
        Create a new pipeline.

        Args:
            analyzers: Optional list of analyzers to run in order.
                Defaults to an empty list.
            project_name: Name of the WandB project used for logging.
                Defaults to "WineryProj".
        """
        self.analyzers = analyzers if analyzers is not None else []
        self.project_name = project_name

    def run(self, df: pl.DataFrame, log_to_wandb: bool = False) -> pl.DataFrame:
        """
        Run all the analyzers on the input data.

        Each step works on the output of the previous one. WandB logging
        is performed after all the processing steps have finished.

        Args:
            df: Input DataFrame containing the sensor or tank data.
            log_to_wandb: Whether to log the final results to WandB.

        Returns:
            The DataFrame after all pipeline steps have been applied.
        """
        out_df = df

        # Pass the data through the analyzers one step at a time.
        for analyzer in self.analyzers:
            out_df = analyzer.analyze_data(out_df)

        if log_to_wandb:
            self.log_to_wandb(out_df)

        return out_df

    def log_to_wandb(self, df: pl.DataFrame) -> None:
        """
        Log the stress score to WandB.

        A new WandB run is created using the configured project name.
        If a stress score is available, the first value is logged.

        Args:
            df: DataFrame containing the results of the pipeline.
        """
        wandb.init(project=self.project_name)

        if "stress_score" in df.columns and len(df) > 0:
            stress_val = df["stress_score"][0]
            wandb.log({"stress_score": stress_val})
