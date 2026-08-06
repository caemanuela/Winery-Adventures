from abc import ABC, abstractmethod
import polars as pl

class BaseWineryAnalyzer(ABC):

    @abstractmethod
    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Abstract method to analyze or transform the DataFrame."""
        pass