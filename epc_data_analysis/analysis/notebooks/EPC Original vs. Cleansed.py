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

# %% [markdown]
# # Comparing the Original EPC Dataset with the Cleansed Version

# %%
import pandas as pd
from ipywidgets import interact

from epc_data_analysis import PROJECT_DIR
from epc_data_analysis.getters import epc_data, util_data
from epc_data_analysis.analysis.notebooks.notebook_utils import my_widgets
from epc_data_analysis.pipeline import feature_engineering, easy_plotting, data_cleaning

# %% [markdown]
# ## Getting the data
#
# The original data is made to match the cleansed set: only England and Wales data and de-duplicated.
#
# The preprocessed original data can be loaded directly or processed here.

# %%
use_preprocessed_original_data = True
save_preprocessed_data = False

DIR_PATH = str(PROJECT_DIR) + "/inputs/Comparing_datasets/"

# %% [markdown]
# ### Loading the cleansed data

# %%
cleansed_epc_df = pd.read_csv(
    DIR_PATH + "EPC_Records__cleansed_and_deduplicated.csv", low_memory=True
)

cleansed_epc_df["YEAR"] = cleansed_epc_df["LODGEMENT_DATE"].apply(
    feature_engineering.get_year
)

# %% [markdown]
# ### Option 1) Loading the preprocessed orignal data

# %%
if use_preprocessed_original_data:
    original_epc_df = pd.read_csv(DIR_PATH + "Original_EPC_Wales_England.csv")
    original_epc_df_non_depl = pd.read_csv(
        DIR_PATH + "Original_EPC_Wales_England_non_depupl.csv"
    )

# %% [markdown]
# ### Option 2) Preprocessing the original data

# %%
if not use_preprocessed_original_data:

    features_of_interest = [
        "ADDRESS1",
        "CURRENT_ENERGY_RATING",
        "POTENTIAL_ENERGY_RATING",
        "TENURE",
        "CURRENT_ENERGY_EFFICIENCY",
        "LMK_KEY",
        "POSTCODE",
        "MAINHEAT_DESCRIPTION",
        "CO2_EMISSIONS_CURRENT",
        "CO2_EMISS_CURR_PER_FLOOR_AREA",
        "LIGHTING_COST_CURRENT",
        "HEATING_COST_CURRENT",
        "HOT_WATER_COST_CURRENT",
        "BUILDING_REFERENCE_NUMBER",
        "LODGEMENT_DATE",
        "INSPECTION_DATE",
        "BUILT_FORM",
        "PROPERTY_TYPE",
        "CONSTRUCTION_AGE_BAND",
        "TRANSACTION_TYPE",
        "MAIN_FUEL",
        "TOTAL_FLOOR_AREA",
        "ENERGY_TARIFF",
    ]

    epc_Wales = epc_data.load_epc_data(
        subset="Wales", usecols=features_of_interest, low_memory=False
    )

    epc_England = epc_data.load_epc_data(
        subset="England", usecols=features_of_interest, low_memory=False
    )

    print("Wales: {} samples".format(epc_Wales.shape[0]))
    print("England: {} samples".format(epc_England.shape[0]))
    original_epc_df = pd.concat([epc_Wales, epc_England], axis=0)

    print("Combined: {} samples".format(original_epc_df.shape[0]))

    print("------------------")

    # Preprocessing
    original_epc_df_non_depl = data_cleaning.clean_epc_data(original_epc_df)
    print(original_epc_df_non_depl.shape)

    original_epc_df_non_depl = feature_engineering.get_additional_features(
        original_epc_df
    )
    print(original_epc_df_non_depl.shape)

    original_epc_df = feature_engineering.filter_by_year(
        original_epc_df_non_depl, "BUILDING_ID", None, selection="latest entry"
    )
    print(original_epc_df.shape)

# %%
if save_preprocessed_data:
    original_epc_df.to_csv(DIR_PATH + "Original_EPC_Wales_England.csv", index=False)
    original_epc_df_non_depl.to_csv(
        DIR_PATH + "Original_EPC_Wales_England_non_depupl.csv", index=False
    )

# %% [markdown]
# ## Analysis
#
# ### Sample comparison

# %%
print("Original: {} samples".format(original_epc_df.shape[0]))
print("Cleansed: {} samples".format(cleansed_epc_df.shape[0]))
print("-------------------")
print(
    "Original: {} features\nDepends on selection of features.".format(
        original_epc_df.shape[1]
    )
)
print()
print("Cleansed: {} features".format(cleansed_epc_df.shape[1]))

# %% [markdown]
# ### Comparing distributions (normalised)

# %%
column_widget_1 = my_widgets.get_custom_widget(
    original_epc_df.columns,
    description="Original EPC feature",
    default_value="CURRENT_ENERGY_RATING",
    widget_type="dropdown",
)

column_widget_2 = my_widgets.get_custom_widget(
    cleansed_epc_df.columns,
    description="Cleansed EPC feature",
    default_value="FINAL_EPC_BAND",
    widget_type="dropdown",
)


print("Original EPC Data")


@interact(category=column_widget_1)
def plot_distribution_normalised(category):
    easy_plotting.plot_subcategory_distribution(
        original_epc_df,
        category,
        normalize=True,
        y_label="Properties",
        x_tick_rotation=45,
        plot_title="Original EPC: Distribution for {} (%)".format(category),
    )


print("Cleansed EPC Data")


@interact(category=column_widget_2)
def plot_distribution_normalised(category):
    easy_plotting.plot_subcategory_distribution(
        cleansed_epc_df,
        category,
        normalize=True,
        y_label="Properties",
        x_tick_rotation=45,
        plot_title="Cleansed EPC: Distribution for {} (%)".format(category),
    )


# %% [markdown]
# ### Comparing distributions (not normalised)

# %%
column_widget_1 = my_widgets.get_custom_widget(
    original_epc_df.columns,
    description="EPC feature",
    default_value="CURRENT_ENERGY_RATING",
    widget_type="dropdown",
)

column_widget_2 = my_widgets.get_custom_widget(
    cleansed_epc_df.columns,
    description="EPC feature",
    default_value="FINAL_EPC_BAND",
    widget_type="dropdown",
)


print("Original EPC Data")


@interact(category=column_widget_1)
def plot_distribution(category):
    easy_plotting.plot_subcategory_distribution(
        original_epc_df,
        category,
        normalize=False,
        y_label="Properties",
        x_tick_rotation=45,
        y_ticklabel_type="k",
        plot_title="Original EPC: Distribution for {}".format(category),
    )


print("Cleansed EPC Data")


@interact(category=column_widget_2)
def plot_distribution(category):
    easy_plotting.plot_subcategory_distribution(
        cleansed_epc_df,
        category,
        normalize=False,
        y_label="Properties",
        x_tick_rotation=45,
        y_ticklabel_type="k",
        plot_title="Cleansed EPC: Distribution for {}".format(category),
    )


# %% [markdown]
# ## What data is kept? The latest entry?
#
# Get properties with several buildings and check lodgement date (and for double checking also EPC score).

# %%
original_epc_df[original_epc_df["N_ENTRIES_BUILD_ID"] > 1]["BUILDING_REFERENCE_NUMBER"]

# %%
building_reference_example = [
    4649558968,
    7194793278,
    8347289178,
    9661627568,
    5936297078,
][2]

# %%
original_epc_df_non_depl[
    original_epc_df_non_depl["BUILDING_REFERENCE_NUMBER"] == building_reference_example
][["CURRENT_ENERGY_EFFICIENCY", "LODGEMENT_DATE", "LMK_KEY"]]

# %%
original_epc_df[
    original_epc_df["BUILDING_REFERENCE_NUMBER"] == building_reference_example
][["CURRENT_ENERGY_EFFICIENCY", "LODGEMENT_DATE", "LMK_KEY"]]

# %%
cleansed_epc_df[
    cleansed_epc_df["BUILDING_REFERENCE_NUMBER"] == building_reference_example
][["FINAL_EPC_SCORE", "LODGEMENT_DATE", "LMK_KEY"]]

# %% [markdown]
# ### Final Fuel Bill Composision
#
# FINAL_FUEL_BILL seems to be combination of HEATING_COST_CURRENT, HOT_WATER_COST_CURRENT and LIGHTING_COST_CURRENT.

# %%
building_reference_number = 9637549468

original_sample = original_epc_df[
    original_epc_df["BUILDING_REFERENCE_NUMBER"] == building_reference_number
]
cleansed_sample = cleansed_epc_df[
    cleansed_epc_df["BUILDING_REFERENCE_NUMBER"] == building_reference_number
]


print(original_sample["HEATING_COST_CURRENT"])
print(original_sample["HOT_WATER_COST_CURRENT"])
print(original_sample["LIGHTING_COST_CURRENT"])

print(cleansed_sample["FINAL_FUEL_BILL"])

print("----------------------")
print(
    "Summed up costs:",
    original_sample["HEATING_COST_CURRENT"]
    + original_sample["HOT_WATER_COST_CURRENT"]
    + original_sample["LIGHTING_COST_CURRENT"],
)

# %% [markdown]
# ### What happened to the unknown sector and other NODATA! entries?
#
# What happened to samples with unknown tenure type or other missing data?
#
# Some data could be filled in, other samples were discarded.
#
# ```
# Tenure Type:  0.2% filled in
# Construction Age: 0.6% filled in
# Built Form: 70% filled in
# ```

# %%
unknown_tenure_keys = list(
    original_epc_df[original_epc_df["TENURE"] == "unknown"]["BUILDING_REFERENCE_NUMBER"]
)
unknown_age_keys = list(
    original_epc_df[original_epc_df["CONSTRUCTION_AGE_BAND"] == "unknown"][
        "BUILDING_REFERENCE_NUMBER"
    ]
)
unknown_built_keys = list(
    original_epc_df[original_epc_df["BUILT_FORM"] == "NO DATA!"][
        "BUILDING_REFERENCE_NUMBER"
    ]
)

print("Number of unknown data samples for:")
print("Tenure: {}".format(len(unknown_tenure_keys)))
print("Construction Age: {}".format(len(unknown_age_keys)))
print("Built Form: {}".format(len(unknown_built_keys)))

cleansed_epc_df[cleansed_epc_df["BUILDING_REFERENCE_NUMBER"].isin(unknown_tenure_keys)][
    "FINAL_PROP_TENURE"
].value_counts()

# %%
cleansed_epc_df[cleansed_epc_df["BUILDING_REFERENCE_NUMBER"].isin(unknown_age_keys)][
    "FINAL_PROPERTY_AGE"
].value_counts()

# %%
cleansed_epc_df[cleansed_epc_df["BUILDING_REFERENCE_NUMBER"].isin(unknown_built_keys)][
    "FINAL_PROPERTY_TYPE"
].value_counts()

# %% [markdown]
# ### LMK_KEYS are differnet for two datasets
#
# There seems to be no overlap, even on the newer data.

# %%
cleansed_epc_df[cleansed_epc_df["BUILDING_REFERENCE_NUMBER"] == 4504250668][
    ["LMK_KEY", "ADDRESS1", "POSTCODE"]
]

# %%
original_epc_df[original_epc_df["BUILDING_REFERENCE_NUMBER"] == 4504250668][
    ["LMK_KEY", "ADDRESS1", "POSTCODE"]
]

# %%
LMK_KEY_example = "460450212302020031014402078409708"
# LMK_KEY_example = '460450257032010032507140438268803'

# %%
original_epc_df[original_epc_df["LMK_KEY"] == str(LMK_KEY_example)]

# %%
original_epc_df_non_depl[
    original_epc_df_non_depl["BUILDING_REFERENCE_NUMBER"] == 5368814768
]["LMK_KEY"]

# %%
cleansed_epc_df[cleansed_epc_df["LMK_KEY"] == LMK_KEY_example]

# %%
cleansed_epc_df[cleansed_epc_df["LMK_KEY"] == int(LMK_KEY_example)]

# %% [markdown]
# ### LMK_KEYS are differnet for two datasets - What about the 2020 data?
#
# There seems to be no overlap, even on the newer data.

# %%
cleansed_2020 = list(cleansed_epc_df[cleansed_epc_df["YEAR"] == 2020]["LMK_KEY"])

# %%
original_2020 = list(original_epc_df[original_epc_df["YEAR"] == 2020]["LMK_KEY"])

# %%
original_2020_non_dedupl = list(
    original_epc_df_non_depl[original_epc_df_non_depl["YEAR"] == 2020]["LMK_KEY"]
)

# %%
print(len(cleansed_2020))
print(len(original_2020))
print(len(original_2020_non_dedupl))

# %%
# for key in cleansed_2020:
#    if key in original_2020_non_dedupl:
#        print(key)

# %%
original_epc_df[original_epc_df["LMK_KEY"] == "918812462502020072622401808702468"]

# %%
cleansed_epc_df[cleansed_epc_df["BUILDING_REFERENCE_NUMBER"] == 588167078]

# %%
original_epc_df[original_epc_df["LMK_KEY"] == "1809118592242020070922512673000818"]

# %%
cleansed_epc_df[cleansed_epc_df["LMK_KEY"] == "1809118592242020070922512673000818"]

# %%
