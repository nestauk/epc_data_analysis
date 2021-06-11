import pandas as pd
import os
from dask import delayed
import dask.dataframe as dd


from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR


# Load config file
epc_data_config = get_yaml_config(
    Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml")
)

# Get paths
epc_data_path = str(PROJECT_DIR) + epc_data_config["EPC_DATASET_PATH"]


def load_EPC_data(cert_subset="all", usecols=None):
    """Load and return EPC dataset, or specific subset, as pandas dataframe.

    Return:
        EPC_certs (pandas dataframe): EPC certificate data.
    """

    sample_file_path = epc_data_path + "/domestic-W06000015-Cardiff/certificates.csv"
    sample_df = pd.read_csv(sample_file_path)

    if usecols == None:
        usecols = sample_df.columns

    if cert_subset == "Wales":

        EPC_certs = [
            pd.read_csv(
                epc_data_path + directory + "/certificates.csv",
                low_memory=False,
                usecols=usecols,
            )
            for directory in os.listdir(epc_data_path)
            if directory.startswith("domestic-W")  # only Wales data
        ]

    elif cert_subset == "England":

        EPC_certs = [
            pd.read_csv(
                epc_data_path + directory + "/certificates.csv",
                low_memory=False,
                usecols=usecols,
            )
            for directory in os.listdir(epc_data_path)
            if directory.startswith("domestic-E")  # only England data
        ]

    elif cert_subset == "all":

        epc_files = [file for file in os.listdir(epc_data_path)]
        epc_files = [
            file
            for file in epc_files
            if not file.startswith(".") and file != "LICENCE.txt"
        ]

        EPC_certs = [
            pd.read_csv(
                epc_data_path + directory + "/certificates.csv",
                low_memory=False,
                usecols=usecols,
            )
            for directory in epc_files  # all data (except hidden folders)
        ]

    else:
        raise IOError(
            "'{}' is not a valid subset of the EPC dataset.".format(cert_subset)
        )

    # Concatenate single dataframes into dataframe
    EPC_certs = pd.concat(EPC_certs, axis=0)

    return EPC_certs


def main():
    """Main function for testing."""

    epc_df = load_EPC_data(cert_subset="Wales")
    print(epc_df.head())


if __name__ == "__main__":
    # execute only if run as a script
    main()
