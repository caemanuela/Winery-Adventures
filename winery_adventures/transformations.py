from typing import Optional
import polars as pl
from winery_adventures.base import BaseWineryAnalyzer


class WineryTransformer(BaseWineryAnalyzer):
    STANDARD_TEMPERATURE: float = 26.0

    def __init__(self, tank_info_df: Optional[pl.DataFrame] = None):
        self.tank_info_df = tank_info_df

    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Applica in sequenza tutte le trasformazioni."""
        df_out = self.add_avg_ph_per_tank(df)
        df_out = self.add_num_readings_per_tank(df_out)
        df_out = self.add_num_readings_per_grape_variety(df_out)
        df_out = self.add_temperature_deviation(df_out)
        return df_out

    def add_avg_ph_per_tank(self, df: pl.DataFrame) -> pl.DataFrame:
        """Calcola la media del pH per ogni tank_id."""
        return df.with_columns(
            pl.col("pH").mean().over("tank_id").alias("avg_pH_per_tank")
        )

    def add_num_readings_per_tank(self, df: pl.DataFrame) -> pl.DataFrame:
        """Conta le letture dei sensori per ogni tank_id."""
        return df.with_columns(
            pl.len().over("tank_id").alias("tank_num_readings")
        )

    def add_num_readings_per_grape_variety(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Unisce tank_info_df per ottenere grape_variety e conta le letture aggregate.
        Gestisce la presenza di liste nella colonna grape_variety tramite explode.
        """
        if self.tank_info_df is None:
            raise AttributeError("`tank_info_df` non è stato fornito al costruttore!")

        # Se grape_variety contiene liste, spacchettale (explode)
        tank_info = self.tank_info_df
        if tank_info["grape_variety"].dtype == pl.List:
            tank_info = tank_info.explode("grape_variety", empty_as_null=True)

        # Join tra i sensori e le info dei serbatoi
        joined_df = df.join(tank_info, on="tank_id", how="left")

        # Conteggio delle letture per varietà d'uva
        return joined_df.with_columns(
            pl.len().over("grape_variety").alias("grape_variety_num_readings")
        )

    def add_temperature_deviation(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Calcola lo scostamento dalla temperatura standard (26.0).
        Se 'quantity_liters' è presente, scala lo scostamento dividendolo per 1000.0.
        """
        dev_expr = (pl.col("temp") - self.STANDARD_TEMPERATURE).abs()

        if "quantity_liters" in df.columns:
            return df.with_columns(
                (dev_expr * ( 1000.0 / pl.col("quantity_liters"))).alias("temperature_deviation_scaled")
            )
        else:
            return df.with_columns(
                dev_expr.alias("temperature_deviation")
            )