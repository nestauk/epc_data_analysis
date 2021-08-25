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

# %% [markdown]
# ```
# Wales
# (1034720, 32) 1.0m
#
# England
# (18870569, 32) 18m
#
# Scotland
# (1356219, 32) 1.3m
#
# all
# (21271480, 32) 21m
# ```

# %%
# Get parameters from widgets
UK_part = my_widgets.UK_part_widget.value
features_of_interest = list(my_widgets.feature_widget.value)

features_of_interes_2 = [
    "INSPECTION_DATE",
    "CONSTRUCTION_AGE_BAND",
    "MAINHEAT_DESCRIPTION",
    "SHEATING_ENERGY_EFF",
    "ENERGY_CONSUMPTION_CURRENT",
    "ENERGY_TARIFF",
    "FLOOR_LEVEL",
    "HEATING_COST_CURRENT",
    "HEATING_COST_POTENTIAL",
    "HOT_WATER_COST_CURRENT",
    "HOT_WATER_COST_POTENTIAL",
    "HOTWATER_DESCRIPTION",
    "MAIN_FUEL",
    "MAINS_GAS_FLAG",
    "NUMBER_HABITABLE_ROOMS",
    "POTENTIAL_ENERGY_EFFICIENCY",
    "SECONDHEAT_DESCRIPTION",
    "SOLAR_WATER_HEATING_FLAG",
    "TOTAL_FLOOR_AREA",
    "WIND_TURBINE_COUNT",
    "BUILDING_REFERENCE_NUMBER",
]


print("UK part:", UK_part)
# Load Wales EPC data
epc_df = epc_data.load_epc_data(
    subset=UK_part, usecols=features_of_interest, low_memory=False
)
epc_df.head()

# %% [markdown]
# ### Year References

# %%
epc_df = data_cleaning.clean_epc_data(epc_df)
epc_df = feature_engineering.get_date_features(epc_df)

all_entry_df = epc_df.copy()

print(epc_df.shape)
epc_df = feature_engineering.filter_by_year(epc_df, None, selection="latest entry")
print(epc_df.shape)

# %%
n_entries_analysis = False

if n_entries_analysis:

    df_2019 = feature_engineering.filter_by_year(all_entry_df, 2019, up_to=True)
    df_2019_first = feature_engineering.filter_by_year(
        all_entry_df, 2019, up_to=True, selection="first entry"
    )
    df_2019_last = feature_engineering.filter_by_year(
        all_entry_df, 2019, up_to=True, selection="latest entry"
    )

    print(df_2019.shape)
    print(df_2019_first.shape)
    print(df_2019_last.shape)

    TEST_NUMBER = 9686127278
    df_2019_last.loc[df_2019_last.BUILDING_REFERENCE_NUMBER == TEST_NUMBER]
    df_2019_first.loc[df_2019_first.BUILDING_REFERENCE_NUMBER == TEST_NUMBER]

# %% [markdown]
# ### Country specific

# %%
country_order = ["England", "Wales", "Scotland"]
efficiency_order = ["unknown", "Very Poor", "Poor", "Average", "Good", "Very Good"]
tenure_order = ["owner-occupied", "rental (social)", "rental (private)", "unknown"]
prop_type_order = ["House", "Bungalow", "Park home", "Maisonette", "Flat"]
year_order = [
    2008,
    2009,
    2010,
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019,
    2020,
]
rating_order = ["G", "F", "E", "D", "C", "B", "A"]
built_form_order = [
    "End-Terrace",
    "Enclosed End-Terrace",
    "Mid-Terrace",
    "Enclosed Mid-Terrace",
    "Detached",
    "Semi-Detached",
]
constr_year_order = [
    "England and Wales: before 1900",
    "England and Wales: 1900-1929",
    "England and Wales: 1930-1949",
    "England and Wales: 1950-1966",
    "England and Wales: 1967-1975",
    "England and Wales: 1976-1982",
    "England and Wales: 1983-1990",
    "England and Wales: 1991-1995",
    "England and Wales: 1996-2002",
    "England and Wales: 2003-2006",
    "England and Wales: 2007 onwards",
    "Scotland: before 1919",
    "Scotland: 1919-1929",
    "Scotland: 1930-1949",
    "Scotland: 1950-1964",
    "Scotland: 1965-1975",
    "Scotland: 1976-1983",
    "Scotland: 1984-1991",
    "Scotland: 1992-1998",
    "Scotland: 1999-2002",
    "Scotland: 2003-2007",
    "Scotland: 2008 onwards",
    "unknown",
]

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

heating_source_order = ["oil", "LPG", "gas", "electric"]

column_widgets = my_widgets.get_custom_widget(
    epc_df.columns,
    description="EPC Feature",
    default_value="CURRENT_ENERGY_RATING",
    widget_type="dropdown",
)


# %%
# Get new heating features
epc_df = feature_engineering.get_heating_features(epc_df)

# %%
epc_df["WINDOWS_ENERGY_EFF"] = epc_df["WINDOWS_ENERGY_EFF"].apply(
    data_cleaning.standardise_efficiency
)
epc_df["FLOOR_ENERGY_EFF"] = epc_df["FLOOR_ENERGY_EFF"].apply(
    data_cleaning.standardise_efficiency
)
epc_df["HOT_WATER_ENERGY_EFF"] = epc_df["HOT_WATER_ENERGY_EFF"].apply(
    data_cleaning.standardise_efficiency
)
epc_df["LIGHTING_ENERGY_EFF"] = epc_df["LIGHTING_ENERGY_EFF"].apply(
    data_cleaning.standardise_efficiency
)

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
    y_ticklabel_type="m",
    y_label="Properties",
    plot_title="Property Distribution by Country",
)


# %%
@interact(feature_1=column_widgets, country=country_order)
def plot_by_country(feature_1, country):

    easy_plotting.plot_feature_by_subcategories(
        epc_df,
        feature_1,
        "COUNTRY",
        country,
        plot_kind="bar",
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
    )


# %% [markdown]
# ### Country Vs.

# %%
settings_dict = {
    "CURRENT_ENERGY_RATING": (rating_order, "Current Energy Rating", "RdYlGn"),
    "PROPERTY_TYPE": (prop_type_order, "Property Type", "viridis"),
    "TENURE": (tenure_order, "Sector", "viridis"),
    "HEATING_SOURCE": (heating_source_order, "Heating Source", "viridis"),
    "HEATING_SYSTEM": (None, "Heating System", "viridis"),
}


@interact(feature=settings_dict.keys())
def plot_distr_by_country(feature):

    order = settings_dict[feature][0]
    title = settings_dict[feature][1]
    color_map = settings_dict[feature][2]

    easy_plotting.plot_subcats_by_other_subcats(
        epc_df,
        "COUNTRY",
        feature,
        feature_1_order=country_order,
        feature_2_order=order,
        y_ticklabel_type="%",
        normalize=True,
        plotting_colors=color_map,
        plot_title="{} by Country (%)".format(title),
    )


# %%
settings_dict = {
    "YEAR": (year_order, "Year of Latest Entry", "viridis"),
    "BUILT_FORM": (built_form_order, "Built Form", "viridis"),
    "CONSTRUCTION_AGE_BAND": (
        const_year_order_merged,
        "Construction Year Band",
        "viridis",
    ),
}


@interact(feature=settings_dict.keys())
def plot_distr_by_country(feature):

    order = settings_dict[feature][0]
    title = settings_dict[feature][1]
    color_map = settings_dict[feature][2]

    easy_plotting.plot_subcats_by_other_subcats(
        epc_df,
        "COUNTRY",
        feature,
        feature_2_order=order,
        y_ticklabel_type="%",
        normalize=True,
        legend_loc="outside",
        figsize=(10, 5),
        plotting_colors=color_map,
        plot_title="{} by Country (%)".format(title),
    )


# %%
settings_dict = {
    "BUILT_FORM": (built_form_order, "Built Form", "viridis"),
    "CONSTRUCTION_AGE_BAND": (
        const_year_order_merged,
        "Construction Year Band",
        "viridis",
    ),
    "PROPERTY_TYPE": (prop_type_order, "Property Type", "viridis"),
    "TENURE": (tenure_order, "Sector", "viridis"),
    "HEATING_SOURCE": (heating_source_order, "Heating Source", "viridis"),
    "HEATING_SYSTEM": (None, "Heating System", "viridis"),
    "YEAR": (year_order, "Year of Latest Entry", "viridis"),
}


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
        feature_2_order=rating_order,
        y_ticklabel_type="%",
        x_tick_rotation=45,
        normalize=True,
        plotting_colors="RdYlGn",
        plot_title="Energy Rating by {} (%)".format(title),
    )


# %%

settings_dict = {
    "YEAR": (year_order, "Year of Latest Entry", "viridis"),
    "BUILT_FORM": (built_form_order, "Built Form", "viridis"),
    "PROPERTY_TYPE": (prop_type_order, "Property Type", "viridis"),
    "N_ENTRIES": ([1, 2, 3, 4, 5], "Number of Entries", "viridis"),
    "CONSTRUCTION_AGE_BAND": (
        const_year_order_merged,
        "Construction Year Band",
        "viridis",
    ),
    "TENURE": (tenure_order, "Sector", "viridis"),
}

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
        normalize=True,
        plotting_colors="viridis",
        y_ticklabel_type="%",
        x_tick_rotation=45,
        plot_title="{} by {} (%)".format(title_2, title_1),
    )


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
        feature_1_order=country_order,
        # feature_2_order = efficiency_order,
        feature_2_order=efficiency_order[1:]
        if feature in ["HOT_WATER_ENERGY_EFF"]
        else efficiency_order,
        plotting_colors="RdYlGn",
        plot_title="{} by Country".format(title_dict[feature]),
    )


# %%
title_dict = {
    "MAINHEAT_ENERGY_EFF": "Main Heat Energy Efficiency",
    "ROOF_ENERGY_EFF": "Roof Energy Efficiency",
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
        feature_2_order=efficiency_order[1:],
        plotting_colors="RdYlGn",
        plot_title="{} by Country".format(title_dict[feature]),
    )


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
scotland = epc_df.loc[epc_df["COUNTRY"] == "Scotland"]
print(scotland.shape)

wales = epc_df.loc[epc_df["COUNTRY"] == "Wales"]
print(wales.shape)

england = epc_df.loc[epc_df["COUNTRY"] == "England"]
print(england.shape)

df_dict = {"England": england, "Wales": wales, "Scotland": scotland, "all": epc_df}


# %%
@interact(
    feature_1=["CO2_EMISSIONS_CURRENT", "CO2_EMISS_CURR_PER_FLOOR_AREA"],
    feature_2=["TENURE", "WIMD Decile"],
    country=["Scotland", "Wales", "England", "GB"],
)
def plot_CO2_emissions(feature_1, feature_2, country):

    # Get emission data and settings
    # ----------------------------------------------------

    df = df_dict[country]

    emissions_dict = epc_analysis.get_emissions_info(df, feature_1, feature_2)

    descr_part_1 = (
        "CO2 Emissions ({})".format(country)
        if feature_1 == "CO2_EMISSIONS_CURRENT"
        else "CO2 Emissions per Floor Area ({})".format(country)
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
    plt.title("{} {} (abs)".format(descr_part_1, descr_part_2))
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
    n_dwellings = df.shape[0]

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
# ### Heat Pump Analysis

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
epc_df["HAS_HP"] = epc_df["HEATING_SYSTEM"] == "heat pump"

heat_pump_df = epc_df.loc[epc_df["HEATING_SYSTEM"] == "heat pump"]
non_heat_pump_df = epc_df.loc[epc_df["HEATING_SYSTEM"] != "heat pump"]


print("Heat Pump Percentage: {}%".format(heat_pump_df.shape[0] / epc_df.shape[0] * 100))

heat_pump_df["COUNTRY"].value_counts() / epc_df["COUNTRY"].value_counts() * 100


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
        epc_df, category, normalize=True, y_label="Properties", x_tick_rotation=45
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

# %%
