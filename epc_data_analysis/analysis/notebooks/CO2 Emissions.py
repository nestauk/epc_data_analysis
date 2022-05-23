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
#     display_name: 'Python 3.8.8 64-bit (''EPC_data_analysis'': conda)'
#     language: python
#     name: python388jvsc74a57bd01a4c7ba010db823d16e88c91be90e4c3d0f1a2001e059c3c5486bc88e685f2ad
# ---

# %%
import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact
import re

from scipy import stats
import numpy as np

from epc_data_analysis import PROJECT_DIR
from epc_data_analysis.getters import epc_data, deprivation_data, util_data
from epc_data_analysis.pipeline import epc_analysis
from epc_data_analysis.pipeline.preprocessing import (
    feature_engineering,
    data_cleaning,
    preprocess_epc_data,
)
from epc_data_analysis.visualisation import easy_plotting, feature_settings, my_widgets

# %%
# Get parameters from widgets
UK_part = "GB"
version = "preprocessed_dedupl"
features_of_interest = [
    "PROPERTY_TYPE",
    "BUILT_FORM",
    "NUMBER_HABITABLE_ROOMS",
    "CONSTRUCTION_AGE_BAND",
    "CONSTRUCTION_AGE_BAND_ORIGINAL",
    "CO2_EMISSIONS_CURRENT",
    "CURRENT_ENERGY_RATING",
    "HEATING_FUEL",
]

epc_df = epc_data.load_preprocessed_epc_data(
    version=version, usecols=features_of_interest
)

print(epc_df.shape)

# %%
epc_df["CONSTRUCTION_AGE_BAND_ORIGINAL"].value_counts()

# %%
epc_df["CONSTRUCTION_AGE_BAND"].value_counts()

# %%
epc_df = epc_df[epc_df["HEATING_FUEL"] == "gas"]
print(epc_df.shape)

# %%
corrected_df = epc_df[epc_df["CO2_EMISSIONS_CURRENT"] > 0.0]
print(corrected_df.shape)

# %%
corrected_df = corrected_df[
    (np.abs(stats.zscore(corrected_df["CO2_EMISSIONS_CURRENT"])) < 3)
]
print(corrected_df.shape)


# %%
emiss_df = corrected_df

# %%
# emiss_df['CONSTRUCTION_AGE_BAND'].value_counts()
# England and Wales: before 1900    1070292
# England and Wales: before 1900    1070292

# %%
total = emiss_df.shape[0]

age_pre_1900 = emiss_df["CONSTRUCTION_AGE_BAND"] == "England and Wales: before 1900"
age_1900_1949 = (emiss_df["CONSTRUCTION_AGE_BAND"] == "1900-1929") | (
    emiss_df["CONSTRUCTION_AGE_BAND"] == "1930-1949"
)
age_1950_1975 = (emiss_df["CONSTRUCTION_AGE_BAND"] == "1950-1966") | (
    emiss_df["CONSTRUCTION_AGE_BAND"] == "1965-1975"
)
age_1976_1991 = (emiss_df["CONSTRUCTION_AGE_BAND"] == "1976-1983") | (
    emiss_df["CONSTRUCTION_AGE_BAND"] == "1983-1991"
)
age_post_1991 = (
    (emiss_df["CONSTRUCTION_AGE_BAND"] == "1991-2002")
    | (emiss_df["CONSTRUCTION_AGE_BAND"] == "2003-2007")
    | (emiss_df["CONSTRUCTION_AGE_BAND"] == "2007 onwards")
)

rooms_1_2 = (emiss_df["NUMBER_HABITABLE_ROOMS"] == "1.0") | (
    emiss_df["NUMBER_HABITABLE_ROOMS"] == "2.0"
)
rooms_3_4 = (emiss_df["NUMBER_HABITABLE_ROOMS"] == "3.0") | (
    emiss_df["NUMBER_HABITABLE_ROOMS"] == "4.0"
)
rooms_5_6 = (emiss_df["NUMBER_HABITABLE_ROOMS"] == "5.0") | (
    emiss_df["NUMBER_HABITABLE_ROOMS"] == "6.0"
)
rooms_7_9 = (
    (emiss_df["NUMBER_HABITABLE_ROOMS"] == "7.0")
    | (emiss_df["NUMBER_HABITABLE_ROOMS"] == "8.0")
    | (emiss_df["NUMBER_HABITABLE_ROOMS"] == "9.0")
)
rooms_10_plus = emiss_df["NUMBER_HABITABLE_ROOMS"] == "10+"

detached = emiss_df["BUILT_FORM"] == "Detached"
semi_detached = emiss_df["BUILT_FORM"] == "Semi-Detached"
terrace = (
    (emiss_df["BUILT_FORM"] == "Enclosed End-Terrace")
    | (emiss_df["BUILT_FORM"] == "Enclosed Mid-Terrace")
    | (emiss_df["BUILT_FORM"] == "End-Terrace")
    | (emiss_df["BUILT_FORM"] == "Mid-Terrace")
)
flats = emiss_df["PROPERTY_TYPE"] == "Flat"
bungalows = emiss_df["PROPERTY_TYPE"] == "Bungalow"


name_dict = {
    "Pre 1900": age_pre_1900,
    "1900-1950": age_1900_1949,
    "1950-1975": age_1950_1975,
    "1976-1990": age_1976_1991,
    "Post 1900": age_post_1991,
    "1-2 rooms": rooms_1_2,
    "3-4 rooms": rooms_3_4,
    "5-6 rooms": rooms_5_6,
    "7-9 rooms": rooms_7_9,
    "10+ rooms": rooms_10_plus,
    "Detached": detached,
    "Semi-Detached": semi_detached,
    "Terrace": terrace,
    "Flat": flats,
    "Bungalow": bungalows,
}

ages = ["Pre 1900", "1900-1950", "1950-1975", "1976-1990", "Post 1900"]
home_types = ["Detached", "Semi-Detached", "Terrace", "Flat", "Bungalow"]
rooms = ["1-2 rooms", "3-4 rooms", "5-6 rooms", "7-9 rooms", "10+ rooms"]

# %%
emiss_df.loc[flats].head()

# %%
emiss_df.loc[flats].shape

# %%
rooms_1_2.shape

# %%
emiss_df.loc[age_post_1991].shape

# %%
intersection = emiss_df.loc[flats & age_post_1991].shape

# %%
with open("emissions_by_property_characteristics.csv", "w") as outfile:
    outfile.write(
        "Index,Home type,Age,Number of rooms,CO2 Emissions [tonnes/year] (mean),CO2 Emissions [tonnes/year] (median),Number of properties,Percentage of total\n"
    )


# %%
with open("emissions_by_property_characteristics.csv", "a") as outfile:

    counter = 0
    for home_type in home_types:
        for age in ages:
            for room in rooms:

                age_conds = name_dict[age]
                room_conds = name_dict[room]
                home_type_conds = name_dict[home_type]

                intersection = emiss_df.loc[age_conds & room_conds & home_type_conds]

                n_samples = intersection.shape[0]
                percentage = round(n_samples / total * 100, 2)

                mean_emissions = round(intersection["CO2_EMISSIONS_CURRENT"].mean(), 2)
                median_emissions = round(
                    intersection["CO2_EMISSIONS_CURRENT"].median(), 2
                )

                outputs = [
                    str(counter),
                    home_type,
                    age,
                    room,
                    str(mean_emissions),
                    str(median_emissions),
                    str(n_samples),
                    str(percentage),
                ]

                outfile.write(",".join(outputs) + "\n")
                output_collection = []

                counter += 1

# %%
emiss_col_df = pd.read_csv("emissions_by_property_characteristics.csv")

# %%
emiss_col_df.head()

# %%
ages = ["Pre 1900", "1900-1950", "1950-1975", "1976-1990", "Post 1900"]
home_types = ["Detached", "Semi-Detached", "Terrace", "Flat", "Bungalow"]
rooms = ["1-2 rooms", "3-4 rooms", "5-6 rooms", "7-9 rooms", "10+ rooms"]

# %%

for room in rooms:
    print(room + ":\t", emiss_df.loc[name_dict[room]].shape[0])


# %%
for age in ages:
    print(age + ":\t", emiss_df.loc[name_dict[age]].shape[0])

# %%
for home in home_types:
    print(home + ":\t", emiss_df.loc[name_dict[home]].shape[0])

# %%
emiss_col_df.loc[(emiss_col_df["Age"] == "1950-1975")].mean()

# %%
emiss_col_df.loc[(emiss_col_df["Number of rooms"] == "7-9 rooms")].mean()

# %%
emiss_col_df.loc[(emiss_col_df["Number of rooms"] == "10+ rooms")].mean()

# %%

# %%
