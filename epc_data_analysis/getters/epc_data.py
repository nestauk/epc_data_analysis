# File: getters/epc_data.py
""""
Created May 2021
@author: Julia Suter
Last updated on 26/07/2021
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


def load_epc_data(subset="all", usecols=None, low_memory=False):
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
    epc_certs : pandas.DateFrame
        EPC certificate data for given area and features."""

    # Load sample data
    sample_file_path = epc_data_path + "/domestic-W06000015-Cardiff/certificates.csv"
    sample_df = pd.read_csv(sample_file_path)

    # Get all directories
    all_directories = os.listdir(epc_data_path)

    # Set subset dict to select respective subset directories
    start_with_dict = {"Wales": "domestic-W", "England": "domestic-E"}

    # Get directories for given subset
    if subset in start_with_dict:
        directories = [
            dir for dir in all_directories if dir.startswith(start_with_dict[subset])
        ]
    else:
        if subset == "all":
            directories = [
                file
                for file in all_directories
                if not file.startswith(".") and file != "LICENCE.txt"
            ]
        else:
            raise IOError(
                "'{}' is not a valid subset of the EPC dataset.".format(subset)
            )

    # Load EPC certificates for given subset
    # Only load columns of interest (if given)
    epc_certs = [
        pd.read_csv(
            epc_data_path + directory + "/certificates.csv",
            low_memory=low_memory,
            usecols=usecols,
        )
        for directory in directories
    ]

    # Concatenate single dataframes into dataframe
    epc_certs = pd.concat(epc_certs, axis=0)

    return epc_certs


# ---------------------------------------------------------------------------------


def main():
    """Main function for testing."""

    epc_df = load_epc_data(subset="Wales")
    print(epc_df.head())


if __name__ == "__main__":
    # Execute only if run as a script
    main()
