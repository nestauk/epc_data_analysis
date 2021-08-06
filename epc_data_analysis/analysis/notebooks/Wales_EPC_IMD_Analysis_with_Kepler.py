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
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: epc_data_analysis
#     language: python
#     name: epc_data_analysis
# ---

# %% [markdown]
# # Analysis of Energy Efficiency using Kepler.gl
#
#
# We analyse energy efficiency in Wales and compare it to the Index of Multiple Deprivation (IMD). For visualisation, we use [kepler.gl](https://kepler.gl/).

# %% [markdown]
# ### Imports

# %%
import yaml
import pandas as pd
import numpy as np
from keplergl import KeplerGl

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR
from epc_data_analysis.getters import epc_data, util_data
from epc_data_analysis.pipeline import feature_engineering, data_cleaning
from epc_data_analysis.analysis.notebooks.notebook_utils import Kepler_configs

# %% [markdown]
# ### Load Config File

# %%
# Load config file
config = Kepler_configs.get_Kepler_config()

# %% [markdown]
# ### Load EPC data
#
# Only load necessary features and subset to keep Kepler from crashing.

# %%
# Set features of interest
features_of_interest = [
    "TENURE",
    "CURRENT_ENERGY_RATING",
    "POSTCODE",
    "POTENTIAL_ENERGY_RATING",
]

# Load Wales EPC data
epc_df = epc_data.load_epc_data(
    subset="Wales", usecols=features_of_interest, low_memory=False
)
location_df = util_data.get_location_data()

# %% [markdown]
# ### Load Location Data and additional EPC features
#
# And remove uncessary features afterwards (POSTCODE, POTENTIAL_ENERGY_RATING).
#
# Remove samples with invalid CURRENT_ENERGY_RATING.

# %%
# Reformat POSTCODE
epc_df = data_cleaning.reformat_postcode(epc_df)
wimd_df = data_cleaning.reformat_postcode(location_df)

# Merge with location data
epc_df = pd.merge(epc_df, location_df, on=["POSTCODE"])

# Get additional features
epc_df = feature_engineering.get_new_EPC_rating_features(epc_df)

# Remove unnecessary features
epc_df = epc_df[
    ["TENURE", "CURRENT_ENERGY_RATING", "LATITUDE", "LONGITUDE", "ENERGY_RATING_CAT"]
]

epc_df = epc_df.drop(epc_df[epc_df.CURRENT_ENERGY_RATING == "INVALID!"].index)
epc_df.head()

# %% [markdown]
# ### Load Wales IMD data

# %%
# Load Wales IMD data
wimd_df = util_data.get_WIMD_data()
wimd_df = wimd_df[["WIMD Decile", "LATITUDE", "LONGITUDE", "WIMD Score"]]
wimd_df.head()

# %% [markdown]
# ### Load Data in Kepler Visualisation
#
# Load 4 different layers:
#
#     - rental (social)
#     - rental (private)
#     - owner-occupied
#     - IMD

# %%
tenure_type_map = KeplerGl(height=500, config=config)

tenure_type_map.add_data(
    data=epc_df.loc[epc_df["TENURE"] == "rental (social)"], name="social"
)
tenure_type_map.add_data(
    data=epc_df.loc[epc_df["TENURE"] == "rental (private)"], name="private"
)
tenure_type_map.add_data(
    data=epc_df.loc[epc_df["TENURE"] == "owner-occupied"], name="owner-occupied"
)
tenure_type_map.add_data(data=wimd_df, name="WIMD")

tenure_type_map

# %% [markdown]
# ### Save Map and Config File

# %%
tag = "_new"

tenure_type_map.save_to_html(
    file_name=Kepler_configs.KEPLER_OUTPUT_PATH + "Wales_EPC_IMD.html"
)

new_config_file = (
    Kepler_configs.KEPLER_CONFIG_FILE_PATH
    + "/tenure_type_correct_colors_IMD_config{}.txt".format(tag)
)
with open(new_config_file, "w") as outfile:
    outfile.write(str(tenure_type_map.config))
