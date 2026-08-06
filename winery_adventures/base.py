from abc import ABC, abstractmethod
import polars as pl

class BaseWineryAnalyzer(ABC):

    @abstractmethod
    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Metodo astratto per analizzare o trasformare il DataFrame."""
        pass
    