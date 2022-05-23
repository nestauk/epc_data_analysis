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
# # Energy Efficiency and Heat Pumps Across the UK

# %% [markdown]
# ### Imports

# %%
# %load_ext autoreload
# %autoreload 2

import yaml
import pandas as pd
import numpy as np
from keplergl import KeplerGl
import h3

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR
from epc_data_analysis.config.kepler import kepler_config
from epc_data_analysis.config.kepler.kepler_config import (
    MAPS_CONFIG_PATH,
    MAPS_OUTPUT_PATH,
)
from epc_data_analysis.getters import epc_data, util_data
from epc_data_analysis.pipeline.preprocessing import feature_engineering, data_cleaning
from epc_data_analysis.pipeline import data_agglomeration
from epc_data_analysis.visualisation import my_widgets

# %% [markdown]
# ## Data Preparation
#
# ### Load EPC data
#
# Only load necessary features and subset to keep Kepler from crashing.

# %%
# Display dataset widgets
display(my_widgets.UK_part_widget)
display(my_widgets.duplicate_widget)
display(my_widgets.kepler_feat_widget)

# %%
# Get parameters from widgets
UK_part = my_widgets.UK_part_widget.value
dedupl = True if my_widgets.duplicate_widget.value == "Without Duplicates" else False
EPC_LOC_PATH = (
    kepler_config.EPC_DEDUPL_WITH_LOC if dedupl else kepler_config.EPC_WITH_LOC
)

features_of_interest = [
    "COUNTRY",
    "HP_INSTALLED",
    "ENTRY_YEAR_INT",
    "HP_TYPE",
    "CURRENT_ENERGY_RATING",
    "CO2_EMISSIONS_CURRENT",
    "LONGITUDE",
    "LATITUDE",
    "hex_id",
    "HEATING_COST_CURRENT",
    "LOCAL_AUTHORITY_LABEL",
    "TENURE",
    "BUILDING_ID",
    "LODGEMENT_DATE",
    "ENTRY_YEAR_INT",
    "DATE_INT",
]

load_location_data = True

if load_location_data:
    epc_df = pd.read_csv(EPC_LOC_PATH, usecols=features_of_interest)

else:

    epc_df = epc_data.load_preprocessed_epc_data(
        version=version, usecols=features_of_interest
    )

    if ("LONGITUDE" not in epc_df.columns) or ("LATITUDE" not in epc_df.columns):
        epc_df = feature_engineering.get_coordinates(epc_df)

    if "hex_id" not in epc_df.columns:
        epc_df = data_agglomeration.add_hex_id(epc_df, resolution=7.5)
        epc_df.to_csv(path, index=False)

epc_df.head()

# %% [markdown]
# ### Get Country and Sector Data

# %%
if UK_part != "GB":
    epc_df = epc_df.loc[epc_df["COUNTRY"] == UK_part]

sector_dict = {
    "rental private": epc_df.loc[epc_df["TENURE"] == "rental (private)"],
    "rental social": epc_df.loc[epc_df["TENURE"] == "rental (social)"],
    "owner-occupied": epc_df.loc[epc_df["TENURE"] == "owner-occupied"],
    "unknown": epc_df.loc[epc_df["TENURE"] == "unknown"],
}

# %% [markdown]
# ### Recompute Hex ID with another resolution

# %%
# epc_df = data_agglomeration.add_hex_id(epc_df, resolution=10)

# %% [markdown]
# ## Agglomerate Data by Region
#
# For example by Hex ID or Local Authority.
#
# #### Map Hex ID to other features, e.g. Local Authority

# %%
# Get HEX ID to Local Authority Mapping
hex_to_LA = data_agglomeration.map_hex_to_feature(epc_df, "LOCAL_AUTHORITY_LABEL")

# %% [markdown]
# #### Feature agglomerated by Hex ID

# %%
# Get agglomerated features by Hex ID
agglo_df = data_agglomeration.get_agglomerated_features(
    epc_df, feature=None, agglo_feature="hex_id", year_stamp=None
)

# Add Local Authority Label to every Hex ID
agglo_df = pd.merge(agglo_df, hex_to_LA, on=["hex_id"])

agglo_df.head()

# %% [markdown]
# #### Feature agglomerated by Hex ID and split by sector

# %%
agglo_f_sector_dict = {}

for sector in sector_dict.keys():

    sector_df = sector_dict[sector]
    agglo_sector_df = data_agglomeration.get_agglomerated_features(
        sector_df, feature=None, agglo_feature="hex_id"
    )
    agglo_sector_df = pd.merge(agglo_sector_df, hex_to_LA, on=["hex_id"])

    agglo_f_sector_dict[sector] = agglo_sector_df

# %% [markdown]
# ## Create Interactive Maps
#
# ### Weighted EPC Ratings

# %%
version_tag = "weighted_EPC"

config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
config = kepler_config.get_config(config_file)

weighted_epc_map = KeplerGl(height=500, config=config)

weighted_epc_map.add_data(data=agglo_df[["EPC_CAT", "hex_id"]], name="Combo EPC")

weighted_epc_map

# %%
kepler_config.save_config(weighted_epc_map, config_file)

weighted_epc_map.save_to_html(
    file_name=MAPS_OUTPUT_PATH + "Weighted_EPC_{}.html".format(UK_part)
)

# %% [markdown]
# ### Heat Pump Uptake

# %%
version_tag = "heat_pump_percentage"

config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
config = kepler_config.get_config(config_file)

heat_pump_map = KeplerGl(height=500, config=config)

heat_pump_map.add_data(data=agglo_df[["HP_PERC", "hex_id"]], name="heat pump")

heat_pump_map.add_data(data=agglo_df[["density", "hex_id"]], name="density")

heat_pump_map

# %%
kepler_config.save_config(heat_pump_map, config_file)

heat_pump_map.save_to_html(
    file_name=MAPS_OUTPUT_PATH + "Heat_Pump_Percentage_{}.html".format(UK_part)
)

# %% [markdown]
# ### Weighted EPC Ratings by Sectors

# %%
version_tag = "EPC_sector_comparison"

config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
config = kepler_config.get_config(config_file)

epc_tenure_type_map = KeplerGl(height=500, config=config)

epc_tenure_type_map.add_data(data=agglo_df[["EPC_CAT", "hex_id"]], name="Combo EPC")

epc_tenure_type_map.add_data(
    data=agglo_f_sector_dict["rental social"][["EPC_CAT", "hex_id"]], name="social"
)
epc_tenure_type_map.add_data(
    data=agglo_f_sector_dict["rental private"][["EPC_CAT", "hex_id"]], name="private"
)
epc_tenure_type_map.add_data(
    data=agglo_f_sector_dict["owner-occupied"][["EPC_CAT", "hex_id"]],
    name="owner-occupied",
)


epc_tenure_type_map.add_data(data=agglo_f_sector_dict["unknown"], name="unknown")

epc_tenure_type_map


# %%
kepler_config.save_config(epc_tenure_type_map, config_file)

epc_tenure_type_map.save_to_html(
    file_name=MAPS_OUTPUT_PATH
    + "Sector_Comparison_Weighted_EPC_{}.html".format(UK_part)
)

# %% [markdown]
# ### Heat Pump Uptake by Sectors

# %%
version_tag = "HP_sector_dens_comparison"

config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
config = kepler_config.get_config(config_file)

hp_tenure_type_map = KeplerGl(height=500, config=config)

hp_tenure_type_map.add_data(
    data=agglo_f_sector_dict["rental social"][["HP_PERC", "hex_id"]], name="Social: HP"
)

hp_tenure_type_map.add_data(
    data=agglo_f_sector_dict["rental private"][["HP_PERC", "hex_id"]],
    name="Private: HP",
)

hp_tenure_type_map.add_data(
    data=agglo_f_sector_dict["owner-occupied"][["HP_PERC", "hex_id"]], name="Owner: HP"
)

hp_tenure_type_map.add_data(
    data=agglo_f_sector_dict["unknown"][["HP_PERC", "hex_id"]], name="Unknown: HP"
)

hp_tenure_type_map.add_data(
    data=agglo_f_sector_dict["rental social"][["density", "hex_id"]],
    name="Social: Density",
)

hp_tenure_type_map.add_data(
    data=agglo_f_sector_dict["rental private"][["density", "hex_id"]],
    name="Private: Density",
)

hp_tenure_type_map.add_data(
    data=agglo_f_sector_dict["owner-occupied"][["density", "hex_id"]],
    name="Owner: Density",
)

hp_tenure_type_map.add_data(
    data=agglo_f_sector_dict["unknown"][["density", "hex_id"]], name="Unknown: Density"
)

hp_tenure_type_map

# %%
kepler_config.save_config(hp_tenure_type_map, config_file)

hp_tenure_type_map.save_to_html(
    file_name=MAPS_OUTPUT_PATH
    + "Sector_Comparison_Heat_Pump_Percentage_{}.html".format(UK_part)
)

# %% [markdown]
# ### Time Course

# %%
epc_df = pd.read_csv(str(PROJECT_DIR) + "/inputs/epc_df_complete_preprocessed.csv")

# %%
epc_df = feature_engineering.get_coordinates(epc_df)
epc_df = data_agglomeration.add_hex_id(epc_df, resolution=7.5)

# %%
epc_df["DATE_INT"] = (
    epc_df["INSPECTION_DATE"]
    .str.replace("/", "")
    .apply(feature_engineering.get_date_as_int)
)
# epc_df = feature_engineering.filter_by_year(epc_df, "BUILDING_ID", year=2021, up_to=True, selection="latest entry")


# %%
hex_df = pd.DataFrame(epc_df.hex_id.unique())
hex_df.columns = ["hex_id"]

# %%
la_df = pd.DataFrame(epc_df.LOCAL_AUTHORITY_LABEL.unique())
la_df.columns = ["LOCAL_AUTHORITY_LABEL"]

# %%
# dedupl_epc_df = feature_engineering.filter_by_year(epc_df, "BUILDING_ID", year=2021, up_to=True, selection="latest entry")
# dedupl_epc_df.shape

# %%
# dedupl_epc_df['HP_INSTALL_YEAR'].head()

# = 2016
# dedupl_epc_df['HP_INSTALLED']['HP_INSTALLED'] = (dedupl_epc_df['HP_INSTALL_YEAR'] <= year)
# dedupl_epc_df['HP_INSTALL_YEAR'].value_counts(dropna=False)

# %%
# Get HEX ID to Local Authority Mapping
hex_to_LA = data_agglomeration.map_hex_to_feature(epc_df, "LOCAL_AUTHORITY_LABEL")

# %%
data_by_year = []

# epc_df = feature_engineering.filter_by_year(epc_df, "BUILDING_ID", year=2021, up_to=True, selection="latest entry")

for year in [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]:

    year_df = feature_engineering.filter_by_year(
        epc_df, "BUILDING_ID", year, up_to=True
    ).copy()
    print(year_df.shape)
    year_df["HP_INSTALLED"] = year_df["HP_INSTALL_YEAR"] <= year

    year_stamp = str(year) + "/01/01 00:00"
    year_agglo_df = data_agglomeration.get_agglomerated_features(
        year_df,
        feature=None,
        agglo_feature="LOCAL_AUTHORITY_LABEL",
        year_stamp=year_stamp,
    )
    # year_agglo_df = pd.merge(year_agglo_df,hex_df, on='hex_id', how='right')
    year_agglo_df = pd.merge(
        year_agglo_df, la_df, on="LOCAL_AUTHORITY_LABEL", how="right"
    )
    year_agglo_df["YEAR_STAMP"] = str(year) + "/01/01 00:00"

    year_agglo_df = pd.merge(hex_to_LA, year_agglo_df, on=["LOCAL_AUTHORITY_LABEL"])
    data_by_year.append(year_agglo_df)

time_data = pd.concat(data_by_year)

# %%
time_data["HP_PERC"] = time_data["HP_PERC"].fillna(0.0)
time_data["HP_CAT"] = time_data["HP_CAT"].fillna("0.0 %")

# %%
version_tag = "HP_time_course"

config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
config = kepler_config.get_config(config_file)

time_map = KeplerGl(height=500, config=config)

time_map.add_data(
    data=time_data[
        [
            "HP_PERC",
            "HP_CAT",
            "EPC_CAT",
            "hex_id",
            "LOCAL_AUTHORITY_LABEL",  # "CO2_EMISSIONS_CURRENT",
            "YEAR_STAMP",
        ]
    ],
    name="Year Data",
)

time_map

# %%
kepler_config.save_config(time_map, config_file)

time_map.save_to_html(file_name=MAPS_OUTPUT_PATH + "Time_Course_Heat_Pumps.html")

# %%
version_tag = "HP_time_course"

config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
config = kepler_config.get_config(config_file)

time_map = KeplerGl(height=500, config=config)

time_map.add_data(
    data=time_data[
        [
            "HP_PERC",
            "HP_CAT",
            "EPC_CAT",
            "hex_id",
            "LOCAL_AUTHORITY_LABEL",  # "CO2_EMISSIONS_CURRENT",
            "YEAR_STAMP",
        ]
    ],
    name="Year Data",
)

time_map

# %%
version_tag = "HP_time_course_2"
config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
kepler_config.save_config(time_map, config_file)

time_map.save_to_html(file_name=MAPS_OUTPUT_PATH + "Time_Course_Heat_Pumps_2.html")

# %% [markdown]
# ### Local Authority

# %%
# Get agglomerated features by Hex ID
agglo_df = data_agglomeration.get_agglomerated_features(
    epc_df, feature=None, agglo_feature="LOCAL_AUTHORITY_LABEL", year=None
)

print(agglo_df.shape)
# Add Local Authority Label to every Hex ID
agglo_df = pd.merge(hex_to_LA, agglo_df, on=["LOCAL_AUTHORITY_LABEL"])

print(agglo_df.shape)

agglo_df.head()

# %%
version_tag = "local_authority"

config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
config = kepler_config.get_config(config_file)

LA_map = KeplerGl(height=500, config=config)

LA_map.add_data(
    data=agglo_df[
        [
            "HP_PERC",
            "HP_CAT",
            "EPC_CAT",
            "hex_id",
            "LOCAL_AUTHORITY_LABEL",
            "CO2_EMISSIONS_CURRENT",
        ]
    ],
    name="LA",
)

LA_map

# %%
kepler_config.save_config(LA_map, config_file)

LA_map.save_to_html(file_name=MAPS_OUTPUT_PATH + "Local_Authority.html")

# %%

# %%

# %%

# %%
