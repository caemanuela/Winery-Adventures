"""
Feature engineering for winery sensor data.

This module contains the WineryTransformer class, which adds useful features
to the raw fermentation data, such as tank-level statistics, grape variety
information, and temperature deviations.
"""

from typing import Optional

import polars as pl

from winery_adventures.base import BaseWineryAnalyzer


class WineryTransformer(BaseWineryAnalyzer):
    """
    Add derived features to fermentation sensor data.

    The transformer calculates statistics for each tank, combines the sensor
    data with tank information when available, and measures how far the
    recorded temperature is from the reference fermentation temperature.

    Attributes:
        STANDARD_TEMPERATURE: Reference temperature used to calculate
            temperature deviations, in °C.
        tank_info_df: Optional DataFrame containing information about the tanks
            and their grape varieties.
    """

    STANDARD_TEMPERATURE: float = 26.0

    def __init__(self, tank_info_df: Optional[pl.DataFrame] = None) -> None:
        """
        Create a new transformer.

        Args:
            tank_info_df: Optional DataFrame with tank information, such as
                tank IDs, grape varieties, and tank capacity.
        """
        self.tank_info_df = tank_info_df

    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Apply the feature transformations to the sensor data.

        The transformations add the average pH and number of readings for
        each tank, grape variety reading counts when tank information is
        available, and the temperature deviation from the reference value.

        Args:
            df: DataFrame containing the raw sensor measurements.

        Returns:
            The input DataFrame with the new feature columns added.
        """
        df_out = self.add_avg_ph_per_tank(df)
        df_out = self.add_num_readings_per_tank(df_out)

        if self.tank_info_df is not None:
            df_out = self.add_num_readings_per_grape_variety(df_out)

        df_out = self.add_temperature_deviation(df_out)
        return df_out

    def add_avg_ph_per_tank(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Add the average pH recorded for each tank.

        Args:
            df: DataFrame containing `tank_id` and `pH` columns.

        Returns:
            DataFrame with an `avg_pH_per_tank` column.
        """
        return df.with_columns(
            pl.col("pH").mean().over("tank_id").alias("avg_pH_per_tank")
        )

    def add_num_readings_per_tank(self, df: pl.DataFrame) -> pl.DataFrame:
        """Add the total number of sensor readings for each tank.

        Args:
            df: DataFrame containing a `tank_id` column.

        Returns:
            DataFrame with a `tank_num_readings` column.
        """
        return df.with_columns(pl.len().over("tank_id").alias("tank_num_readings"))

    def add_num_readings_per_grape_variety(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Add the number of sensor readings associated with each grape variety.

        Tank information is joined to the sensor data first. If a tank contains
        more than one grape variety, the varieties are split into separate
        rows before counting the readings.

        Args:
            df: DataFrame containing sensor readings and `tank_id`.

        Returns:
            DataFrame with tank information and a
            `grape_variety_num_readings` column.

        Raises:
            AttributeError: If no tank information was provided when creating
                the transformer.
        """
        if self.tank_info_df is None:
            raise AttributeError("`tank_info_df` was not provided to the constructor!")

        tank_info = self.tank_info_df

        # Convert comma-separated varieties into a list first.
        if (
            tank_info["grape_variety"].dtype == pl.Utf8
            or tank_info["grape_variety"].dtype == pl.String
        ):
            tank_info = tank_info.with_columns(pl.col("grape_variety").str.split(","))

        # Put each grape variety on its own row.
        if tank_info["grape_variety"].dtype == pl.List:
            tank_info = tank_info.explode("grape_variety", empty_as_null=True)

        # Add the tank information to the sensor readings.
        joined_df = df.join(tank_info, on="tank_id", how="left")

        # Count how many readings are associated with each grape variety.
        return joined_df.with_columns(
            pl.len().over("grape_variety").alias("grape_variety_num_readings")
        )

    def add_temperature_deviation(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Calculate how far the recorded temperature is from the reference value.

        When the liquid volume is available, the deviation is adjusted based
        on the volume of the batch, using 1000 liters as the reference size.

        Args:
            df: DataFrame containing a `temp` column and, optionally,
                `quantity_liters`.

        Returns:
            DataFrame with either `temperature_deviation_scaled` or
            `temperature_deviation`, depending on whether volume information
            is available.
        """
        dev_expr = (pl.col("temp") - self.STANDARD_TEMPERATURE).abs()

        if "quantity_liters" in df.columns:
            return df.with_columns(
                (dev_expr * (1000.0 / pl.col("quantity_liters"))).alias(
                    "temperature_deviation_scaled"
                )
            )

        return df.with_columns(dev_expr.alias("temperature_deviation"))
