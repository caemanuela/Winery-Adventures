"""
Base class for the components used in the Winery Adventures pipeline.

It defines the common interface that each analysis or transformation step
has to follow.
"""

from abc import ABC, abstractmethod

import polars as pl


class BaseWineryAnalyzer(ABC):
    """
    Base class for winery data analysis and transformation steps.

    Each component used in the pipeline inherits from this class and
    implements `analyze_data` to process the input DataFrame.
    """

    @abstractmethod
    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Process the input DataFrame.

        Args:
            df: DataFrame containing sensor data or the results of a
                previous pipeline step.

        Returns:
            A DataFrame containing the processed data.
        """
        pass
