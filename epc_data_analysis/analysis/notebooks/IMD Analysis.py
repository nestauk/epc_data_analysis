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
# %load_ext autoreload
# %autoreload 2

import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact
import re

from scipy.stats import pearsonr

from epc_data_analysis import PROJECT_DIR
from epc_data_analysis.getters import epc_data, deprivation_data, util_data
from epc_data_analysis.pipeline import epc_analysis
from epc_data_analysis.pipeline.preprocessing import (
    feature_engineering,
    data_cleaning,
    preprocess_epc_data,
)
from epc_data_analysis.visualisation import easy_plotting, feature_settings, my_widgets
from epc_data_analysis.getters import epc_data, deprivation_data, util_data

# %%
# Display dataset widgets
display(my_widgets.UK_part_widget)
display(my_widgets.duplicate_widget)
display(my_widgets.preprocessed_feat_widget)

# %%
# Get parameters from widgets
UK_part = my_widgets.UK_part_widget.value
version = (
    "preprocessed_dedupl"
    if my_widgets.duplicate_widget.value == "Without duplicates"
    else "preprocessed"
)

features_of_interest = my_widgets.preprocessed_feat_widget.value
features_of_interest = [
    "TOTAL_FLOOR_AREA",
    "COUNTRY",
    "POSTCODE",
    "HEATING_FUEL",
    "N_ENTRIES_BUILD_ID",
    "HEATING_SYSTEM",
    "PROPERTY_TYPE",
    "BUILT_FORM",
    "CONSTRUCTION_AGE_BAND",
    "ENTRY_YEAR_INT",
    "TENURE",
    "CURRENT_ENERGY_RATING",
    "CURR_ENERGY_RATING_NUM",
]

epc_df = epc_data.load_preprocessed_epc_data(
    version=version, usecols=features_of_interest, nrows=5000000
)
# epc_df = preprocess_epc_data.load_and_preprocess_epc_data()

if UK_part != "GB":
    epc_df = epc_df.loc[epc_df["COUNTRY"] == UK_part]

# %%
epc_df.shape


# %%
def merge_imd_with_other_set(imd_df, other_df):
    """Merge IMD data with other data based on postcode.

    Parameters
    ----------
    imd_df : pandas.DataFrame
        Deprivation data

    other_df : pandas.DataFrame
        Other data

    Return
    ----------
    merged_df : pandas.DataFrame
        Two datasets merged on postcode."""

    if "POSTCODE" in other_df.columns:
        other_df = other_df.rename(columns={"POSTCODE": "Postcode"})

    imd_df["Postcode"] = imd_df["Postcode"].str.replace(r" ", "")
    other_df["Postcode"] = other_df["Postcode"].str.replace(r" ", "")

    merged_df = pd.merge(imd_df, other_df, on=["Postcode"])  # , how='inner')
    # other_df.merge(imd_df, how='left')

    return merged_df


# %%
print(epc_df.shape)
imd_df = deprivation_data.get_gb_imd_data()
print(imd_df.shape)

# %%
print(imd_df.shape)
imd_df.drop_duplicates(inplace=True)
print(imd_df.shape)

# %%
print(imd_df.shape)
print(epc_df.shape)
epc_imd_df = deprivation_data.merge_imd_with_other_set(imd_df, epc_df)
epc_imd_df = epc_imd_df.rename(columns={"Postcode": "POSTCODE"})
print(epc_imd_df.shape)
epc_imd_df.head()

# %%
import numpy as np

epc_imd_df.loc[epc_imd_df["CURRENT_ENERGY_RATING"] == "A"].head()

# %%
print("GB total:\t", epc_df.shape)
epc_df["TOTAL_FLOOR_AREA"] = epc_df["TOTAL_FLOOR_AREA"].replace("unknown", float("NaN"))

epc_df["TOTAL_FLOOR_AREA"] = pd.to_numeric(epc_df["TOTAL_FLOOR_AREA"])


def map_floor_area_to_cat(floor_area):

    if floor_area < 20:
        return "<20"
    elif floor_area >= 20.0 and floor_area < 30.0:
        return "<30"
    elif floor_area >= 30.0 and floor_area < 40.0:
        return "<40"
    elif floor_area >= 40.0 and floor_area < 50.0:
        return "<50"
    elif floor_area >= 50.0 and floor_area < 60.0:
        return "<60"

    elif floor_area >= 60.0 and floor_area < 70.0:
        return "<70"
    elif floor_area >= 70.0 and floor_area < 80.0:
        return "<80"
    elif floor_area >= 80.0 and floor_area < 90.0:
        return "<90"
    elif floor_area >= 90.0 and floor_area < 100.0:
        return "<100"

    elif floor_area >= 100.0 and floor_area < 110.0:
        return "<110"
    elif floor_area >= 110.0 and floor_area < 120.0:
        return "<120"
    elif floor_area >= 120.0 and floor_area < 130.0:
        return "<130"
    elif floor_area >= 130.0 and floor_area < 140.0:
        return "<140"
    elif floor_area >= 140.0 and floor_area < 150.0:
        return "<150"
    elif floor_area >= 150.0 and floor_area < 200.0:
        return "<200"
    elif floor_area >= 200:
        return "200+"


epc_df["FLOOR_AREA_CAT"] = epc_df["TOTAL_FLOOR_AREA"].apply(map_floor_area_to_cat)


# %%
epc_df.head()

# %%
epc_df.columns

# %%

england = epc_df.loc[epc_df["COUNTRY"] == "England"]
print("England:\t", england.shape)

wales = epc_df.loc[epc_df["COUNTRY"] == "Wales"]
print("Wales:\t", wales.shape)

scotland = epc_df.loc[epc_df["COUNTRY"] == "Scotland"]
print("Scotland:\t", scotland.shape)


df_dict = {"England": england, "Wales": wales, "Scotland": scotland, "GB": epc_df}

# %%
scotland["TOTAL_FLOOR_AREA"].value_counts()

# %%
import matplotlib.pyplot as plt

scotland_red = scotland[scotland.TOTAL_FLOOR_AREA < 300]

scotland_red["TOTAL_FLOOR_AREA"].plot(
    kind="hist", title="Scotland Floor Area Distribution", bins=100, grid=True
)
plt.savefig("Scotland Floor Area Distribution.png", dpi=2000)

# %%
wales_red = wales[wales.TOTAL_FLOOR_AREA < 300]

wales_red["TOTAL_FLOOR_AREA"].plot(
    kind="hist", title="Wales Floor Area Distribution", bins=100, grid=True
)
plt.savefig("Wales Floor Area Distribution.png", dpi=2000)

# %%
england_red = england[england.TOTAL_FLOOR_AREA < 300]

england_red["TOTAL_FLOOR_AREA"].plot(
    kind="hist", title="England Floor Area Distribution", bins=100, grid=True
)
plt.savefig("England Floor Area Distribution.png", dpi=2000)

# %%
scotland["CURR_ENERGY_RATING_NUM"].mean()

# %%
wales["CURR_ENERGY_RATING_NUM"].mean()

# %%
england["CURR_ENERGY_RATING_NUM"].mean()

# %%

wales["CURR_ENERGY_RATING_NUM"].mean()

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 10]
last_decile.head()

# %%
epc_df["FLOOR_AREA_CAT"].value_counts()

# %%
# Plot Energy Rating Distribution by Sector
easy_plotting.plot_subcats_by_other_subcats(
    england,
    "IMD Decile",
    "FLOOR_AREA_CAT",
    feature_2_order=[
        "<20",
        "<30",
        "<40",
        "<50",
        "<60",
        "<70",
        "<80",
        "<90",
        "<100",
        "<110",
        "<120",
        "<130",
        "<140",
        "<150",
        "<200",
        "200+",
    ],
    feature_1_order=feature_settings.rating_order,
    y_label="# dwellings",
    plotting_colors="viridis",
    x_tick_rotation=45,
    legend_loc="outside",
    plot_title="IMD Decile by EPC Rating",
)

# %%
# Plot Energy Rating Distribution by Sector
easy_plotting.plot_subcats_by_other_subcats(
    scotland,
    "IMD Decile",
    "CURRENT_ENERGY_RATING",
    # feature_1_order=["<20", "<30", "<40", "<50", "<60","<70","<80","<90","<100","<110","<120","<130",
    #  "<140", "<150","<200","200+"],
    feature_2_order=["A", "B", "C", "D", "E", "F", "G"],
    y_label="# dwellings",
    plotting_colors="RdYlGn_r",
    x_tick_rotation=45,
    legend_loc="outside",
    plot_title="Scotland: EPC Rating by IMD Decile",
)

# %%
# Plot Energy Rating Distribution by Sector
easy_plotting.plot_subcats_by_other_subcats(
    last_decile,
    "FLOOR_AREA_CAT",
    "CURRENT_ENERGY_RATING",
    # feature_1_order=["<20", "<30", "<40", "<50", "<60","<70","<80","<90","<100","<110","<120","<130",
    #  "<140", "<150","<200","200+"],
    feature_1_order=[
        "<20",
        "<30",
        "<40",
        "<50",
        "<60",
        "<70",
        "<80",
        "<90",
        "<100",
        "<110",
        "<120",
        "<130",
        "<140",
        "<150",
        "<200",
        "200+",
    ],
    feature_2_order=["A", "B", "C", "D", "E", "F", "G"],
    y_label="# dwellings",
    plotting_colors="RdYlGn_r",
    x_tick_rotation=45,
    legend_loc="outside",
    plot_title="Floor Area by IMD Decile",
)

# %%
epc_df["Income Score"].unique()

# %%
epc_df["TOTAL_FLOOR_AREA"] = epc_df["TOTAL_FLOOR_AREA"].dropna()
epc_df["Income Score"] = epc_df["Income Score"].dropna()

# %%
corr, _ = pearsonr(epc_df["IMD Decile"], epc_df["TOTAL_FLOOR_AREA"])

# %%
# 80, 90, 70

# %%
easy_plotting.plot_subcategory_distribution(
    england,
    "FLOOR_AREA_CAT",
    normalize=True,
    y_ticklabel_type="%",
    y_label="Properties",
    plot_title="Property Distribution by Country (%)",
    x_tick_rotation=45,
)

# %%
easy_plotting.plot_subcategory_distribution(
    scotland,
    "FLOOR_AREA_CAT",
    normalize=True,
    y_ticklabel_type="%",
    y_label="Properties",
    plot_title="Property Distribution by Country (%)",
    x_tick_rotation=45,
)

# %%
easy_plotting.plot_subcategory_distribution(
    wales,
    "IMD Decile",
    normalize=True,
    y_ticklabel_type="%",
    y_label="Properties",
    plot_title="Wales IMD Decile Distribution",
    color="royalblue",
    x_tick_rotation=45,
)

# %%
england.loc[england["TOTAL_FLOOR_AREA"] < 50].shape[0] / england.shape[0]

# %%
wales.loc[wales["TOTAL_FLOOR_AREA"] < 50].shape[0] / wales.shape[0]

# %%
scotland.loc[scotland["TOTAL_FLOOR_AREA"] < 50].shape[0] / scotland.shape[0]

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 10]
last_decile["TOTAL_FLOOR_AREA"].mean()

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 9]
last_decile["TOTAL_FLOOR_AREA"].mean()

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 8]
last_decile["TOTAL_FLOOR_AREA"].mean()

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 7]
last_decile["TOTAL_FLOOR_AREA"].mean()

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 6]
last_decile["TOTAL_FLOOR_AREA"].mean()

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 5]
last_decile["TOTAL_FLOOR_AREA"].mean()

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 4]
last_decile["TOTAL_FLOOR_AREA"].mean()

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 3]
last_decile["TOTAL_FLOOR_AREA"].mean()

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 2]
last_decile["TOTAL_FLOOR_AREA"].mean()

# %%
last_decile = epc_df.loc[epc_df["IMD Decile"] == 1]
last_decile["TOTAL_FLOOR_AREA"].mean()

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


df_dict = {"England": england, "Wales": wales, "Scotland": scotland, "GB": epc_df}


@interact(feature=settings_dict.keys(), country=df_dict.keys())
def plot_efficiency(feature, country):

    df = df_dict[country]

    easy_plotting.plot_subcats_by_other_subcats(
        df,
        "IMD Decile",
        feature,
        y_ticklabel_type="%",
        normalize=True,
        # feature_1_order = ['England', 'Wales'],
        feature_2_order=settings_dict[feature][0],
        legend_loc="outside",
        plotting_colors="viridis",
        plot_title="{}: {} by IMD Decile".format(country, settings_dict[feature][1]),
    )


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


df_dict = {"England": england, "Wales": wales, "Scotland": scotland, "GB": epc_df}


@interact(feature=settings_dict.keys(), country=df_dict.keys())
def plot_efficiency(feature, country):

    df = df_dict[country]

    easy_plotting.plot_subcats_by_other_subcats(
        df,
        "IMD Decile",
        feature,
        y_ticklabel_type="%",
        normalize=True,
        # feature_1_order = ['England', 'Wales'],
        feature_2_order=settings_dict[feature][0],
        legend_loc="outside",
        plotting_colors="viridis",
        plot_title="{}: {} by IMD Decile".format(country, settings_dict[feature][1]),
    )


# %%
scotland.loc[scotland["TENURE"] == "owner-occupied"].head()

# %%
scotland.shape

# %%
scotland.loc[scotland["TENURE"] == "owner-occupied"]["CURR_ENERGY_RATING_NUM"].mean()

# %%
scotland.loc[scotland["TENURE"] == "rental (social)"]["CURR_ENERGY_RATING_NUM"].mean()

# %%
scotland.loc[scotland["TENURE"] == "rental (private)"]["CURR_ENERGY_RATING_NUM"].mean()

# %%
scotland["CURR_ENERGY_RATING_NUM"].mean()

# %%
england.loc[england["TENURE"] == "rental (private)"]["CURR_ENERGY_RATING_NUM"].mean()

# %%
england.loc[england["TENURE"] == "rental (social)"]["CURR_ENERGY_RATING_NUM"].mean()

# %%
england.loc[england["TENURE"] == "owner-occupied"]["CURR_ENERGY_RATING_NUM"].mean()

# %%
easy_plotting.plot_subcategory_distribution(
    scotland.loc[scotland["TENURE"] == "rental (private)"],
    "CURRENT_ENERGY_RATING",
    normalize=True,
    plot_title="Scotland Distribution of EPC Ratings for Private Rental Sector",
    color="royalblue",
)

# %%
easy_plotting.plot_subcategory_distribution(
    scotland.loc[scotland["TENURE"] == "rental (social)"],
    "CURRENT_ENERGY_RATING",
    normalize=True,
    plot_title="Scotland Distribution of EPC Ratings for Social Rental Sector",
    color="royalblue",
)


# %%
easy_plotting.plot_subcategory_distribution(
    scotland.loc[scotland["TENURE"] == "owner-occupied"],
    "CURRENT_ENERGY_RATING",
    normalize=True,
    plot_title="Scotland Distribution of EPC Ratings for Owner-Occupied Sector",
    color="royalblue",
)

# %%
easy_plotting.plot_subcategory_distribution(
    scotland,
    "CURRENT_ENERGY_RATING",
    normalize=True,
    plot_title="Scotland Distribution of EPC Ratings for All Sectors",
    color="royalblue",
)

# %%

# %%

# %%

# %%

# %%
