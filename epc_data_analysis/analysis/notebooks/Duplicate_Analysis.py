# -*- coding: utf-8 -*-
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
# # EPC Anlaysis for England
#
#
# ### What Do We Want to Find?
#
#
# ### Structure of this Notebook<a id='top'></a>
#
#
#
#

# %%
import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact
import re

from epc_data_analysis import PROJECT_DIR
from epc_data_analysis.getters import epc_data, util_data
from epc_data_analysis.pipeline import feature_engineering, data_cleaning
from epc_data_analysis.visualisation import easy_plotting
from epc_data_analysis.analysis.notebooks.notebook_utils import my_widgets

# %% [markdown]
# ## Data Loading and Preprocessing<a id='loading'></a>
# [[back to top]](#top)
#
#
# ### Select Subset of EPC data
# Select the part of the UK for which to load EPC data and select the features of interest. Loading all features at once is not recommended as it considerably slows down processing.

# %%
# Display dataset widgets
display(my_widgets.UK_part_widget)
display(my_widgets.duplicate_widget)
display(my_widgets.preprocessed_feat_widget)

# %% [markdown]
# ### Load EPC data
#

# %%
# Get parameters from widgets
UK_part = my_widgets.UK_part_widget.value
version = (
    "preprocessed_dedupl"
    if my_widgets.duplicate_widget.value == "Without Duplicates"
    else "preprocessed"
)
features_of_interest = my_widgets.preprocessed_feat_widget.value


epc_df = epc_data.load_preprocessed_epc_data(
    version=version, usecols=features_of_interest
)

# %%
if UK_part != "GB":
    epc_df = epc_df.loc[epc_df["COUNTRY"] == UK_part]


# %%
@interact(category=column_widgets)
def plot_value_counts(category):
    print(epc_df[category].value_counts(dropna=False))


# %% [markdown]
# ### Analysis of Duplicates

# %%
unique_building_ids = len(epc_df["BUILDING_ID"].unique())
unique_building_ref_nr = len(epc_df["BUILDING_REFERENCE_NUMBER"].unique())

print("Total:", epc_df.shape[0])
print("Unique by BUILDING_ID:", unique_building_ids)
print("Unique by BUILDING_REFERENCE_NUMBER:", unique_building_ref_nr)

# %%
df_2019_last.loc[df_2019_last.BUILDING_REFERENCE_NUMBER == TEST_NUMBER].head()

# %%
n_entries_analysis = True

if n_entries_analysis:

    df_2019 = feature_engineering.filter_by_year(
        epc_df, "BUILDING_ID", 2019, up_to=True
    )
    df_2019_first = feature_engineering.filter_by_year(
        epc_df, "BUILDING_ID", 2019, up_to=True, selection="first entry"
    )
    df_2019_last = feature_engineering.filter_by_year(
        epc_df, "BUILDING_ID", 2019, up_to=True, selection="latest entry"
    )

    print(df_2019.shape)
    print(df_2019_first.shape)
    print(df_2019_last.shape)

    TEST_NUMBER = 9686127278

    print(
        df_2019_last.loc[df_2019_last.BUILDING_REFERENCE_NUMBER == TEST_NUMBER][
            "INSPECTION_DATE"
        ]
    )
    print(
        df_2019_first.loc[df_2019_first.BUILDING_REFERENCE_NUMBER == TEST_NUMBER][
            "INSPECTION_DATE"
        ]
    )

# %%
latest_df = feature_engineering.filter_by_year(
    epc_df, "BUILDING_ID", None, selection="latest entry"
)
first_df = feature_engineering.filter_by_year(
    epc_df, "BUILDING_ID", None, selection="first entry"
)

print(epc_df.shape)
print(latest_df.shape)
print(first_df.shape)

latest_df["NOW_HP"] = latest_df["HP_INSTALLED"]
first_df["PAST_HP"] = first_df["HP_INSTALLED"]


# %%
latest_df["YEAR_NOW"] = latest_df["ENTRY_YEAR_INT"]
first_df["YEAR_PAST"] = first_df["ENTRY_YEAR_INT"]

# %%
first_df = first_df[["PAST_HP", "BUILDING_ID", "YEAR_PAST"]]
latest_df = latest_df[
    ["NOW_HP", "BUILDING_ID", "YEAR_NOW", "N_ENTRIES_BUILD_ID", "HP_TYPE"]
]

unique_epc_df = feature_engineering.filter_by_year(
    epc_df, "BUILDING_ID", None, selection="latest entry"
)
unique_epc_df = pd.merge(latest_df, first_df, on=["BUILDING_ID"])
unique_epc_df.head()

# %%
unique_epc_df["ENTRY_DIFF"] = unique_epc_df["YEAR_NOW"] - unique_epc_df["YEAR_PAST"]
unique_epc_df.head()

# %%
unique_epc_df.loc[unique_epc_df["NOW_HP"] == True]["ENTRY_DIFF"].mean()

# %%
unique_epc_df["CHANGE_TO_HP"] = (unique_epc_df["NOW_HP"] == True) & (
    unique_epc_df["PAST_HP"] == False
)
unique_epc_df["CHANGE_TO_NON_HP"] = (unique_epc_df["NOW_HP"] == False) & (
    unique_epc_df["PAST_HP"] == True
)

print(unique_epc_df["NOW_HP"].sum())
print(unique_epc_df["PAST_HP"].sum())
print(unique_epc_df["CHANGE_TO_HP"].sum())
print(unique_epc_df["CHANGE_TO_NON_HP"].sum())

# %%
unique_epc_df.head()

# %%
len(
    unique_epc_df.loc[(unique_epc_df["NOW_HP"] == True)][
        (unique_epc_df["N_ENTRIES_BUILD_ID"] > 1)
    ]
)

# %%
unique_epc_df.loc[(unique_epc_df["CHANGE_TO_NON_HP"] == True)]

# %%
unique_epc_df.loc[(unique_epc_df["CHANGE_TO_NON_HP"] == True)][
    "HEATING_SYSTEM"
].value_counts()

# %% [markdown]
# ### BUILDING REFERENCE
#
# Only one samples does not have BUILDING_REFERENCE_NUMBER

# %%
if n_entries_analysis:
    epc_df = feature_engineering.get_build_entry_feature(epc_df)

    # How many are dropped
    print(epc_df.shape)
    epc_df.dropna(subset=["BUILDING_REFERENCE_NUMBER"], inplace=True)
    print(epc_df.shape)

# %%
if n_entries_analysis:
    epc_df_unique = all_entry_df.drop_duplicates(
        subset=["BUILDING_REFERENCE_NUMBER"], keep="last"
    )
    easy_plotting.plot_subcategory_distribution(
        epc_df_unique,
        "N_ENTRIES",
        normalize=True,
        y_label="Properties",
        plot_title="N Entries",
        x_tick_rotation=45,
    )

    print(epc_df.shape)
    print(epc_df_unique.shape)

# %%
n_entries_analysis = True

if n_entries_analysis:
    epc_df_unique = all_entry_df.drop_duplicates(subset=["BUILDING_ID"], keep="last")
    easy_plotting.plot_subcategory_distribution(
        epc_df_unique,
        "N_ENTRIES_BUILD_ID",
        normalize=True,
        y_label="Properties",
        plot_title="N Entries",
        x_tick_rotation=45,
    )

    print(epc_df.shape)
    print(epc_df_unique.shape)

# %%
if n_entries_analysis:
    easy_plotting.plot_subcats_by_other_subcats(
        all_entry_df,
        "COUNTRY",
        "N_ENTRIES",
        feature_2_order=[1, 2, 3, 4, 5],
        normalize=True,
        plotting_colors="viridis_r",
        y_ticklabel_type="%",
        plot_title="# Entries for same property",
    )


# %%
@interact(country=["Wales", "England", "Scotland"])
def plot_EPC_rating_by_sectors(country):

    easy_plotting.plot_feature_by_subcategories(
        epc_df, "N_ENTRIES", "COUNTRY", country, plot_kind="bar", x_tick_rotation=45
    )


# %% [markdown]
# ### Heat Pump Analysis

# %%
epc_df["HAS_HP"] = epc_df["HEATING_SYSTEM"] == "heat pump"

heat_pump_df = epc_df.loc[epc_df["HEATING_SYSTEM"] == "heat pump"]
non_heat_pump_df = epc_df.loc[epc_df["HEATING_SYSTEM"] != "heat pump"]


print("Heat Pump Percentage: {}%".format(heat_pump_df.shape[0] / epc_df.shape[0] * 100))

heat_pump_df["COUNTRY"].value_counts() / epc_df["COUNTRY"].value_counts() * 100

# %%
settings_dict = {
    "BUILT_FORM": (built_form_order, "Built Form", "viridis"),
    "CONSTRUCTION_AGE_BAND": (
        const_year_order_merged,
        "Construction Age Band",
        "viridis",
    ),
    "PROPERTY_TYPE": (prop_type_order, "Property Type", "viridis"),
    "TENURE": (tenure_order, "Sector", "viridis"),
    "HEATING_SOURCE": (heating_source_order, "Heating Source", "viridis"),
    "HEATING_SYSTEM": (None, "Heating System", "viridis"),
    "YEAR": (year_order, "Year of Latest Entry", "viridis"),
    "N_ENTRIES": ([1, 2, 3, 4, 5], "Number of Entries", "viridis"),
    "N_ENTRIES_BUILD_ID": ([1, 2, 3, 4, 5], "Number of Entries", "viridis"),
    "CURRENT_ENERGY_RATING": (rating_order, "Current Energy Rating", "RdYlGn"),
    "COUNTRY": (country_order, "Country", "viridis"),
}


@interact(feature=settings_dict.keys())
def plot_distribution_of_HP(feature):

    order = settings_dict[feature][0]
    title = settings_dict[feature][1]

    easy_plotting.plot_subcats_by_other_subcats(
        epc_df,
        feature,
        "HAS_HP",
        feature_1_order=order,
        y_ticklabel_type="%",
        x_tick_rotation=45,
        normalize=True,
        plotting_colors="prism",
        plot_title="{} with and without Heat Pumps".format(title),
    )


# %%


@interact(feature=settings_dict.keys(), normalize=[True, False])
def plot_distribution_with_without_HP(feature, normalize):

    title = settings_dict[feature][1]

    if normalize:
        y_ticklabel_type = "%"
    else:
        y_ticklabel_type = "m"

    easy_plotting.plot_subcategory_distribution(
        heat_pump_df,
        feature,
        normalize=normalize,
        y_ticklabel_type=y_ticklabel_type,
        y_label="Properties",
        x_tick_rotation=45,
        plot_title="HP Properties by {}".format(title),
    )

    easy_plotting.plot_subcategory_distribution(
        non_heat_pump_df,
        feature,
        normalize=normalize,
        y_ticklabel_type=y_ticklabel_type,
        y_label="Properties",
        x_tick_rotation=45,
        plot_title="Non-HP Properties by {}".format(title),
    )


# %%
@interact(category=heat_pump_df.columns)
def plot_distribution(category):

    heat_pump_df[category].plot(
        kind="hist",
        bins=50,
        color="lightseagreen",
        title="{} Histogram for HP Properties".format(category),
    )
    plt.show()

    non_heat_pump_df[category].plot(
        kind="hist",
        bins=50,
        color="lightseagreen",
        title="{} Histogram for non-HP Properties".format(category),
    )
    plt.show()

    print(heat_pump_df[category].mean())
    print(non_heat_pump_df[category].mean())


# %% [markdown]
# ## Further Analysis <a id='other'></a>
# [[back to top]](#top)
#
#     - Plot Histogram for any Feature
#     - Plot Feature by Sectors
#     - Plot Subcategories by other Subcategories
#
#
# ### Plot Histogram for any Feature
#
# Plot distribution for any feature in the EPC dataset.

# %%
column_widget = my_widgets.get_custom_widget(
    epc_df.columns,
    description="EPC feature",
    default_value="CURRENT_ENERGY_RATING",
    widget_type="dropdown",
)


@interact(category=column_widget)
def plot_distribution(category):
    easy_plotting.plot_subcategory_distribution(
        epc_df, category, normalize=False, y_label="Properties", x_tick_rotation=45
    )


# %% [markdown]
# ### Plot Feature by Sectors
#
# Plot any feature from EPC data by different sectors.

# %%
@interact(tenure_type=my_widgets.tenure_type_widget, feature=column_widgets)
def plot_distribution_by_sector(tenure_type, feature):

    easy_plotting.plot_feature_by_subcategories(
        epc_df, feature, "TENURE", tenure_type, plot_kind="hist"
    )


# %% [markdown]
# ### Plot Subcategories by other Subcategories
#
# Plot any feature (and its subcategories) from EPC dataset by any other feature (and its subcategories).

# %%
# Get feature widgets
column_widgets_1 = my_widgets.get_custom_widget(
    epc_df.columns,
    description="EPC Feature 1",
    default_value="TENURE",
    widget_type="dropdown",
)
column_widgets_2 = my_widgets.get_custom_widget(
    epc_df.columns,
    description="EPC Feature 2",
    default_value="CURRENT_ENERGY_RATING",
    widget_type="dropdown",
)


# %%
features = list(epc_df.columns)
print(features)


@interact(feature_1=features, feature_2=features[::-1])
def plot_feature_subcats_by_other_feature_subcats(feature_1, feature_2):

    easy_plotting.plot_subcats_by_other_subcats(
        epc_df, feature_1, feature_2, plotting_colors="RdYlGn"
    )

    easy_plotting.plot_subcats_by_other_subcats(
        epc_df, feature_2, feature_1, plotting_colors="RdYlGn"
    )


# %%
def plot_feature_subcats_by_other_feature_subcats(feature_1, feature_2):

    easy_plotting.plot_subcats_by_other_subcats(
        epc_df, feature_1, feature_2, plotting_colors="RdYlGn"
    )

    easy_plotting.plot_subcats_by_other_subcats(
        epc_df, feature_2, feature_1, plotting_colors="RdYlGn"
    )


# %%

# %%
