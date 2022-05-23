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
epc_df = pd.read_csv(str(PROJECT_DIR) + "/outputs/data_and_predictions_x.csv")

# %%
epc_df.columns

# %%
epc_df["growth error"] = round(abs(epc_df["GROWTH"] - epc_df["growth prediction"]), 2)

epc_df["coverage error"] = round(
    abs(epc_df["HP_COVERAGE_FUTURE"] - epc_df["coverage prediction"]), 2
)

# %%
epc_df["coverage prediction"] = round(epc_df["coverage prediction"], 2)
epc_df["growth prediction"] = round(epc_df["growth prediction"], 2)

# %%
epc_df["HP_COVERAGE_FUTURE"] = round(epc_df["HP_COVERAGE_FUTURE"], 2)
epc_df["HP_COVERAGE_CURRENT"] = round(epc_df["HP_COVERAGE_CURRENT"], 2)

# %%
epc_df["coverage ground truth"] = epc_df["HP_COVERAGE_FUTURE"]
epc_df["growth ground truth"] = round(epc_df["GROWTH"], 2)
epc_df["coverage at time t"] = epc_df["HP_COVERAGE_CURRENT"]

# %%
epc_df = epc_df.rename(
    columns={"POSTCODE_UNIT": "POSTCODE", "POSTCODE_UNIT_TOTAL": "POSTCODE TOTAL"}
)
epc_df = feature_engineering.get_coordinates(epc_df)

# %%
epc_df["zero"] = epc_df["HP_COVERAGE_FUTURE"] == 0.0

# %%
epc_df.head()

# %%
config = kepler_config.get_config("coverage")

temp_model_map_coverage = KeplerGl(height=500)  # , config=config)

temp_model_map_coverage.add_data(
    data=epc_df[
        [
            "LONGITUDE",
            "LATITUDE",
            "coverage prediction",
            "coverage error",
            "coverage at time t",
            "coverage ground truth",  # "HP_COVERAGE_CURRENT",
            "POSTCODE TOTAL",
            "# Properties",
            "train_set",
            "zero",
            "POSTCODE",
        ]
    ],
    name="coverage",
)

temp_model_map_coverage

# %%
# config = kepler_config.get_config("growth")

kepler_config.save_config(temp_model_map_coverage, "coverage")

temp_model_map_coverage.save_to_html(file_name=MAPS_OUTPUT_PATH + "Coverage.html")

# %%
epc_df.head()

# %%
config = kepler_config.get_config("growth")

temp_model_map_growth = KeplerGl(height=500, config=config)

temp_model_map_growth.add_data(
    data=epc_df[
        [
            "LONGITUDE",
            "LATITUDE",
            "growth prediction",
            "growth error",
            "growth ground truth",  # "HP_COVERAGE_CURRENT",
            "POSTCODE_UNIT_TOTAL",
            "train_set",
            "zero",
            "POSTCODE",
        ]
    ],
    name="growth",
)

temp_model_map_growth

# %%
# config = kepler_config.get_config("growth")

kepler_config.save_config(temp_model_map_growth, "growth")

temp_model_map_growth.save_to_html(file_name=MAPS_OUTPUT_PATH + "Growth.html")

# %%
test = epc_df.loc[epc_df["train_set"] == False]
train = epc_df.loc[epc_df["train_set"] == True]
test.shape

# %%
test = test.loc[test["zero"] == False]
epc_df = epc_df.loc[epc_df["zero"] == False]

# %%

# %%
epc_df["zero"].value_counts()

# %%
epc_df["growth ground truth"].mean() * 100

# %%
round(test["growth ground truth"].mean() * 100, 0)

# %%
test["growth prediction"].mean() * 100

# %%
test["growth error"].mean() * 100

# %%
print(test["coverage ground truth"].mean() * 100)
print(test["coverage prediction"].mean() * 100)
print(test["coverage error"].mean() * 100)

# %%
print(test["growth ground truth"].mean() * 100)
print(test["growth prediction"].mean() * 100)
print(test["growth error"].mean() * 100)

# %%
test["coverage ground truth int"] = round(test["coverage ground truth"] * 100, 0)
test["coverage prediction int"] = round(test["coverage prediction"] * 100, 0)
test["coverage error int"] = round(test["coverage error"] * 100, 0)

# %%
test["growth ground truth int"] = round(test["growth ground truth"] * 100, 0)
test["growth prediction int"] = round(test["growth prediction"] * 100, 0)
test["growth error int"] = round(test["growth error"] * 100, 0)

# %%
test["coverage error int"].value_counts()


# %%
def get_tenure(df):

    tenures = []
    for index, row in df.iterrows():
        if row["TENURE: owner-occupied"] == 1.0:
            tenure = "owner-occupied"
        elif row["TENURE: rental (private)"] == 1.0:
            tenure = "rental (private)"
        elif row["TENURE: rental (social)"] == 1.0:
            tenure = "rental (social)"
        elif row["TENURE: unknown"] == 1.0:
            tenure = "unknown"

        tenures.append(tenure)

    df["TENURE"] = tenures
    return df


test = get_tenure(test)

# %%
test["TENURE"].value_counts(dropna=False)

# %%
color_dict = {
    "owner-occupied": "red",
    "rental (social)": "teal",
    "rental (private)": "blue",
    "unknown": "green",
}

# %%
test["color"] = test["TENURE"].map(color_dict)

# %%
test["color"]

# %%
import matplotlib.pyplot as plt

plt.scatter(
    test["coverage error"], test["coverage ground truth"], color=list(test["color"])
)
plt.title(
    "Error: {} using {} on {}".format(
        "Coverage", "Random Forest Regressor", "Validation Set"
    )
)
plt.xlabel("Error")
plt.ylabel("Ground Truth")
plt.legend()
plt.show()

# %%
import matplotlib.pyplot as plt

plt.scatter(
    test["growth error"], test["growth ground truth"], color=list(test["color"])
)
plt.title(
    "Error: {} using {} on {}".format(
        "Growth", "Random Forest Regressor", "Validation Set"
    )
)
plt.xlabel("Error")
plt.ylabel("Ground Truth")
plt.legend()
plt.show()

# %%
import matplotlib.pyplot as plt

plt.scatter(
    test["growth prediction"], test["growth ground truth"], color=list(test["color"])
)
plt.title(
    "Prediction: {} using {} on {}".format(
        "Growth", "Random Forest Regressor", "Validation Set"
    )
)
plt.xlabel("Prediction")
plt.ylabel("Ground Truth")
plt.legend()
plt.show()

# %%
import matplotlib.pyplot as plt

plt.scatter(
    test["coverage prediction"],
    test["coverage ground truth"],
    color=list(test["color"]),
)
plt.title(
    "Prediction: {} using {} on {}".format(
        "Coverage", "Random Forest Regressor", "Validation Set"
    )
)
plt.xlabel("Prediction")
plt.ylabel("Ground Truth")
plt.legend()
plt.show()

# %%
test["coverage prediction int"].value_counts()

# %%
test["coverage ground truth int"].value_counts()

# %%
sample_x = epc_df.loc[epc_df["POSTCODE"] == "CM07BE"]

sample_x = epc_df.loc[epc_df["POSTCODE"] == "CM07FY"]


# %%

from ipywidgets import interact


@interact(feature=sample_x.columns)
def value_counts(feature):
    print(feature)
    print(sample_x[feature].value_counts(dropna=False))

    print(sample_x[feature].unique())
    print(sample_x[feature].max())
    print(sample_x[feature].min())


# %%
