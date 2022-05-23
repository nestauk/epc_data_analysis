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
from epc_data_analysis.getters import epc_data, deprivation_data, util_data
from epc_data_analysis.pipeline import epc_analysis
from epc_data_analysis.pipeline.preprocessing import (
    feature_engineering,
    data_cleaning,
    preprocess_epc_data,
)
from epc_data_analysis.visualisation import easy_plotting, feature_settings, my_widgets

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

# %%
my_widgets.preprocessed_feat_widget.value

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
features_of_interest = my_widgets.preprocessed_feat_widget.value + (
    "HEATING_SYSTEM",
    "HEATING_FUEL",
    "NUMBER_HABITABLE_ROOMS",
    "WINDOWS_ENERGY_EFF",
    "FLOOR_ENERGY_EFF",
    "WALLS_ENERGY_EFF",
    "LIGHTING_ENERGY_EFF",
    "HOT_WATER_ENERGY_EFF",
    "MAINHEAT_ENERGY_EFF",
    "ROOF_ENERGY_EFF",
    "MAINHEATC_ENERGY_EFF",
)

# features_of_interest = ['CONSTRUCTION_AGE_BAND', 'CURRENT_ENERGY_RATING']

epc_df = epc_data.load_preprocessed_epc_data(
    version=version, usecols=features_of_interest
)
# epc_df = preprocess_epc_data.load_and_preprocess_epc_data()

if UK_part != "GB":
    epc_df = epc_df.loc[epc_df["COUNTRY"] == UK_part]


# %%
print(epc_df.shape)
print(version)

# %%
imd_df = deprivation_data.get_GB_IMD_data()
epc_imd_df = deprivation_data.merge_IMD_with_other_set(imd_df, epc_df)
epc_imd_df = epc_imd_df.rename(columns={"Postcode": "POSTCODE"})
epc_df = epc_imd_df

# %%
print("GB total:\t", epc_df.shape)

england = epc_df.loc[epc_df["COUNTRY"] == "England"]
print("England:\t", england.shape)

wales = epc_df.loc[epc_df["COUNTRY"] == "Wales"]
print("Wales:\t", wales.shape)

scotland = epc_df.loc[epc_df["COUNTRY"] == "Scotland"]
print("Scotland:\t", scotland.shape)


df_dict = {"England": england, "Wales": wales, "Scotland": scotland, "GB": epc_df}

# %%
epc_df["CONSTRUCTION_AGE_BAND"].value_counts(dropna=False)

# %% [markdown]
# ### Country specific

# %%
column_widgets = my_widgets.get_custom_widget(
    epc_df.columns,
    description="EPC Feature",
    default_value="CURRENT_ENERGY_RATING",
    widget_type="dropdown",
)


# %%
@interact(category=column_widgets)
def plot_distribution(category):
    easy_plotting.plot_subcategory_distribution(
        epc_df,
        category,
        normalize=True,
        y_ticklabel_type="%",
        y_label="Properties",
        plot_title="Distribution",
        color="royalblue",
    )


# %% [markdown]
# ## General Country Data

# %%
easy_plotting.plot_subcategory_distribution(
    epc_df,
    "COUNTRY",
    normalize=True,
    y_ticklabel_type="%",
    y_label="Properties",
    plot_title="Property Distribution by Country (%)",
)

easy_plotting.plot_subcategory_distribution(
    epc_df,
    "COUNTRY",
    normalize=False,
    y_ticklabel_type="k",
    y_label="Properties",
    plot_title="Property Distribution by Country",
)

# %% [markdown]
# ### Country Vs.

# %%
epc_df["HEATING_SYSTEM"].unique()

# %%
heating_order = [
    "boiler and radiator",
    "boiler and underfloor",
    "underfloor heating",
    "heater",
    "storage heater",
    "heat pump",
    "warm air",
    "community scheme",
    "unknown",
]

settings_dict = {
    "ENTRY_YEAR_INT": (
        feature_settings.year_order,
        "Year of Latest Entry",
        "viridis",
        (10, 5),
        "outside",
    ),
    "CONSTRUCTION_AGE_BAND": (
        feature_settings.const_year_order_merged,
        "Construction Year Band",
        "viridis",
        (10, 5),
        "outside",
    ),
    "LOCAL_AUTHORITY_LABEL": (None, "Local Authority", "viridis", (10, 5), "outside"),
    "CURRENT_ENERGY_RATING": (
        feature_settings.rating_order,
        "Current Energy Rating",
        "RdYlGn",
        None,
        None,
    ),
    "POTENTIAL_ENERGY_RATING": (
        feature_settings.rating_order,
        "Potential Energy Rating",
        "RdYlGn",
        None,
        None,
    ),
    "PROPERTY_TYPE": (
        feature_settings.prop_type_order,
        "Property Type",
        "viridis",
        None,
        None,
    ),
    "BUILT_FORM": (
        feature_settings.built_form_order,
        "Built Form",
        "viridis",
        None,
        None,
    ),
    "TENURE": (feature_settings.tenure_order, "Sector", "viridis", None, None),
    "COUNTRY": (feature_settings.country_order, "Country", "viridis", None, None),
    "HEATING_FUEL": (
        feature_settings.heating_source_order,
        "Heating Fuel",
        "viridis",
        None,
        None,
    ),
    "HEATING_SYSTEM": (heating_order, "Heating System", "winter", None, None),
    "N_ENTRIES": (
        None,
        "Number of Entries (based on Build. Reference Nr.)",
        "viridis_r",
        None,
        None,
    ),
    "N_ENTRIES_BUILD_ID": (None, "Number of Entries", "viridis_r", None, None),
}


# %%
@interact(feature_1=column_widgets, country=feature_settings.country_order)
def plot_by_country(feature_1, country):

    f_name = settings_dict[feature_1][1]

    easy_plotting.plot_feature_by_subcategories(
        epc_df,
        feature_1,
        "COUNTRY",
        country,
        plot_kind="bar",
        plot_title="{} Distribution for {}".format(f_name, country),
    )


# %%
@interact(feature=["HEATING_SYSTEM"] + list(settings_dict.keys()))
def plot_distr_by_country(feature):

    settings = settings_dict[feature]

    order, title, color_map = settings[0], settings[1], settings[2]
    print(order)
    figsize, legend_loc = settings[3], settings[4]

    easy_plotting.plot_subcats_by_other_subcats(
        epc_df,
        "COUNTRY",
        feature,
        feature_1_order=feature_settings.country_order,
        feature_2_order=order,
        y_ticklabel_type="%",
        normalize=True,
        legend_loc=legend_loc,
        figsize=figsize,
        fig_save_path=str(PROJECT_DIR) + "/outputs/",
        plotting_colors=color_map,
        plot_title="{} by Country (%)".format(title),
    )


# %%
@interact(feature=settings_dict.keys())
def plot_EPC_by_other_feature(feature):

    order = settings_dict[feature][0]
    title = settings_dict[feature][1]
    color_map = settings_dict[feature][2]

    easy_plotting.plot_subcats_by_other_subcats(
        epc_df,
        feature,
        "CURRENT_ENERGY_RATING",
        feature_1_order=order,
        feature_2_order=feature_settings.rating_order,
        y_ticklabel_type="%",
        x_tick_rotation=45,
        normalize=True,
        plotting_colors="RdYlGn",
        plot_title="Energy Rating by {} (%)".format(title),
    )


# %%
features = list(settings_dict.keys())


@interact(feature_1=features, feature_2=features[::-1])
def plot_feature_by_feature(feature_1, feature_2):

    order_1 = settings_dict[feature_1][0]
    order_2 = settings_dict[feature_2][0]

    title_1 = settings_dict[feature_1][1]
    title_2 = settings_dict[feature_2][1]

    color_map = settings_dict[feature_1][2]

    easy_plotting.plot_subcats_by_other_subcats(
        epc_df,
        feature_1,
        feature_2,
        feature_1_order=order_1,
        feature_2_order=order_2,
        normalize=False,
        plotting_colors="viridis",
        y_ticklabel_type="%",
        x_tick_rotation=45,
        plot_title="{} by {} (%)".format(title_2, title_1),
    )


# %% [markdown]
# ### Efficiency Levels

# %%
title_dict = {
    "WINDOWS_ENERGY_EFF": "Window Energy Efficiency",
    "FLOOR_ENERGY_EFF": "Floor Energy Efficiency",
    "WALLS_ENERGY_EFF": "Walls Energy Efficiency",
    "LIGHTING_ENERGY_EFF": "Lighting Energy Efficiency",
    "HOT_WATER_ENERGY_EFF": "Hot Water Energy Efficiency",
}


@interact(
    feature=[
        "WINDOWS_ENERGY_EFF",
        "FLOOR_ENERGY_EFF",
        "WALLS_ENERGY_EFF",
        "LIGHTING_ENERGY_EFF",
        "HOT_WATER_ENERGY_EFF",
    ]
)
def plot_efficiency(feature):
    easy_plotting.plot_subcats_by_other_subcats(
        epc_df,
        "COUNTRY",
        feature,
        y_ticklabel_type="%",
        normalize=True,
        feature_1_order=feature_settings.country_order,
        feature_2_order=feature_settings.efficiency_order[1:]
        if feature in ["HOT_WATER_ENERGY_EFF"]
        else feature_settings.efficiency_order,
        plotting_colors="RdYlGn",
        plot_title="{} by Country".format(title_dict[feature]),
    )


# %%
title_dict = {
    "MAINHEAT_ENERGY_EFF": "Main Heat Energy Efficiency",
    "ROOF_ENERGY_EFF": "Roof Energy Efficiency",
    "MAINHEATC_ENERGY_EFF": "Main Heat Control Energy Efficiency",
}


@interact(feature=["MAINHEAT_ENERGY_EFF", "ROOF_ENERGY_EFF"])
def plot_efficiency(feature):
    easy_plotting.plot_subcats_by_other_subcats(
        epc_df,
        "COUNTRY",
        feature,
        y_ticklabel_type="%",
        normalize=True,
        feature_1_order=["England", "Wales"],
        feature_2_order=feature_settings.efficiency_order[1:],
        plotting_colors="RdYlGn",
        plot_title="{} by Country".format(title_dict[feature]),
    )


# %% [markdown]
# ## CO2 Emissions <a id='emissions'></a>
# [[back to top]](#top)
#
#     - Plot CO2 Emissions by Sectors and IMD Decile
#
#
# ### Plot CO2 Emissions by Sectors
#
# Emissions are lower in the rental sector than in the owner-occupied sector in Wales, even when normalising by the number of dwellings or by floor area.
#
# The WIMD Deciles 5-7 have the highest CO2 Emissions, although there is no strong fluctuation across the different WIMD Deciles.
#
#

# %%
def save_figure(plt, plot_title=None, fig_path=None, file_extension=".png", dpi=1000):
    """Create filename and save figure.

    Parameters
    ----------

    plt : matplotlib.pyplot
        Plot to save.

    plot_title: str, None, default=None
        Use plot title to generate filename.
        If None, use "figure" as filename.

    fig_path: str, None, default=None
        Where to save the plot.
        If not specified, use FIG_PATH given by config file.

    file_extension: str, default=".png"
        File extension, file format to save.

    dpi: int, default=500
        Dots per inches (dpi) determines how many pixels the figure comprises.


    Return
    ----------
        None"""

    # Tight layout
    # plt.tight_layout()

    # Automatically generate filename
    if plot_title is not None:
        save_filename = plot_title
        save_filename = re.sub(" ", "_", save_filename)

    # Use "figure" as filename as default
    else:
        save_filename = "figure.png"

    # Adjust figure path if necessary
    fig_path = fig_path if fig_path is not None else FIG_PATH

    # Save fig
    plt.savefig(fig_path + save_filename + file_extension, dpi=dpi, bbox_inches="tight")


# %%
epc_df["CONSTRUCTION_AGE_BAND"].value_counts()

# %%
# 2

const_year_order_merged = [
    "England and Wales: before 1900",
    "Scotland: before 1919",
    "1900-1929",
    "1930-1949",
    "1950-1966",
    "1965-1975",
    "1976-1983",
    "1983-1991",
    "1991-1998",
    "1996-2002",
    "2003-2007",
    "2007 onwards",
    "unknown",
]

clean_dict = {
    "PROPERTY_TYPE": ("Property Type", feature_settings.prop_type_order),
    "BUILT_FORM": ("Built Form", feature_settings.built_form_order),
    "CURRENT_ENERGY_RATING": ("Current EPC Rating", feature_settings.rating_order[:-1]),
    "CONSTRUCTION_AGE_BAND": ("Construction Age", const_year_order_merged),
    "ENTRY_YEAR": ("Year of Entry", None),
    "TENURE": ("Tenure Sector", None),
    "COUNTRY": ("Country", None),
    "MAINS_GAS_FLAG": ("Mains Gas Flag", None),
    "NUMBER_HABITABLE_ROOMS": ("Number Habitable Rooms", None),
    "LOCAL_AUTHORITY_LABEL": ("Local Authority", None),
    "IMD Decile": ("IMD Decile", None),
    "Income Score": ("Income Score", None),
}


@interact(
    feature_1=["CO2_EMISSIONS_CURRENT", "CO2_EMISS_CURR_PER_FLOOR_AREA"],
    feature_2=[
        "TENURE",
        "PROPERTY_TYPE",
        "BUILT_FORM",
        "CURRENT_ENERGY_RATING",
        "CONSTRUCTION_AGE_BAND",
        "ENTRY_YEAR",
        "COUNTRY",
        "MAINS_GAS_FLAG",
        "NUMBER_HABITABLE_ROOMS",
        "LOCAL_AUTHORITY_LABEL",
        "IMD Decile",
        "Income Score",
    ],
    country=["GB", "Scotland", "Wales", "England"],
)
def plot_CO2_emissions(feature_1, feature_2, country):

    # Get emission data and settings
    # ----------------------------------------------------

    df = df_dict[country]

    title_tag, order = clean_dict[feature_2]

    emissions_dict = epc_analysis.get_emissions_info(df, feature_1, feature_2)

    if order is not None:

        for key in emissions_dict.keys():
            if not key.startswith("total"):
                emissions_dict[key] = emissions_dict[key][order]

    descr_part_1 = (
        "{} CO2 Emissions".format(country)
        if feature_1 == "CO2_EMISSIONS_CURRENT"
        else "{} CO2 Emissions per Floor Area".format(country)
    )
    descr_part_2 = "by {}".format(title_tag)

    # Set tick roation and position
    x_tick_rotation, x_tick_ha = (45, "right")

    print(easy_plotting.FIG_PATH)

    # Where to save figures
    FIG_PATH = easy_plotting.FIG_PATH + "emissions/"

    axis_label = (
        "[kg/m²/year]"
        if feature_1 == "CO2_EMISS_CURR_PER_FLOOR_AREA"
        else "[tonnes/dwelling/year]"
    )

    # Plot relative emissions
    # ----------------------------------------------------

    # fig = plt.gcf()
    # fig.set_size_inches(7.5, 5)

    if feature_2 in ["LOCAL_AUTHORITY_LABEL"]:
        fig = plt.gcf()
        fig.set_size_inches(10, 5)

        if country == "England":
            fig.set_size_inches(50, 10)

    # Get relative emissions as bar plot
    emissions_dict["relative emissions"].plot(kind="bar", color="royalblue")

    # Get highest counter value for adjusting plot format
    highest_count = max([cty for cty in emissions_dict["relative emissions"].values])

    # Display count for every bar on top of bar
    ax = plt.gca()

    # ax = df.set_index(field).loc[order]

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
    plt.title("{} (%) {}".format(descr_part_1, descr_part_2))
    plt.xticks(rotation=x_tick_rotation, ha=x_tick_ha)
    plt.xlabel("")

    # Set ylabel (with ompute total emissions)
    plt.ylabel("CO2 Emissions (%)".format(str(round(emissions_dict["total"], 0))[:-3]))
    # # Set ylabel (with ompute total emissions)
    #  plt.ylabel(
    #     "CO2 Emissions (%)\n(total of {}k tonnes/year)".format(
    #         str(round(emissions_dict["total"], 0))[:-3]
    #    )
    #   )

    # Save and show
    plt.tight_layout()
    filename = "{} {} relative".format(descr_part_1, descr_part_2)
    filename = re.sub(" ", "_", filename)

    plt.savefig(FIG_PATH + filename, dpi=2000, bbox_inches="tight")
    plt.show()

    # Plot absolute emissions
    # ----------------------------------------------------

    if feature_2 in ["LOCAL_AUTHORITY_LABEL"]:
        fig = plt.gcf()
        fig.set_size_inches(10, 5)

        if country == "England":
            fig.set_size_inches(50, 10)

    # Get absolute emissions as bar plot
    emissions_dict["absolute emissions"].plot(kind="bar", color="royalblue")

    # Get highest counter value for adjusting plot format
    highest_count = max([cty for cty in emissions_dict["absolute emissions"].values])

    # Set yticklabels
    ylabels, ax, division_int, division_type = easy_plotting.get_readable_tick_labels(
        plt, "m", "y"
    )
    ax.set_yticklabels(ylabels)

    # Display count for every bar on top of bar
    ax = plt.gca()

    for i, cty in enumerate(emissions_dict["absolute emissions"].values):
        ax.text(
            i,
            cty + highest_count / 25,
            str(round(cty / division_int, 1)) + division_type,
            horizontalalignment="center",
        )

    # Adjust the ylimit of the plot
    ax.set_ylim([0.0, highest_count + highest_count / 5])

    # Set title, ticks and labels
    plt.title("{} {}".format(descr_part_1, descr_part_2))
    plt.xticks(rotation=x_tick_rotation, ha=x_tick_ha)
    plt.xlabel("")
    plt.ylabel("CO2 Emissions\n".format(axis_label))

    # Save and show
    plt.tight_layout()
    filename = "{} {} absolute".format(descr_part_1, descr_part_2)
    filename = re.sub(" ", "_", filename)

    plt.savefig(FIG_PATH + filename, dpi=2000, bbox_inches="tight")
    plt.show()

    # Plot emissions per dwelling
    # ----------------------------------------------------

    if feature_2 in ["LOCAL_AUTHORITY_LABEL"]:
        fig = plt.gcf()
        fig.set_size_inches(10, 5)

        if country == "England":
            fig.set_size_inches(50, 10)

    # Get number of dwellings/properties
    n_dwellings = df.shape[0]

    # Get emissions by dwelling
    emissions_dict["emissions by dwelling"].plot(kind="bar", color="royalblue")

    # Get highest counter value for adjusting plot format
    highest_count = max([cty for cty in emissions_dict["emissions by dwelling"].values])

    # Display count for every bar on top of bar
    ax = plt.gca()

    for i, cty in enumerate(emissions_dict["emissions by dwelling"].values):
        ax.text(
            i, cty + highest_count / 25, round(cty, 1), horizontalalignment="center"
        )

    # Set ylabels in desired format
    ylabels = ["{:.0f}".format(x) for x in ax.get_yticks()]
    ax.set_yticklabels(ylabels)

    # Set title, labels and ticks
    plt.title("{} (per dwelling) {}".format(descr_part_1, descr_part_2))
    plt.ylabel("CO2 Emissions\n{}".format(axis_label))
    plt.xticks(rotation=x_tick_rotation, ha=x_tick_ha)
    plt.xlabel("")

    # Adjust the ylimit of the plot
    ax.set_ylim([0.0, highest_count + highest_count / 5])

    # Save and show
    plt.tight_layout()
    filename = "{} {} mean".format(descr_part_1, descr_part_2)
    filename = re.sub(" ", "_", filename)

    plt.savefig(FIG_PATH + filename, dpi=2000, bbox_inches="tight")
    plt.show()


# %%
# 3

clean_dict = {
    "PROPERTY_TYPE": ("Property Type", feature_settings.prop_type_order),
    "BUILT_FORM": ("Built Form", feature_settings.built_form_order),
    "CURRENT_ENERGY_RATING": ("Current EPC Rating", feature_settings.rating_order),
    "CONSTRUCTION_AGE_BAND": (
        "Construction Age",
        feature_settings.const_year_order_merged,
    ),
    "ENTRY_YEAR": ("Year of Entry", None),
    "TENURE": ("Tenure Sector", feature_settings.tenure_order),
    "COUNTRY": ("Country", None),
    "MAINS_GAS_FLAG": ("Mains Gas Flag", None),
    "NUMBER_HABITABLE_ROOMS": ("Number Habitable Rooms", None),
    "LOCAL_AUTHORITY_LABEL": ("Local Authority", None),
}


@interact(
    feature_1=["CO2_EMISSIONS_CURRENT", "CO2_EMISS_CURR_PER_FLOOR_AREA"],
    feature_2=[
        "TENURE",
        "WIMD Decile",
        "PROPERTY_TYPE",
        "BUILT_FORM",
        "CURRENT_ENERGY_RATING",
        "CONSTRUCTION_AGE_BAND",
        "ENTRY_YEAR",
        "COUNTRY",
        "MAINS_GAS_FLAG",
        "NUMBER_HABITABLE_ROOMS",
        "LOCAL_AUTHORITY_LABEL",
    ],
    country=["GB", "Scotland", "Wales", "England"],
)
def plot_CO2_emissions(feature_1, feature_2, country):

    # Get emission data and settings
    # ----------------------------------------------------

    df = df_dict[country]

    import numpy as np

    title_tag, order = clean_dict[feature_2]

    n_cats = len(df[feature_2].unique())

    emissions_dict = epc_analysis.get_emissions_info(df, feature_1, feature_2)
    emissions_dict_emissions = epc_analysis.get_emissions_info(
        df, "CO2_EMISSIONS_CURRENT", feature_2
    )
    emissions_dict_by_area = epc_analysis.get_emissions_info(
        df, "CO2_EMISS_CURR_PER_FLOOR_AREA", feature_2
    )

    if order is not None:

        for key in emissions_dict.keys():
            if not key.startswith("total"):
                emissions_dict[key] = emissions_dict[key][order]

    descr_part_1 = (
        "{} CO2 Emissions".format(country)
        if feature_1 == "CO2_EMISSIONS_CURRENT"
        else "{} CO2 Emissions per Floor Area".format(country)
    )
    descr_part_2 = "by {}".format(title_tag)

    # Set tick roation and position
    x_tick_rotation, x_tick_ha = (45, "right")

    # Where to save figures
    FIG_PATH = easy_plotting.FIG_PATH + "Emissions/"

    # Plot relative emissions
    # ----------------------------------------------------

    fig = plt.gcf()
    fig.set_size_inches(10, 5)

    if feature_2 in ["LOCAL_AUTHORITY_LABEL"]:
        fig = plt.gcf()
        fig.set_size_inches(10, 5)

        if country == "England":
            fig.set_size_inches(50, 10)

    # Get relative emissions as bar plot
    # emissions_dict["relative emissions"].plot(kind="bar", color="lightseagreen")

    feat_bar_dict = {}
    feat_bar_dict["CO2_EMISSIONS_CURRENT"] = emissions_dict_emissions[
        "relative emissions"
    ][order]
    feat_bar_dict["CO2_EMISS_CURR_PER_FLOOR_AREA"] = emissions_dict_by_area[
        "relative emissions"
    ][order]
    subcat_by_subcat = pd.DataFrame(feat_bar_dict, index=order)
    subcat_by_subcat.plot(kind="bar", color=["tomato", "orange"], width=0.7)

    # Get highest counter value for adjusting plot format
    highest_count = max(
        [
            cty
            for cty in list(emissions_dict_emissions["relative emissions"].values)
            + list(emissions_dict_by_area["relative emissions"].values)
        ]
    )

    # Display count for every bar on top of bar
    ax = plt.gca()
    ax.legend(["CO2 Emissions", "CO2 Emissions by Floor Area"])

    # fig.set_size_inches(10,5)

    # ax = df.set_index(field).loc[order]

    for i, cty in enumerate(feat_bar_dict["CO2_EMISSIONS_CURRENT"].values):
        ax.text(
            i - 0.2,
            cty + highest_count / 25,
            str(round(cty, 1)) + "%",
            horizontalalignment="center",
        )

    for i, cty in enumerate(feat_bar_dict["CO2_EMISS_CURR_PER_FLOOR_AREA"].values):
        ax.text(
            i + 0.2,
            cty + highest_count / 25,
            str(round(cty, 1)) + "%",
            horizontalalignment="center",
        )

    # Adjust the ylimit of the plot
    ax.set_ylim([0.0, highest_count + highest_count / 2.5])

    #  Set title, ticks and labels
    plt.title("{} (%) {}".format(descr_part_1, descr_part_2))
    plt.xticks(rotation=x_tick_rotation, ha=x_tick_ha)
    plt.xlabel("")

    # Set ylabel (with ompute total emissions)
    plt.ylabel("CO2 Emissions (%)".format(str(round(emissions_dict["total"], 0))[:-3]))
    # # Set ylabel (with ompute total emissions)
    #  plt.ylabel(
    #     "CO2 Emissions (%)\n(total of {}k tonnes/year)".format(
    #         str(round(emissions_dict["total"], 0))[:-3]
    #    )
    #   )

    # Save and show
    plt.tight_layout()
    filename = "{} {} relative".format(descr_part_1, descr_part_2)
    filename = re.sub(" ", "_", filename)

    plt.savefig(FIG_PATH + filename)
    plt.show()

    # Plot absolute emissions
    # ----------------------------------------------------

    if feature_2 in ["LOCAL_AUTHORITY_LABEL"]:
        fig = plt.gcf()
        fig.set_size_inches(10, 5)

        if country == "England":
            fig.set_size_inches(50, 10)

    # Get absolute emissions as bar plot
    # emissions_dict["absolute emissions"].plot(kind="bar", cmap="inferno")

    feat_bar_dict = {}
    feat_bar_dict["CO2_EMISSIONS_CURRENT"] = emissions_dict_emissions[
        "absolute emissions"
    ]
    feat_bar_dict["CO2_EMISS_CURR_PER_FLOOR_AREA"] = emissions_dict_by_area[
        "absolute emissions"
    ]
    subcat_by_subcat = pd.DataFrame(feat_bar_dict, index=order)
    subcat_by_subcat.plot(kind="bar", color=["tomato", "orange"])

    # Get highest counter value for adjusting plot format
    highest_count = max(
        [
            cty
            for cty in emissions_dict_emissions["absolute emissions"].values
            + emissions_dict_by_area["absolute emissions"].values
        ]
    )

    # Set yticklabels
    ylabels, ax, division_int, division_type = easy_plotting.get_readable_tick_labels(
        plt, "m", "y"
    )
    ax.set_yticklabels(ylabels)
    ax.legend(["CO2 Emissions", "CO2 Emissions by Floor Area"])

    # Display count for every bar on top of bar
    ax = plt.gca()

    #  for i, cty in enumerate(emissions_dict["absolute emissions"].values+emissions_dict_by_area["absolute emissions"].values):
    #   ax.text(
    #       i,
    #        cty + highest_count / 25,
    #        str(round(cty / division_int,1)) + division_type,
    #        horizontalalignment="center",
    #    )

    # Adjust the ylimit of the plot
    ax.set_ylim([0.0, highest_count + highest_count / 5])

    # Set title, ticks and labels
    plt.title("{} {}".format(descr_part_1, descr_part_2))
    plt.xticks(rotation=x_tick_rotation, ha=x_tick_ha)
    plt.xlabel("")
    plt.ylabel("CO2 Emissions\n[tonnes/year]")

    # Save and show
    plt.tight_layout()
    filename = "{} {} absolute".format(descr_part_1, descr_part_2)
    filename = re.sub(" ", "_", filename)

    plt.savefig(FIG_PATH + filename)
    plt.show()

    # Plot emissions per dwelling
    # ----------------------------------------------------

    if feature_2 in ["LOCAL_AUTHORITY_LABEL"]:
        fig = plt.gcf()
        fig.set_size_inches(10, 5)

        if country == "England":
            fig.set_size_inches(50, 10)

    # Get number of dwellings/properties
    n_dwellings = df.shape[0]

    # Get emissions by dwelling
    feat_bar_dict = {}
    feat_bar_dict["CO2_EMISSIONS_CURRENT"] = emissions_dict_emissions[
        "emissions by dwelling"
    ]
    feat_bar_dict["CO2_EMISS_CURR_PER_FLOOR_AREA"] = emissions_dict_by_area[
        "emissions by dwelling"
    ]

    subcat_by_subcat = pd.DataFrame(feat_bar_dict, index=order)
    subcat_by_subcat = subcat_by_subcat[
        ["CO2_EMISSIONS_CURRENT", "CO2_EMISS_CURR_PER_FLOOR_AREA"]
    ]

    # Get highest counter value for adjusting plot format
    highest_count = max(
        [cty for cty in list(emissions_dict["emissions by dwelling"].values)]
    )

    # Get highest counter value for adjusting plot format
    highest_count_ax2 = max(
        [cty for cty in list(emissions_dict_by_area["emissions by dwelling"].values)]
    )

    # Display count for every bar on top of bar
    ax = plt.gca()

    ax2 = ax.twinx()

    feat_bar_dict["CO2_EMISSIONS_CURRENT"].plot(
        kind="bar", color="tomato", align="center", width=0.25, ax=ax, position=1
    )
    feat_bar_dict["CO2_EMISS_CURR_PER_FLOOR_AREA"].plot(
        kind="bar", color="orange", width=0.25, ax=ax2, position=0
    )

    plt.xticks(rotation=x_tick_rotation, ha=x_tick_ha)

    for i, cty in enumerate(emissions_dict_emissions["emissions by dwelling"].values):
        ax.text(
            i - 0.2,
            cty + highest_count / 25,
            str(round(cty, 1)) + " t",
            horizontalalignment="center",
        )

    for i, cty in enumerate(emissions_dict_by_area["emissions by dwelling"].values):
        ax2.text(
            i + 0.2,
            cty + highest_count_ax2 / 25,
            str(round(cty)) + " kg",
            horizontalalignment="center",
        )

    # Set ylabels in desired format
    ylabels = ["{:.0f}".format(x) for x in ax.get_yticks()]

    ax.set_yticklabels(ylabels)
    ax2.set_yticklabels(["{:.0f}".format(x) for x in ax2.get_yticks()])

    # Set title, labels and ticks
    plt.title("{} (per dwelling) {}".format(descr_part_1, descr_part_2))

    ax.set_xlabel("")
    ax2.set_xlabel("")
    ax.set_ylabel("CO2 Emissions\n[tonnes/year/dwelling]")
    ax2.set_ylabel(
        "CO2 Emissions\n[kg/m²/year]", rotation=-90, va="bottom", loc="center"
    )

    ax.tick_params(axis="x", rotation=45)
    ax.legend(["GB Properties", "Total Floor Area"])

    # Adjust the ylimit of the plot
    ax.set_ylim([0.0, highest_count + highest_count / 2])
    ax2.set_ylim([0.0, highest_count_ax2 + highest_count_ax2 / 2])
    plt.xlim([-0.5, n_cats - 1.5])

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(
        lines + lines2, ["CO2 Emissions (avg.)", "CO2 Emissions by Floor Area"], loc=0
    )

    # Save and show
    plt.tight_layout()
    filename = "Emissions by {}".format(title_tag)
    filename = re.sub(" ", "_", filename)

    plt.savefig(FIG_PATH + filename)
    plt.show()

    # Plot histogram dwellings and floor area
    # ----------------------------------------------------

    total_floor_area = df["TOTAL_FLOOR_AREA"].sum()
    feat_bar_dict = {}
    category_distr = round(df[feature_2].value_counts(normalize=True) * 100, 2)
    print(
        df.loc[df[feature_2] == feat]["TOTAL_FLOOR_AREA"].sum() / total_floor_area * 100
        for feat in order
    )

    # floor_area_by_cat = pd.DataFrame.from_dict({feat: df.loc[df[feature_2] == feat]['TOTAL_FLOOR_AREA'].sum() / total_floor_area * 100
    #                                    for feat in order})

    floor_area_by_cat = pd.DataFrame(
        [
            df.loc[df[feature_2] == feat]["TOTAL_FLOOR_AREA"].sum()
            / total_floor_area
            * 100
            for feat in order
        ],
        index=order,
    )[0]

    # floor_area_by_cat = floor_area_by_cat.reshape((-1,1))
    print(floor_area_by_cat)
    print(floor_area_by_cat.shape)

    print(category_distr)
    print(category_distr.shape)

    print(category_distr.values)
    print(floor_area_by_cat.values)

    feat_bar_dict = {}
    feat_bar_dict["CAT_DISTR"] = category_distr
    feat_bar_dict["FLOOR AREA"] = floor_area_by_cat
    subcat_by_subcat = pd.DataFrame(feat_bar_dict, index=order)
    subcat_by_subcat.plot(kind="bar", color=["steelblue", "turquoise"])

    # Get highest counter value for adjusting plot format
    highest_count = max(
        [cty for cty in list(category_distr.values) + list(floor_area_by_cat.values)]
    )

    print(highest_count)

    # Set yticklabels
    ylabels, ax, division_int, division_type = easy_plotting.get_readable_tick_labels(
        plt, "m", "y"
    )
    ax.set_yticklabels(ylabels)
    ax.legend(["GB Properties", "Total Floor Area"])

    # Display count for every bar on top of bar
    ax = plt.gca()

    for i, cty in enumerate(category_distr.values):
        ax.text(
            i - 0.2,
            cty + highest_count / 25,
            str(round(cty, 1)) + "%",
            horizontalalignment="center",
        )

    for i, cty in enumerate(floor_area_by_cat.values):
        ax.text(
            i + 0.2,
            cty + highest_count / 25,
            str(round(cty, 1)) + "%",
            horizontalalignment="center",
        )

    ## Get highest counter value for adjusting plot format
    # highest_count = max([cty for cty in list(category_distr.values)])

    ## Get highest counter value for adjusting plot format
    # highest_count_ax2 = max([cty for cty in list(floor_area_by_cat.values)])

    # Display count for every bar on top of bar
    # ax = plt.gca()
    # ax2=ax.twinx()

    # category_distr.plot(kind='bar', color='tomato',align="center", width=0.25, ax=ax, position=1)
    # floor_area_by_cat.plot(kind='bar', color='orange', width=0.25, ax=ax2, position=0)

    # for i, cty in enumerate(category_distr.values):
    #    ax.text(
    #        i-0.15, cty + highest_count / 25, str(round(cty))+'%', horizontalalignment="center"
    # )
    #
    # for i, cty in enumerate(floor_area_by_cat.values):
    #    ax2.text(
    #        i+0.15, cty + highest_count_ax2 / 25  , str(round(cty))+'%', horizontalalignment="center"
    # )

    # Set ylabels in desired format
    ylabels = ["{:.0f}".format(x) for x in ax.get_yticks()]

    ax.set_yticklabels(ylabels)
    # ax2.set_yticklabels(["{:.0f}".format(x) for x in ax2.get_yticks()])

    # Set title, labels and ticks
    plt.title("Property and Floor Area Distribution by {}".format(title_tag))

    ax.set_xlabel("")
    # ax2.set_xlabel('')
    ax.set_ylabel("Distribution")
    # ax2.set_ylabel('Distribution of Floor Area', rotation=-90, va="bottom", loc='center')

    ax.tick_params(axis="x", rotation=45)

    # Adjust the ylimit of the plot
    ax.set_ylim([0.0, highest_count + highest_count / 5])
    # ax2.set_ylim([0.0, highest_count_ax2 + highest_count_ax2 / 2])
    plt.xlim([-0.5, n_cats - 1.5])

    # lines, labels = ax.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    # ax2.legend(lines + lines2, ['GB Properties', 'Floor Area'], loc=0)

    # Save and show
    plt.tight_layout()
    filename = "Distributions by {}".format(title_tag)
    filename = re.sub(" ", "_", filename)

    plt.savefig(FIG_PATH + filename)
    plt.show()


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
def get_readable_tick_labels(plt, ticklabel_type, axis):
    """Get more readable tick labels, e.g. 50k for 50000.

    Parameters
    ----------

    plt : matplotlib.pyplot
        Plot from which to get axes.

    ticklabel_type : {'', 'm', 'k' or '%'}, default=None
        Label type for ticklabel (y-axis or x-axis).

    axis : {'y', 'x'}
        For which axis to update the labels.

    Return
    ---------

    labels : list
        Updated tick labels for x or y axis.

    ax : plt.gca
        Current axes for plt.

    division_int : int
        By which number to divide values to match new tick labels.

    division_type : str
        Same as ticklabel_type, except for None (--> ""),
        representing string to display after updated tick values."""

    # Depending on ticklabel adjust display of numbers
    # e.g. (50000 --> 50k)

    # 1000 --> k
    if ticklabel_type == "k":
        division_type = "k"
        division_int = 1000.0

    # 1000000 --> m
    elif ticklabel_type == "m":
        division_type = "m"
        division_int = 1000000.0

    # "" or None --> ""
    elif ticklabel_type == "" or ticklabel_type is None:
        division_type = ""
        division_int = 1.0

    # % --> %
    elif ticklabel_type == "%":
        division_type = "%"
        division_int = 1.0

    else:
        raise IOError("Invalid value: ticklabel has to be '', 'm', 'k' or '%'")

    # Get axis and ticks
    ax = plt.gca()

    if axis == "y":
        ticks = ax.get_yticks()
    else:
        ticks = ax.get_xticks()

    # Get updated tick labels
    labels = ["{:.0f}".format(x / division_int) + division_type for x in ticks]

    return labels, ax, division_int, division_type


def plot_subcategory_distribution(
    df,
    category,
    normalize=False,
    color="lightseagreen",
    plot_title=None,
    fig_save_path=None,
    y_label="",
    x_label="",
    y_ticklabel_type=None,
    x_tick_rotation=0,
):
    """Plot distribution of subcategories/values of specific category/feature.

    Parameters
    ----------

    df : pd.DataFrame
        Dataframe to analyse and plot.

    category : str
        Category/column of interest for which distribution is plotted.

    normalize : bool, default=False
        If True, relative numbers (percentage) instead of absolute numbers.

    color : str
        Color of bars in plot.

    plot_title : str, None, default=None
        Title to display above plot.
        If None, title is created automatically.
        Plot title is also used when saving file.

    fig_save_path : str, None, default=None
        Location where to save plot.

    y_label : str, default=""
        Label for y-axis.

    x_label : str, default=""
        Label for x-axis.

    y_ticklabel_type : {'', 'm', 'k' or '%'}, default=None
        Label for yticklabel, e.g. 'k' when displaying numbers
        in more compact way for easier readability (50000 --> 50k).

    x_tick_rotation : int, default=0
        Rotation of x-tick labels.
        If rotation set to 45, make end of label align with tick (ha="right").

    Return
    ---------
    None"""

    # Get relative numbers (percentage) instead of absolute numbers
    if normalize:

        # Get counts for every category
        category_counts = round(
            df[category].value_counts(dropna=False, normalize=True) * 100, 2
        )
        y_ticklabel_type = "%"

    else:
        # Get counts for every category
        category_counts = df[category].value_counts(dropna=False)

    # Plot category counts
    category_counts.plot(kind="bar", color=color)

    # Set plot title
    if plot_title is None:
        plot_title = "Distribution of {}".format(category.lower())
        if normalize:
            plot_title += " (%)"

    # Add titles and labels
    plt.title(plot_title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(
        rotation=x_tick_rotation, ha="right"
    ) if x_tick_rotation == 45 else plt.xticks(rotation=x_tick_rotation)

    # Get new yticklabels
    ax = plt.gca()

    yticklabels, ax, division_int, division_type = get_readable_tick_labels(
        plt, y_ticklabel_type, "y"
    )
    ax.set_yticklabels(yticklabels)

    # Adjust ylim in case of ylabel adjustment for easier readiablity (50000 --> 50k)
    highest_count = max(category_counts)

    for i, cty in enumerate(category_counts.values):
        ax.text(
            i,
            cty + highest_count / 80,
            str(round(cty / division_int, 1)) + division_type,
            horizontalalignment="center",
        )

    ax.set_ylim([0.0, int(highest_count + highest_count / 8)])

    # Save figure
    # save_figure(plt, plot_title, fig_path=fig_save_path)

    # Show plot
    plt.show()


# %%
epc_df.shape

# %%
column_widget = my_widgets.get_custom_widget(
    epc_df.columns,
    description="EPC feature",
    default_value="CURRENT_ENERGY_RATING",
    widget_type="dropdown",
)


@interact(category=column_widget)
def plot_distribution(category):
    plot_subcategory_distribution(
        epc_df,
        category,
        normalize=True,
        y_label="Properties",
        x_tick_rotation=45,
        color="royalblue",
    )


# C, D, E make up 83.3% of emissions and include 84.3 of all houses


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
