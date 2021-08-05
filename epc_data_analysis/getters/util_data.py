import pandas as pd
import os

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR

# Load config file
data_config = get_yaml_config(
    Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml")
)

# Get paths
LOCATION_PATH = str(PROJECT_DIR) + data_config["POSTCODE_PATH"]
WIMD_PATH = str(PROJECT_DIR) + data_config["WIMD_PATH"]


def get_location_data():
    """Load location data (postcode, latitude, longitude).

    Parameters
    ----------
    None

    Return
    ---------
    location_data_df : pandas.DateFrame
        Location data (postcode, latitude, longitude).
    """

    # Load data
    location_data_df = pd.read_csv(LOCATION_PATH)

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
    wimd_df : pandas.DateFrame
        Wales Index of Multiple Deprivation data."""

    # Load data
    wimd_df = pd.read_csv(WIMD_PATH)
    return wimd_df
