from typing import List, Optional
import polars as pl
import wandb

from winery_adventures.base import BaseWineryAnalyzer

class WineryPipeline:

    def __init__(self, analyzers: Optional[List[BaseWineryAnalyzer]] = None, project_name: str = "WineryProj",):
        self.analyzers = analyzers if analyzers is not None else []
        self.project_name = project_name

    def run(self, df: pl.DataFrame, log_to_wandb: bool = False) -> pl.DataFrame:
        """Runs the pipeline by applying each analyzer in sequence to the DataFrame."""
        out_df = df
        for analyzer in self.analyzers:
            out_df = analyzer.analyze_data(out_df)

        if log_to_wandb:
            self.log_to_wandb(out_df)

        return out_df

    def log_to_wandb(self, df: pl.DataFrame):
        """Initializes a wandb run and logs the stress metric."""
        wandb.init(project=self.project_name)

        if "stress_score" in df.columns:
            # Takes the calculated stress value
            stress_val = df["stress_score"][0]
            wandb.log({"stress_score": stress_val})