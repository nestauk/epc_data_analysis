import pandas as pd
import os

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR

# Load config file
epc_data_config = get_yaml_config(
    Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml")
)

# Get paths
postcode_path = str(PROJECT_DIR) + epc_data_config["POSTCODE_PATH"]


def get_postcode_loc_df() -> pd.DataFrame:
    """Load and return EPC dataset, or specific subset, as pandas dataframe.

    Return:
        EPC_certs (pandas dataframe): EPC certificate data.
    """

    postcode_loc_df = pd.read_csv(postcode_path)

    del postcode_loc_df["id"]

    # Rename column with postcodes
    postcode_loc_df = postcode_loc_df.rename(
        columns={
            "postcode": "POSTCODE",
            "latitude": "LATITUDE",
            "longitude": "LONGITUDE",
        }
    )
    return postcode_loc_df
