# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     comment_magics: true
#     formats: ipynb,md,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: 'Python 3.8.8 64-bit (''EPC_data_analysis'': conda)'
#     language: python
#     name: python388jvsc74a57bd01a4c7ba010db823d16e88c91be90e4c3d0f1a2001e059c3c5486bc88e685f2ad
# ---

# %%
import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact

from epc_data_analysis.getters import epc_data, util_data
from epc_data_analysis.pipeline.data_augmentation import feature_engineering
from epc_data_analysis.pipeline.plotting import easy_plotting
from epc_data_analysis.pipeline.analysis import wales_analysis

from epc_data_analysis.analysis.notebooks.notebook_utils import my_widgets

# %%
features_of_interest = [
    "CURRENT_ENERGY_RATING",
    "POTENTIAL_ENERGY_RATING",
    "TENURE",
    "MAINHEAT_ENERGY_EFF",
    "MAINHEAT_ENV_EFF",
    "HOT_WATER_ENERGY_EFF",
    "HOT_WATER_ENV_EFF",
    "FLOOR_ENERGY_EFF",
    "FLOOR_ENV_EFF",
    "WINDOWS_ENERGY_EFF",
    "WINDOWS_ENV_EFF",
    "WALLS_ENERGY_EFF",
    "WALLS_ENV_EFF",
    "ROOF_ENERGY_EFF",
    "ROOF_ENV_EFF",
    "MAINHEATC_ENERGY_EFF",
    "MAINHEATC_ENV_EFF",
    "LIGHTING_ENERGY_EFF",
    "LIGHTING_ENV_EFF",
    "POSTCODE",
    "MAINHEAT_DESCRIPTION",
    "CO2_EMISSIONS_CURRENT",
    "CO2_EMISS_CURR_PER_FLOOR_AREA",
]

# Load Wales EPC data
epc_df = epc_data.load_EPC_data(cert_subset="Wales", usecols=features_of_interest)

# %%
# Remove NO DATA tenure types
# epc_df = epc_df.drop(epc_df[epc_df.TENURE == "NO DATA!"].index)

# Add new features
epc_df = feature_engineering.get_new_EPC_rating_features(epc_df)

post_df = util_data.get_postcode_loc_df()
epc_df = pd.merge(epc_df, post_df, on=["POSTCODE"])
epc_df["POSTCODE"] = epc_df["POSTCODE"].str.replace(r" ", "")

wimd_df = pd.read_csv(
    "../../../outputs/data/Pandas Dataframes/wimd_df.csv", low_memory=True
)

epc_df = pd.merge(epc_df, wimd_df, on=["POSTCODE"])
epc_df.head()


# %%
@interact(tenure_type=my_widgets.tenure_type_midi)
def plot_EPC_by_tenure_type(tenure_type):

    easy_plotting.plot_feature_by_subcategories(
        epc_df,
        "CURRENT_ENERGY_RATING",
        "TENURE",
        tenure_type,
        plot_kind="bar",
    )


# %%
@interact(tenure_type=[1, 2, 3, 4, 5])
def plot_EPC_by_tenure_type(tenure_type):

    easy_plotting.plot_feature_by_subcategories(
        epc_df,
        "CURRENT_ENERGY_RATING",
        "WIMD Quartile",
        tenure_type,
        plot_kind="bar",
    )


# %%
# cost_midi = my_widgets.get_custom_dropdown_midi(
# ['LIGHTING_COST_CURRENT',
#  'LIGHTING_COST_POTENTIAL',
#  'HEATING_COST_CURRENT',
#  'HEATING_COST_POTENTIAL',
#  'HOT_WATER_COST_CURRENT',
#  'HOT_WATER_COST_POTENTIAL',
#  'WIMD score', 'WIMD Rank'
# ]
# )

# @interact(tenure_type=my_widgets.tenure_type_midi, cost_type=cost_midi)
# def plot_EPC_by_tenure_type(tenure_type, cost_type):

# easy_plotting.plot_feature_by_subcategories(
#     epc_df,
#     cost_type,
#     "TENURE",
#     tenure_type,
#     plot_kind="hist",
# )

# %%
column_midi = my_widgets.get_dropdown_midi(epc_df)


@interact(category=column_midi)
def plot_distribution(category):
    easy_plotting.plot_distribution_by_category(
        epc_df, category, normalize=True, y_label="# dwellings"
    )


# %%
efficiency_order = ["Very Good", "Good", "Average", "Poor", "Very Poor"]
cat_order = ["A", "B", "C", "D", "E", "F", "G"]
tenure_type_order = ["rental (social)", "rental (private)", "owner-occupied", "unknown"]
color_list = ["darkgreen", "green", "greenyellow", "yellow", "orange", "red", "darkred"]


@interact(
    feature=["WIMD Decile", "WIMD Quartile", "WIMD Quintile", "WIMD score", "WIMD Rank"]
)
def plotting(feature):
    easy_plotting.plot_groups_by_other_groups(
        epc_df,
        "TENURE",
        feature,
        feature_1_order=tenure_type_order,
        y_ticklabel_type="",
        y_label="# dwellings",
        plot_title="IMD decile by tenure type",
        normalize=False,
    )


# %%
efficiency_midi = my_widgets.get_custom_dropdown_midi(
    [
        "MAINHEAT_ENERGY_EFF",
        "MAINHEAT_ENV_EFF",
        "HOT_WATER_ENERGY_EFF",
        "HOT_WATER_ENV_EFF",
        "FLOOR_ENERGY_EFF",
        "FLOOR_ENV_EFF",
        "WINDOWS_ENERGY_EFF",
        "WINDOWS_ENV_EFF",
        "WALLS_ENERGY_EFF",
        "WALLS_ENV_EFF",
        "ROOF_ENERGY_EFF",
        "ROOF_ENV_EFF",
        "MAINHEATC_ENERGY_EFF",
        "MAINHEATC_ENV_EFF",
        "LIGHTING_ENERGY_EFF",
        "LIGHTING_ENV_EFF",
    ]
)


@interact(feature_2=efficiency_midi)
def plot_group_by_subgroup(feature_2):
    easy_plotting.plot_groups_by_other_groups(
        epc_df,
        "TENURE",
        feature_2,
        feature_1_order=tenure_type_order,
        feature_2_order=efficiency_order,
        y_ticklabel_type="k",
        use_color_list=True,
        y_label="# dwellings",
        normalize=False,
    )


# %%
feature_1 = ["WIMD Decile", "WIMD Quartile", "WIMD Quintile", "WIMD score", "WIMD Rank"]

social_epc = epc_df.loc[epc_df["TENURE"] == "rental (social)"]


@interact(feature_1=feature_1, feature_2=efficiency_midi)
def plot_group_by_subgroup(feature_1, feature_2):
    easy_plotting.plot_groups_by_other_groups(
        epc_df,
        feature_1,
        feature_2,
        # feature_1_order=tenure_type_order,
        feature_2_order=efficiency_order,
        y_ticklabel_type="k",
        use_color_list=True,
        y_label="# dwellings",
        normalize=False,
    )


# %%

(
    epc_df["HEATING_TYPE"],
    epc_df["HEATING_GENERAL_TYPE"],
) = feature_engineering.get_heating_type(epc_df["MAINHEAT_DESCRIPTION"])

epc_social_df = epc_df.loc[epc_df["TENURE"] == "rental (social)"]


@interact(feature_2=["HEATING_TYPE", "HEATING_GENERAL_TYPE"])
def plot_group_by_subgroup(feature_2):
    easy_plotting.plot_groups_by_other_groups(
        # epc_social_df,
        epc_df,
        "TENURE",
        feature_2,
        feature_1_order=tenure_type_order,
        # feature_2_order=['oil','electric','LPG','gas','unknown'],
        y_ticklabel_type="k",
        y_label="# dwellings",
        color_list=[
            "teal",
            "green",
            "greenyellow",
            "yellow",
            "orange",
            "red",
            "darkred",
            "blue",
            "darkblue",
            "purple",
            "violet",
        ],
        normalize=False,
    )


# %%
@interact(feature=["CO2_EMISSIONS_CURRENT", "CO2_EMISS_CURR_PER_FLOOR_AREA"])
def emissions_by_tenure_type(feature):
    wales_analysis.emissions_by_tenure_type(epc_df, feature)


# %%
social_epc = epc_df.loc[epc_df["TENURE"] == "rental (social)"]


@interact(
    feature_1=["CO2_EMISSIONS_CURRENT", "CO2_EMISS_CURR_PER_FLOOR_AREA"],
    feature_2=[
        "WIMD Decile",
        "WIMD Quartile",
        "WIMD Quintile",
        "WIMD score",
        "WIMD Rank",
    ],
)
def emissions_by_wimd_type(feature_1, feature_2):
    wales_analysis.emissions_by_wimd_type(social_epc, feature_1, feature_2)


# %%
