# File: getters/epc_data.py
""""
Created May 2021
@author: Julia Suter
Last updated on 26/07/2021
"""

# ---------------------------------------------------------------------------------

import pandas as pd
import os
import re

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR

# ---------------------------------------------------------------------------------

# Load config file
epc_data_config = get_yaml_config(
    Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml")
)

# Get path
EPC_DATA_PATH_ENG_WALES = str(PROJECT_DIR) + epc_data_config["EPC_DATASET_PATH"]
EPC_DATA_PATH_SCOTLAND = str(PROJECT_DIR) + epc_data_config["EPC_DATASET_SCOTLAND_PATH"]


def load_Scotland_data(usecols=None, low_memory=False):

    # Fix columns ("WALLS" features are labeled differently here)
    usecols = [re.sub("WALLS_", "WALL_", col) for col in usecols]

    # Get all directories
    all_directories = os.listdir(EPC_DATA_PATH_SCOTLAND)
    directories = [file for file in all_directories if file.endswith(".csv")]

    EPC_certs = [
        pd.read_csv(
            EPC_DATA_PATH_SCOTLAND + file,
            low_memory=low_memory,
            usecols=usecols,
            skiprows=1,  # don't load first row (more ellaborate feature names)
        )
        for file in directories
    ]

    # Concatenate single dataframes into dataframe
    EPC_certs = pd.concat(EPC_certs, axis=0)
    EPC_certs["COUNTRY"] = "Scotland"

    EPC_certs = EPC_certs.rename(
        columns={"WALL_ENV_EFF": "WALLS_ENV_EFF", "WALL_ENERGY_EFF": "WALLS_ENERGY_EFF"}
    )

    return EPC_certs


def load_Wales_England_data(subset, usecols, low_memory=False):

    # Get all directories
    all_directories = os.listdir(EPC_DATA_PATH_ENG_WALES)

    # Set subset dict to select respective subset directories
    start_with_dict = {"Wales": "domestic-W", "England": "domestic-E"}

    # Get directories for given subset
    if subset in start_with_dict:
        directories = [
            dir for dir in all_directories if dir.startswith(start_with_dict[subset])
        ]

    # Load EPC certificates for given subset
    # Only load columns of interest (if given)
    EPC_certs = [
        pd.read_csv(
            EPC_DATA_PATH_ENG_WALES + directory + "/certificates.csv",
            low_memory=low_memory,
            usecols=usecols,
        )
        for directory in directories
    ]

    # Concatenate single dataframes into dataframe
    EPC_certs = pd.concat(EPC_certs, axis=0)
    EPC_certs["COUNTRY"] = subset

    return EPC_certs


def load_epc_data(subset="all", usecols=None, low_memory=False):
    """Load and return EPC dataset, or specific subset, as pandas dataframe.

    Parameters
    ----------
    subset : {'all', 'Wales', 'England', 'Scotland'}, default='all'
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

    all_epc_df = []

    # Get Scotland data
    if subset in ["Scotland", "all"]:
        epc_Scotland_df = load_Scotland_data(usecols=usecols)
        all_epc_df.append(epc_Scotland_df)

        if subset == "Scotland":
            return epc_Scotland_df

    if subset in ["Wales", "England"]:
        epc_df = load_Wales_England_data(subset, usecols=usecols, low_memory=low_memory)
        return epc_df

    elif subset == "all":

        for country in ["Wales", "England"]:

            epc_df = load_Wales_England_data(
                country, usecols=usecols, low_memory=low_memory
            )
            all_epc_df.append(epc_df)

        epc_df = pd.concat(all_epc_df, axis=0)

        return epc_df

    else:
        raise IOError("'{}' is not a valid subset of the EPC dataset.".format(subset))


# ---------------------------------------------------------------------------------


def main():
    """Main function for testing."""

    epc_df = load_epc_data(subset="Wales")
    print(epc_df.head())


if __name__ == "__main__":
    # Execute only if run as a script
    main()
