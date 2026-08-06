#TODO: creare funzioni BaseWineryAnalyzer
from abc import ABC, abstractmethod
import polars as pl

class BaseWineryAnalyzer(ABC):
    @abstractmethod
    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        pass