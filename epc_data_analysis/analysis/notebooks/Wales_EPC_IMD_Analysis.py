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
# # EPC Anlaysis for Wales Properties
#
#
# ### What Do We Want to Find?
#
# In this notebook, we analyse and plot the energy efficiency and household emissions for housing properties in Wales. We put a special focus on the difference between the different sectors: social and private rented and owner-occupied.
#
# For the full report and analysis on Wales emissions and energy efficiency across sectors, please consult this document [here](https://docs.google.com/document/d/1jIx0sU0esqO86-T3qv6VTc9kdpk6pQ7472KRC2rj5RU/edit#heading=h.on1g77x0j864).
#
# Using iPython widgets, you can easily adjust the settings and generate plots for all kinds of computations of features.
#
# ### Structure of this Notebook<a id='top'></a>
#
#
# - [Data Loading and Preprocessing](#loading)
#     - Select subset of EPC dataset (area and features)
#     - Load the EPC data for Wales
#     - Load Index of Multiple Deprivation data for Wales
#     - Merge dataframes on basis of postcodes
#
#
# - [EPC Ratings](#epc_ratings)
#     - Create additional EPC features
#     - Plot EPC Rating Distribution for Different Sectors
#     - Plot Energy Rating for All Sectors at once
#     - Plot Potential Energy Rating Increase for Different Sectors
#     - Plot Distribution of EPC Ratings and other Features
#
#
# - [Index of Multiple Deprivation Wales (WIMD](#wimd)
#     - Plot Index of Multiple Deprivation by Sectors
#     - Plot Distribution of EPC Ratings by IMD Quartiles
#     - Correlation Check between Energy Efficiency and IMD
#
#
# - [Heating, Water and Insulation Efficiency](#heating)
#     - Plot Efficiency Features by Sectors
#     - Plot Efficiency Features by IMD
#     - Create new Heating Features
#     - Plot Heating System and Source by Sectors
#
#
# - [CO2 Emissions](#emissions)
#
#     - Plot CO2 Emissions by Sectors and IMD Decile
#
#
# - [Further Analysis](#other)
#
#     - Plot Histogram for any Feature
#     - Plot Feature by Sectors
#     - Plot Subcategories by other Subcategories
#
#

# %%
import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact
import re

from epc_data_analysis.getters import epc_data, util_data
from epc_data_analysis.pipeline import (
    feature_engineering,
    easy_plotting,
    epc_analysis,
    data_cleaning,
)
from epc_data_analysis.analysis.notebooks.notebook_utils import my_widgets

# %% [markdown]
# ## Data Loading and Preprocessing<a id='loading'></a>
# [[back to top]](#top)
#
#     - Select subset of EPC dataset (area and features)
#     - Load the EPC data for Wales
#     - Load Index of Multiple Deprivation data for Wales
#     - Merge dataframes on basis of postcodes
#
#
#
# ### Select Subset of EPC data
# Select the part of the UK for which to load EPC data and select the features of interest. Loading all features at once is not recommended as it considerably slows down processing.

# %%
# Display dataset widgets
display(my_widgets.UK_part_widget)
display(my_widgets.feature_widget)

# %% [markdown]
# ### Load EPC data
#
# Load EPC data subset according to settings. Furthermore, remove all samples with `NO DATA!` as TENURE value  (only 0.84%) since we are especially interested in this feature and don't want to consider features with no tenure data.

# %%
# Get parameters from widgets
UK_part = my_widgets.UK_part_widget.value
features_of_interest = list(my_widgets.feature_widget.value)

# Load Wales EPC data
epc_df = epc_data.load_epc_data(
    subset=UK_part, usecols=features_of_interest, low_memory=False
)
epc_df.head()

# Remove samples with NO DATA! on tenure type
epc_df = epc_df[epc_df.TENURE != "NO DATA!"]
epc_df.head()

# %% [markdown]
# ### Load IMP (Index of Multiple Deprivation)
#
# Load IMP data and merge datasets using the POSTCODE feature.

# %%
# Load Wales IMD data
wimd_df = util_data.get_WIMD_data()

# Reformat POSTCODE
epc_df = data_cleaning.reformat_postcode(epc_df)
wimd_df = data_cleaning.reformat_postcode(wimd_df)

# Merge datasets
epc_wimd_df = pd.merge(epc_df, wimd_df, on=["POSTCODE"])
epc_wimd_df.head()

# %% [markdown]
# ## EPC Ratings <a id='epc_ratings'></a>
# [[back to top]](#top)
#
#     - Create additional EPC features
#     - Plot EPC Rating Distribution for Different Sectors
#     - Plot Energy Rating for All Sectors at once
#     - Plot Potential Energy Rating Increase for Different Sectors
#     - Plot Distribution of EPC Ratings and other Features
#
#
# ### Create additional EPC features
#
# `CURR_ENERGY_RATING_NUM`: represents EPC rating (A-H) in number instead of letter (A --> 7, B --> 6 etc.)
# This is helpful for computing the difference between two ratings or the average potential increase.
#
# `DIFF_POT_ENERGY_RATING`: represents the difference between the current and the potential energy rating as a number (e.g. 2 if increase from D to B is impossible).
#

# %%
# Add new features
epc_wimd_df = feature_engineering.get_new_EPC_rating_features(epc_wimd_df)
epc_wimd_df.head()


# %% [markdown]
# ### Plot EPC Rating Distribution for Different Sectors
#
# The social rental sector shows on average the highest EPC ratings, with C being the most common category.

# %%
@interact(tenure_type=my_widgets.tenure_type_widget)
def plot_EPC_rating_by_sectors(tenure_type):

    easy_plotting.plot_feature_by_subcategories(
        epc_wimd_df,
        "CURRENT_ENERGY_RATING",
        "TENURE",
        tenure_type,
        plot_kind="bar",
    )


# %% [markdown]
# ### Plot Energy Rating for All Sectors at once
#
# The social rental sector shows on average the highest EPC ratings, with C being the most common category. The private rental sector has slightly worse average ratings with an average rating of D. For the owner-occupied sector the ratings D and E are most common.

# %%
epc_rating_order = ["A", "B", "C", "D", "E", "F", "G"]
tenure_type_order = ["rental (social)", "rental (private)", "owner-occupied", "unknown"]
color_list = ["darkgreen", "green", "greenyellow", "yellow", "orange", "red", "darkred"]

# Plot Energy Rating Distribution by Sector
easy_plotting.plot_subcats_by_other_subcats(
    epc_wimd_df,
    "TENURE",
    "CURRENT_ENERGY_RATING",
    feature_1_order=tenure_type_order,
    feature_2_order=epc_rating_order,
    y_label="# dwellings",
    plotting_colors=color_list,
    plot_title="Current Energy Rating Distribution by Sectors",
)


# %% [markdown]
# ### Plot Potential Energy Rating Increase for Different Sectors
#
# The social rented and owner-occupied sectors have higher potential for improving their EPC ratings since their current ratings are generally lower than for the social renter sector.

# %%
@interact(tenure_type=my_widgets.tenure_type_widget)
def plot_potential_EPC_difference_by_tenure_type(tenure_type):

    easy_plotting.plot_feature_by_subcategories(
        epc_wimd_df,
        "DIFF_POT_ENERGY_RATING",
        "TENURE",
        tenure_type,
        plot_kind="bar",
    )


# %% [markdown]
# ### Plot Distribution of EPC Ratings and other Features
#
# More than one third of all properties have the rating D. Every fourth property has rating C and every fifth property has rating E. The ratings B, F and G are rare. Rating A doesn't even cover 1% of all properties.
#
# When looking at the potential EPC ratings, B and C cover 80% of all properties, showing a high potential higher energy efficiency.
#
# You can also inspect other feature's distribution.

# %%
# Get all features from EPC dataset as widget
column_widgets = my_widgets.get_custom_widget(
    epc_wimd_df.columns,
    description="EPC feature",
    default_value="CURRENT_ENERGY_RATING",
    widget_type="dropdown",
)


@interact(category=column_widgets)
def plot_EPC_rarting_distribution(category):
    easy_plotting.plot_subcategory_distribution(
        epc_wimd_df, category, normalize=True, y_label="# dwellings"
    )


# %% [markdown]
# ## Index of Multiple Deprivation <a id='wimd'></a>
# [[back to top]](#top)
#
#     - Plot Index of Multiple Deprivation by Sectors
#     - Plot Distribution of EPC Ratings by IMD Quartiles
#     - Correlation Check between Energy Efficiency and IMD
#
#
# *Note that a low IMD score signifies a more deprived area, while a high IMD score indicates less deprived areas.*
#
# ### Plot Index of Multiple Deprivation by Sectors
#
# The social rental sector mainly consists of properties with low IMD scores. For the other two sectors, it's more balanced, with few properties from the least deprived areas for the private rental sector and few properties from the most deprived areas in the owner-occupied sector.

# %%
# The the order in which to display efficiency and color map
efficiency_order = ["Very Good", "Good", "Average", "Poor", "Very Poor"]
color_list = ["darkgreen", "green", "greenyellow", "yellow", "orange", "red", "darkred"]


@interact(feature=my_widgets.WIMD_widget)
def plot_IMD_by_sectors(feature):
    easy_plotting.plot_subcats_by_other_subcats(
        epc_wimd_df,
        "TENURE",
        feature,
        feature_1_order=tenure_type_order,
        y_label="# dwellings",
        plotting_colors="RdYlGn",
        plot_title="{} by tenure type".format(feature),
    )


# %% [markdown]
# ### Plot Distribution of EPC Ratings by IMD Quartiles
#
# The distribution of EPC ratings across different IMD (Index of Multiple Deprivation) Quartiles is very similar, with D being the most common category, followed by C and E. The IMD does not seem to considerably effect the EPC ratings.

# %%
@interact(quartile=my_widgets.quartile_type_widget)
def plot_EPC_by_IMD_quartile(quartile):

    easy_plotting.plot_feature_by_subcategories(
        epc_wimd_df,
        "CURRENT_ENERGY_RATING",
        "WIMD Quartile",
        quartile,
        plot_kind="bar",
        plot_title="Current Energy Rating for WIMD Quartile {}".format(quartile),
    )


# %% [markdown]
# ### Correlation Check between Energy Efficiency and IMD
#
# There is no signficant correlation between energy efficiency and IMD. There are probably many other factors that influence energy efficiency, for example location, area density, heating costs, age of building, and ‘who is in charge’.

# %%
# Settings for widgets
social_rental_epc = epc_wimd_df.loc[epc_wimd_df["TENURE"] == "rental (social)"]
private_rental_epc = epc_wimd_df.loc[epc_wimd_df["TENURE"] == "rental (private)"]
owner_epc = epc_wimd_df.loc[epc_wimd_df["TENURE"] == "owner-occupied"]

feature_1 = ["WIMD Score", "WIMD Quartile", "WIMD Quintile", "WIMD Decile", "WIMD Rank"]

feature_2 = [
    "CURRENT_ENERGY_EFFICIENCY",
    "CURR_ENERGY_RATING_NUM",
    "CURRENT_ENERGY_RATING",
    "CO2_EMISSIONS_CURRENT",
]

df_subsets = ["all", "social rental", "private rental", "owner-occupied"]


@interact(
    df_subset=df_subsets,
    feature_1=feature_1,
    feature_2=feature_2,
    ylim_max=my_widgets.ylim_slider_widget,
    with_hist_subplots=True,
)
def check_for_correlation(
    df_subset, feature_1, feature_2, ylim_max, with_hist_subplots
):

    # Select subset
    if df_subset == "all":
        df = epc_wimd_df
    elif df_subset == "social rental":
        df = social_rental_epc
    elif df_subset == "private rental":
        df = private_rental_epc
    elif df_subset == "owner-occupied":
        df = owner_epc
    else:
        raise IOError("Unknown subset '{}'".format(df_subset))

    # Plot correlation between feature 1 and feature 2
    easy_plotting.plot_correlation(
        df,
        feature_1,
        feature_2,
        ylim_max=ylim_max,
        with_hist_subplots=with_hist_subplots,
    )

    # Compute Pearson correlation between feature 1 and feature 2
    pearson_correlation = easy_plotting.get_pearson_correlation(
        df, feature_1, feature_2
    )
    print("Pearson Correlation:", round(pearson_correlation, 3))


# %% [markdown]
# ## Heating, Water and Insulation Efficiency<a id='heating'></a>
# [[back to top]](#top)
#
#     - Plot Efficiency Features by Sectors
#     - Plot Efficiency Features by IMD
#     - Create new Heating Features
#     - Plot Heating System and Source by Sectors
#
#
# ### Plot Efficiency Features by Sectors
#
# For most sectors, "good" is the most frequent rating for the main heat energy efficiency, although the private rental and owner-occupied sector have considerably more properties with a rating of "average" or below.
#
# You can also insepct other features. For instance, the walls energy efficiency is poor for many properties across sectors.

# %%
@interact(feature_2=my_widgets.efficiency_widget)
def plot_efficiency_by_sectors(feature_2):
    easy_plotting.plot_subcats_by_other_subcats(
        epc_wimd_df,
        "TENURE",
        feature_2,
        feature_1_order=tenure_type_order,
        feature_2_order=efficiency_order,
        y_ticklabel_type="k",
        plotting_colors=None,
        y_label="# dwellings",
    )


# %% [markdown]
# ### Plot Efficiency Features by IMD
#
# As observed above, there is no strong correlation between energy efficiency and IMD so there are no signficant fluctuations in the energy efficiency across the different WIMD Deciles, Quartiles or Quintiles.

# %%
social_epc = epc_wimd_df.loc[epc_wimd_df["TENURE"] == "rental (social)"]


@interact(feature_1=my_widgets.WIMD_widget, feature_2=my_widgets.efficiency_widget)
def plot_efficiency_by_IMD(feature_1, feature_2):
    easy_plotting.plot_subcats_by_other_subcats(
        epc_wimd_df,
        feature_1,
        feature_2,
        feature_2_order=efficiency_order,
        y_ticklabel_type="k",
        plotting_colors=None,
        y_label="# dwellings",
    )


# %% [markdown]
# ### Create new Heating Features
#
# Features created on basis of free text feature `MAINHEAT_DESCRIPTION`.
#
# `HEATING_SYSTEM`: Heating system (heat pump, underfloor heating, boiler and radiator etc.)
#
# `HEATING_SOURCE`: Source energy for heating (electric, oil, gas, LPG)
#
# ------
#
# `...EFF_AS_NUM`: The function *map_quality_to_number* generates numeric feature for efficiency features with values `very good` to `very poor`.
#
# For example, for `MAINHEAT_ENERGY_EFF` a new feature `MAINHEAT_ENERGY_EFF_AS_NUM` is created with numbers representing the efficiency instead of strings, e.g. `very good` --> 5 and `average` --> 3.

# %%
# Get new heating features
epc_wimd_df = feature_engineering.get_heating_features(epc_wimd_df)

# Generate numeric feature for mainheat efficiency (not used here)
epc_wimd_df = feature_engineering.map_quality_to_number(
    epc_wimd_df, ["MAINHEAT_ENERGY_EFF"]
)
epc_wimd_df.head()


# %% [markdown]
# ### Plot Heating System and Source by Sectors
#
# The boiler and radiator combi is by far the most common heating system while gas is clearly the most common heating source.

# %%
@interact(
    feature_1="TENURE",
    feature_2=["HEATING_SYSTEM", "HEATING_SOURCE"],
    only_social_properties=False,
)
def plot_heating_system_and_source(feature_1, feature_2, only_social_properties):

    # Settings if only social properties are inspected
    if only_social_properties:
        selected_df = epc_wimd_df.loc[epc_wimd_df["TENURE"] == "rental (social)"]
        tenure_type_order = ["rental (social)"]

    # Settings if looking at all sectors
    else:
        selected_df = epc_wimd_df
        tenure_type_order = [
            "rental (social)",
            "rental (private)",
            "owner-occupied",
            "unknown",
        ]

    # Set feature order for heating source
    if feature_2 == "HEATING_SOURCE":
        feature_2_order = ["oil", "gas", "LPG", "electric", "unknown"]
    else:
        feature_2_order = None

    # Plot sector by heating feature
    easy_plotting.plot_subcats_by_other_subcats(
        selected_df,
        feature_1,
        feature_2,
        feature_1_order=tenure_type_order,
        feature_2_order=feature_2_order,
        y_ticklabel_type="k",
        y_label="# dwellings",
        plotting_colors="RdYlGn",
    )


# %% [markdown]
# ## CO2 Emissions <a id='emissions'></a>
# [[back to top]](#top)
#
#     - Plot CO2 Emissions by Sectors and IMD Decile
#
#
# ### Plot CO2 Emissions by Sectors and IMD Deciles
#
# Emissions are lower in the rental sector than in the owner-occupied sector in Wales, even when normalising by the number of dwellings or by floor area.
#
# The WIMD Deciles 5-7 have the highest CO2 Emissions, although there is no strong fluctuation across the different WIMD Deciles.

# %%
@interact(
    feature_1=["CO2_EMISSIONS_CURRENT", "CO2_EMISS_CURR_PER_FLOOR_AREA"],
    feature_2=["TENURE", "WIMD Decile"],
)
def plot_CO2_emissions(feature_1, feature_2):

    # Get emission data and settings
    # ----------------------------------------------------

    emissions_dict = epc_analysis.get_emissions_info(epc_wimd_df, feature_1, feature_2)

    descr_part_1 = (
        "CO2 Emissions"
        if feature_1 == "CO2_EMISSIONS_CURRENT"
        else "CO2 Emissions per Floor Area"
    )
    descr_part_2 = "by Tenure Type" if feature_2 == "TENURE" else "by WIMD Decile"

    # Set tick roation and position
    x_tick_rotation, x_tick_ha = (
        (45, "right") if feature_2 == "TENURE" else (0, "center")
    )

    # Where to save figures
    FIG_PATH = easy_plotting.FIG_PATH

    # Plot relative emissions
    # ----------------------------------------------------

    # Get relative emissions as bar plot
    emissions_dict["relative emissions"].plot(kind="bar", color="lightseagreen")

    # Get highest counter value for adjusting plot format
    highest_count = max([cty for cty in emissions_dict["relative emissions"].values])

    # Display count for every bar on top of bar
    ax = plt.gca()

    for i, cty in enumerate(emissions_dict["relative emissions"].values):
        ax.text(
            i,
            cty + highest_count / 25,
            str(round(cty, 1)) + "%",
            horizontalalignment="center",
        )

    # Adjust the ylimit of the plot
    ax.set_ylim([0.0, highest_count + highest_count / 5])

    #  Set title, ticks and labels
    plt.title("{} {} (%)".format(descr_part_1, descr_part_2))
    plt.xticks(rotation=x_tick_rotation, ha=x_tick_ha)
    plt.xlabel("")

    # Set ylabel (with ompute total emissions)
    plt.ylabel(
        "CO2 Emissions (%)\n(total of {}k tonnes/year)".format(
            str(round(emissions_dict["total"], 0))[:-3]
        )
    )

    # Save and show
    plt.tight_layout()
    filename = "{} {} (relative)".format(descr_part_1, descr_part_2)
    filename = re.sub(" ", "_", filename)

    plt.savefig(FIG_PATH + filename)
    plt.show()

    # Plot absolute emissions
    # ----------------------------------------------------

    # Get absolute emissions as bar plot
    emissions_dict["absolute emissions"].plot(kind="bar", color="lightseagreen")

    # Get highest counter value for adjusting plot format
    highest_count = max([cty for cty in emissions_dict["absolute emissions"].values])

    # Set yticklabels
    ylabels, ax, division_int, division_type = easy_plotting.get_readable_tick_labels(
        plt, "k", "y"
    )
    ax.set_yticklabels(ylabels)

    # Display count for every bar on top of bar
    ax = plt.gca()

    for i, cty in enumerate(emissions_dict["absolute emissions"].values):
        ax.text(
            i,
            cty + highest_count / 25,
            str(int(cty / division_int)) + division_type,
            horizontalalignment="center",
        )

    # Adjust the ylimit of the plot
    ax.set_ylim([0.0, highest_count + highest_count / 5])

    # Set title, ticks and labels
    plt.title("{} {} (%)".format(descr_part_1, descr_part_2))
    plt.xticks(rotation=x_tick_rotation, ha=x_tick_ha)
    plt.xlabel("")
    plt.ylabel("CO2 Emissions\n[tonnes/year]")

    # Save and show
    plt.tight_layout()
    filename = "{} {} (absolute)".format(descr_part_1, descr_part_2)
    filename = re.sub(" ", "_", filename)

    plt.savefig(FIG_PATH + filename)
    plt.show()

    # Plot emissions per dwelling
    # ----------------------------------------------------

    # Get number of dwellings/properties
    n_dwellings = epc_wimd_df.shape[0]

    # Get emissions by dwelling
    emissions_dict["emisisons by dwelling"].plot(kind="bar", color="lightseagreen")

    # Get highest counter value for adjusting plot format
    highest_count = max([cty for cty in emissions_dict["emisisons by dwelling"].values])

    # Display count for every bar on top of bar
    ax = plt.gca()

    for i, cty in enumerate(emissions_dict["emisisons by dwelling"].values):
        ax.text(
            i, cty + highest_count / 25, round(cty, 1), horizontalalignment="center"
        )

    # Set ylabels in desired format
    ylabels = ["{:.0f}".format(x) for x in ax.get_yticks()]
    ax.set_yticklabels(ylabels)

    # Set title, labels and ticks
    plt.title("{} per Dwelling {}".format(descr_part_1, descr_part_2))
    plt.ylabel("CO2 Emissions\n[tonnes/year/dwelling]")
    plt.xticks(rotation=x_tick_rotation, ha=x_tick_ha)

    # Adjust the ylimit of the plot
    ax.set_ylim([0.0, highest_count + highest_count / 5])

    # Save and show
    plt.tight_layout()
    filename = "{} per Dwelling {}".format(descr_part_1, descr_part_2)
    filename = re.sub(" ", "_", filename)

    plt.savefig(FIG_PATH + filename)
    plt.show()


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
    epc_wimd_df.columns,
    description="EPC feature",
    default_value="CURRENT_ENERGY_RATING",
    widget_type="dropdown",
)


@interact(category=column_widget)
def plot_distribution(category):
    easy_plotting.plot_subcategory_distribution(
        epc_wimd_df, category, normalize=True, y_label="# dwellings"
    )


# %% [markdown]
# ### Plot Feature by Sectors
#
# Plot any feature from EPC data by different sectors.

# %%
@interact(tenure_type=my_widgets.tenure_type_widget, feature=column_widgets)
def plot_distribution_by_sector(tenure_type, feature):

    easy_plotting.plot_feature_by_subcategories(
        epc_wimd_df, feature, "TENURE", tenure_type, plot_kind="hist"
    )


# %% [markdown]
# ### Plot Subcategories by other Subcategories
#
# Plot any feature (and its subcategories) from EPC dataset by any other feature (and its subcategories).

# %%
# Get feature widgets
column_widgets_1 = my_widgets.get_custom_widget(
    epc_wimd_df.columns,
    description="EPC Feature 1",
    default_value="MAINHEAT_ENERGY_EFF",
    widget_type="dropdown",
)
column_widgets_2 = my_widgets.get_custom_widget(
    epc_wimd_df.columns,
    description="EPC Feature 2",
    default_value="HEATING_SOURCE",
    widget_type="dropdown",
)


@interact(feature_1=column_widgets_1, feature_2=column_widgets_2)
def plot_feature_subcats_by_other_feature_subcats(feature_1, feature_2):

    easy_plotting.plot_subcats_by_other_subcats(
        epc_wimd_df, feature_1, feature_2, plotting_colors="RdYlGn"
    )


# %%
