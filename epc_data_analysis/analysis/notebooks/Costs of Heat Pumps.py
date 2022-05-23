# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     comment_magics: true
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

# %%
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

from epc_data_analysis.pipeline import data_agglomeration
from epc_data_analysis.pipeline.preprocessing import feature_engineering
from epc_data_analysis.visualisation import my_widgets

# %%
mcs_df = pd.read_csv(str(PROJECT_DIR) + "/inputs/mcs_epc.csv")
mcs_df = mcs_df.rename(columns={"postcode": "POSTCODE"})

# %%
mcs_df = feature_engineering.get_coordinates(mcs_df)
print(mcs_df.columns)

# %%
mcs_df = data_agglomeration.add_hex_id(mcs_df, resolution=7.5)

# %%
mcs_df.columns

# %%
mcs_df["PROPERTY_TYPE"].unique()


# %%

# %%
def get_cost_cat(cost):

    if cost < 5000:
        return "<5k"
    elif cost >= 5000 and cost < 10000:
        return "5k - 10k"
    elif cost >= 10000 and cost < 15000:
        return "10k - 15k"
    elif cost >= 15000 and cost < 20000:
        return "15k - 20k"
    elif cost >= 20000 and cost < 30000:
        return "20k - 30k"
    elif cost >= 30000 and cost < 50000:
        return "30k - 50k"
    elif cost >= 50000:
        return ">50k"


mcs_df["COST_CAT"] = mcs_df["cost"].apply(get_cost_cat)

# %%
# hex_to_LA = data_agglomeration.map_hex_to_feature(mcs_df, "LOCAL_AUTHORITY_LABEL")

# %%
sector_dict = {
    "owner-occupied": mcs_df.loc[mcs_df["TENURE"] == "owner-occupied"],
    "social rental": mcs_df.loc[mcs_df["TENURE"] == "rental (social)"],
    "private rental": mcs_df.loc[mcs_df["TENURE"] == "rental (private)"],
    "unknown": mcs_df.loc[mcs_df["TENURE"] == "unknown"],
}


full_agglo_dict = mcs_df[["cost", "hex_id"]].groupby("hex_id").median().reset_index()
full_agglo_dict["COST_CAT"] = full_agglo_dict["cost"].apply(get_cost_cat)

agglo_dict = {}
# Get agglomerated features by Hex ID
# agglo_df = data_agglomeration.get_agglomerated_features(mcs_df, feature=None, agglo_feature="hex_id", year=None)
for part in sector_dict.keys():
    df = sector_dict[part]
    agglo_df = df[["cost", "hex_id"]].groupby("hex_id").median().reset_index()
    agglo_df["COST_CAT"] = agglo_df["cost"].apply(get_cost_cat)
    agglo_dict[part] = agglo_df

# %%
agglo_df.head()

# %%
mcs_df["date"] = mcs_df["date"].str.replace(r"-", "/", regex=True)
mcs_df["date"] = mcs_df["date"] + " 00:00"
mcs_df.head()

# %%
agglo_df["COST_CAT"] = agglo_df["cost"].apply(get_cost_cat)

# %%
mcs_df["TENURE"].unique()

# %%

version_tag = "hp_costs"

# config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
config = kepler_config.get_config("test")

weighted_epc_map = KeplerGl(height=500, config=config)

weighted_epc_map.add_data(
    data=sector_dict["owner-occupied"][["COST_CAT", "cost", "hex_id", "date"]],
    name="owner-occupied",
)
weighted_epc_map.add_data(
    data=sector_dict["private rental"][["COST_CAT", "cost", "hex_id", "date"]],
    name="private rental",
)
weighted_epc_map.add_data(
    data=sector_dict["social rental"][["COST_CAT", "cost", "hex_id", "date"]],
    name="social rental",
)
weighted_epc_map.add_data(
    data=sector_dict["unknown"][["COST_CAT", "cost", "hex_id", "date"]], name="unknown"
)


weighted_epc_map

# %%

version_tag = "hp_costs"

# config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
config = kepler_config.get_config("test")

weighted_epc_map = KeplerGl(height=500, config=config)
weighted_epc_map.add_data(data=full_agglo_dict, name="all sectors")

weighted_epc_map.add_data(
    data=agglo_dict["owner-occupied"][["COST_CAT", "cost", "hex_id"]],
    name="owner-occupied",
)
weighted_epc_map.add_data(
    data=agglo_dict["private rental"][["COST_CAT", "cost", "hex_id"]],
    name="private rental",
)
weighted_epc_map.add_data(
    data=agglo_dict["social rental"][["COST_CAT", "cost", "hex_id"]],
    name="social rental",
)
weighted_epc_map.add_data(
    data=agglo_dict["unknown"][["COST_CAT", "cost", "hex_id"]], name="unknown"
)


weighted_epc_map

# %%
kepler_config.save_config(weighted_epc_map, "test")

weighted_epc_map.save_to_html(file_name=MAPS_OUTPUT_PATH + "Costs.html")

# %%
version_tag = "hp_costs"

# config_file = MAPS_CONFIG_PATH + "{}_config.txt".format(version_tag)
config = kepler_config.get_config("test")

weighted_epc_map = KeplerGl(height=500, config=config)

weighted_epc_map.add_data(
    data=mcs_df[["cost", "hex_id", "COST_CAT", "PROPERTY_TYPE", "date"]],
    name="Combo EPC",
)

weighted_epc_map

# %%
