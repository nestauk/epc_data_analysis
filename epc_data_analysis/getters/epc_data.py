# File: getters/epc_data.py
""""
Created May 2021
@author: Julia Suter
Last updated on 23/07/2021
"""

# ---------------------------------------------------------------------------------

import pandas as pd
import os

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR

# ---------------------------------------------------------------------------------

# Load config file
epc_data_config = get_yaml_config(
    Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml")
)

# Get path
epc_data_path = str(PROJECT_DIR) + epc_data_config["EPC_DATASET_PATH"]


def load_EPC_data(subset="all", usecols=None, low_memory=False):
    """Load and return EPC dataset, or specific subset, as pandas dataframe.

    Parameters
    ----------
    subset : {'all', 'Wales', 'England'}, default='all'
        EPC certificate area subset.

    usecols : list, default=None
        List of features/columns to load from EPC dataset.

    low_memory : bool, default=False
        Internally process the file in chunks, resulting in lower memory use while parsing,
        but possibly mixed type inference.
        To ensure no mixed types either set False, or specify the type with the dtype parameter.

    Return
    ---------
    EPC_certs : pandas.DateFrame
        EPC certificate data for given area and features."""

    # Load data
    sample_file_path = epc_data_path + "/domestic-W06000015-Cardiff/certificates.csv"
    sample_df = pd.read_csv(sample_file_path)

    # Get all columns if not other specified
    if usecols == None:
        usecols = sample_df.columns

    # Get Wales data
    if subset == "Wales":

        # Load specific location certificates and features
        EPC_certs = [
            pd.read_csv(
                epc_data_path + directory + "/certificates.csv",
                low_memory=low_memory,
                usecols=usecols,
            )
            for directory in os.listdir(epc_data_path)
            if directory.startswith("domestic-W")  # only Wales data
        ]

    # Get England data
    elif subset == "England":

        # Load specific location certificates and features
        EPC_certs = [
            pd.read_csv(
                epc_data_path + directory + "/certificates.csv",
                low_memory=low_memory,
                usecols=usecols,
            )
            for directory in os.listdir(epc_data_path)
            if directory.startswith("domestic-E")  # only England data
        ]

    # Get all data
    elif subset == "all":

        # Load
        epc_files = [
            file
            for file in os.listdir(epc_data_path)[:500]
            if not file.startswith(".") and file != "LICENCE.txt"
        ]

        # Load specific location certificates and features
        EPC_certs = [
            pd.read_csv(
                epc_data_path + directory + "/certificates.csv",
                low_memory=low_memory,
                usecols=usecols,
            )
            for directory in epc_files  # all data (except hidden folders)
        ]

    else:
        raise IOError("'{}' is not a valid subset of the EPC dataset.".format(subset))

    # Concatenate single dataframes into dataframe
    EPC_certs = pd.concat(EPC_certs, axis=0)

    return EPC_certs


# ---------------------------------------------------------------------------------


def main():
    """Main function for testing."""

    epc_df = load_EPC_data(subset="Wales")
    print(epc_df.head())


if __name__ == "__main__":
    # Execute only if run as a script
    main()
