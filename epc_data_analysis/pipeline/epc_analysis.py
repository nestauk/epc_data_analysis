# File: getters/epc_analysis.py
"""Functions to help with EPC analysis.

Created May 2021
@author: Julia Suter
Last updated on 13/07/2021
"""

# ---------------------------------------------------------------------------------

# Imports

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR

# ---------------------------------------------------------------------------------

# Load config file
epc_data_config = get_yaml_config(
    Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml")
)
FIG_PATH = str(PROJECT_DIR) + epc_data_config["FIGURE_PATH"]


def get_emissions_info(df, feature_1, feature_2):
    """Get CO2 emissions data as absolute and relative numbers as well
    as per dwelling (mean).

    Parameters
    ----------

    df : pandas.DataFrame
        Dataframe from which to retrieve emission data.
        Needs to have columns named CO2_EMISSIONS_CURRENT
        and CO2_EMISS_CURR_PER_FLOOR_AREA.

    feature_1: str
        Emission feature, ideally "CO2_EMISSIONS_CURRENT"
        or "CO2_EMISS_CURR_PER_FLOOR_AREA" (y-axis).

    feature_2: str
        Feature by which to plot emissions (x-axis).

    Return
    ----------

    emissions_dict : dict
        Dictionary holding data on emissions (absolute, relative and mean)."""

    # Total emissions
    total_emissions = np.sum(df["CO2_EMISSIONS_CURRENT"].sum())
    total_emissions_by_area = np.sum(df["CO2_EMISS_CURR_PER_FLOOR_AREA"].sum())
    total = total_emissions = np.sum(df[feature_1].sum())

    # Get absolute, relative and mean emissions
    emissions_rel = df.groupby(feature_2)[feature_1].sum() / total * 100
    emissions_abs = df.groupby(feature_2)[feature_1].sum()
    emissions_mean = df.groupby(feature_2)[feature_1].mean()
    emissions_by_dwelling = emissions_abs / df[feature_2].value_counts()

    # Set up emissions dictionary
    emissions_dict = {
        "total emissions": total_emissions,
        "total emissions by area": total_emissions_by_area,
        "total": total,
        "relative emissions": emissions_rel,
        "absolute emissions": emissions_abs,
        "mean emissions": emissions_mean,
        "emisisons by dwelling": emissions_by_dwelling,
    }

    return emissions_dict
