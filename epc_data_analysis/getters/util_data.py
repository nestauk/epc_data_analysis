import pandas as pd
import os

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR

# Load config file
data_config = get_yaml_config(
    Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml")
)

# Get paths
location_path = str(PROJECT_DIR) + data_config["POSTCODE_PATH"]
WIMD_path = str(PROJECT_DIR) + data_config["WIMD_PATH"]


def get_location_data():
    """Load location data (postcode, latitude, longitude).

    Parameters
    ----------
        None

    Return
    ---------
        location_data_df: pandas.DateFrame
        Location data (postcode, latitude, longitude).
    """

    # Load data
    location_data_df = pd.read_csv(location_path)

    # Remove ID (not necessary and conflicts with EPC dataframe)
    del location_data_df["id"]

    # Rename columns to match EPC data
    location_data_df = location_data_df.rename(
        columns={
            "postcode": "POSTCODE",
            "latitude": "LATITUDE",
            "longitude": "LONGITUDE",
        }
    )
    return location_data_df


def get_WIMD_data():
    """Load Wales Index of Multiple Deprivation (WIMD).

    Parameters
    ----------
        None

    Return
    ---------
        wimd_df: pandas.DateFrame
        Wales Index of Multiple Deprivation data."""

    # Load data
    wimd_df = pd.read_csv(WIMD_path)
    return wimd_df


def merge_dataframes(df1, df2, merge_feature):
    """Merge dataframes based on given feature/column.

    Parameters
    ----------
        df1: pandas.Dataframe
        First dataframe to be merged with second dataframe.

        df2: pandas.Dataframe
        Second dataframe to be merged with first dataframe.

        merge_feature: string
        Feature/column used to merge two dataframes.

    Return
    ---------
        merged_df: pandas.DateFrame
        Merged new dataframe."""

    # Fix postcode format before merging
    if merge_feature == "POSTCODE":

        df1["POSTCODE"] = df1["POSTCODE"].str.replace(r" ", "")
        df2["POSTCODE"] = df2["POSTCODE"].str.replace(r" ", "")

    # Merge datasets
    merged_df = pd.merge(df1, df2, on=[merge_feature])

    return merged_df
