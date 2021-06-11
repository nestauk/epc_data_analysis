# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     comment_magics: true
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: EPC_data_analysis
#     language: python
#     name: epc_data_analysis
# ---

# %% [markdown]
# # Analysis of Energy Efficiency using Kepler.gl
#
#
# We analyse energy efficiency in Wales and compare it to the Index of Multiple Deprivation (IMD). For visualisation, we use [kepler.gl](https://kepler.gl/).

# %% [markdown]
# ### Importing and Loading

# %%
import yaml
import pandas as pd
import numpy as np
from keplergl import KeplerGl

# %%
with open("Kepler/tenure_type_correct_colors_IMD_config.txt", "r") as infile:
    config = infile.read()
    config = yaml.load(config, Loader=yaml.FullLoader)


# %%
wales_epc = pd.read_csv(
    "../../../outputs/data/Pandas Dataframes/out.csv", low_memory=False
)
wimd_df = pd.read_csv(
    "../../../outputs/data/Pandas Dataframes/wimd.csv", low_memory=False
)

# %% [markdown]
# ### Only Load Necessary Data to Reduce Loading Time
#
# ... and keep Kepler from crashing

# %%
dataframe = wales_epc[
    [
        "TENURE",
        "longitude",
        "latitude",
        "CURRENT_ENERGY_RATING",
        "CURR_ENERGY_RATING_IN_NUMBER",
    ]
]

# %%
EPC_map = {
    "A": "A-C",
    "B": "A-C",
    "C": "A-C",
    "D": "D-G",
    "E": "D-G",
    "F": "D-G",
    "G": "D-G",
}


def get_EPC_cat(EPC_list):
    return [EPC_map[EPC] for EPC in EPC_list]


dataframe = dataframe.drop(
    dataframe[dataframe.CURRENT_ENERGY_RATING == "INVALID!"].index
)

dataframe["EPC CATEGORY"] = get_EPC_cat(dataframe["CURRENT_ENERGY_RATING"])

# %%

dataframe.head()

# %% [markdown]
# ### Load Data in Kepler Visualisation

# %%
tenure_type_map = KeplerGl(height=500, config=config)

tenure_type_map.add_data(
    data=dataframe.loc[dataframe["TENURE"] == "rental (social)"], name="social"
)
tenure_type_map.add_data(
    data=dataframe.loc[dataframe["TENURE"] == "rental (private)"], name="private"
)
tenure_type_map.add_data(
    data=dataframe.loc[dataframe["TENURE"] == "owner-occupied"], name="owner-occupied"
)
tenure_type_map.add_data(data=wimd_df, name="WIMD")

tenure_type_map

# %% [markdown]
# ### Save Map and Config File

# %%
tenure_type_map.save_to_html(
    file_name="../../../outputs/data/Wales HTML/Wales_EPC_IMD.html"
)
with open("Kepler/tenure_type_correct_colors_IMD_config.txt", "w") as outfile:
    outfile.write(str(tenure_type_map.config))

# %%
