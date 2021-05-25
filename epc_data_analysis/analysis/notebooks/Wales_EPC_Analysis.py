# ---
# jupyter:
#   jupytext:
#     formats: ipynb,md,py:percent
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

# %%
import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact

from epc_data_analysis.getters import epc_data, util_data
from epc_data_analysis.pipeline.data_augmentation import feature_engineering
from epc_data_analysis.pipeline.plotting import easy_plotting
from epc_data_analysis.pipeline.analysis import wales_analysis

from epc_data_analysis.analysis.notebooks import my_widgets

# %%
# Load Wales EPC data
epc_df = epc_data.load_EPC_data(cert_subset="Wales")
# epc_df.head()

# %%
epc_df = epc_df.drop(epc_df[epc_df.TENURE == "NO DATA!"].index)
epc_df = feature_engineering.get_new_EPC_rating_features(epc_df)

post_df = util_data.get_postcode_loc_df()
epc_df = pd.merge(epc_df, post_df, on=["POSTCODE"])


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
# easy_plotting.plot_distribution_by_category(epc_df, 'TENURE', normalize=True, y_ticklabel_type='k', plot_title='Distribution of Tenure Types', y_label='# dwellings')

column_midi = my_widgets.get_dropdown_midi(epc_df)


@interact(category=column_midi)
def plot_distribution(category):
    easy_plotting.plot_distribution_by_category(
        epc_df, category, normalize=True, y_label="# dwellings"
    )


# %%

# %% tags=[]

efficiency_order = ["Very Good", "Good", "Average", "Poor", "Very Poor"]
tenure_type_order = ["rental (social)", "rental (private)", "owner-occupied", "unknown"]

easy_plotting.plot_groups_by_other_groups(
    epc_df,
    "TENURE",
    "MAINHEAT_ENERGY_EFF",
    feature_1_order=tenure_type_order,
    feature_2_order=efficiency_order,
    y_ticklabel_type="",
    y_label="# dwellings",
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
        "SHEATING_ENERGY_EFF",
        "SHEATING_ENV_EFF",
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
        y_ticklabel_type="",
        y_label="# dwellings",
        normalize=False,
    )


# %%
@interact(feature=["CO2_EMISSIONS_CURRENT", "CO2_EMISS_CURR_PER_FLOOR_AREA"])
def emissions_by_tenure_type(feature):
    wales_analysis.emissions_by_tenure_type(epc_df, feature)


# %%
