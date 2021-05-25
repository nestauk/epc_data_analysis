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
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: EPC_data_analysis
#     language: python
#     name: epc_data_analysis
# ---

# %%
import yaml
import pandas as pd
import numpy as np
from keplergl import KeplerGl

# %%
with open("../config/Kepler/tenure_type_correct_colors_config.txt", "r") as infile:
    config = infile.read()
    config = yaml.load(config)

# %%
wales_epc = pd.read_csv("../../outputs/data/Pandas Dataframes/out.csv", low_memory=True)

# %%
dataframe = wales_epc[
    [
        "TENURE",
        "longitude",
        "latitude",
        #'POSTCODE','PROPERTY_TYPE', 'BUILT_FORM',
        #   'INSPECTION_DATE', 'LOCAL_AUTHORITY_LABEL',
        #   'LODGEMENT_DATE', 'LODGEMENT_DATETIME',
        #   'TOTAL_FLOOR_AREA', 'ENERGY_TARIFF', 'MAINS_GAS_FLAG', 'FLOOR_LEVEL',
        "CURRENT_ENERGY_RATING",  #'POTENTIAL_ENERGY_RATING',
        # 'CURRENT_ENERGY_EFFICIENCY','POTENTIAL_ENERGY_EFFICIENCY',
        # 'DIFF_ENERGY_EFFICIENCY', 'DIFF_ENERGY_RATING',
        "CURR_ENERGY_RATING_IN_NUMBER",
        # 'ENVIRONMENT_IMPACT_CURRENT', 'ENVIRONMENT_IMPACT_POTENTIAL',
        # 'ENERGY_CONSUMPTION_CURRENT', 'ENERGY_CONSUMPTION_POTENTIAL',
        #   'CO2_EMISSIONS_CURRENT','CO2_EMISS_CURR_PER_FLOOR_AREA', 'CO2_EMISSIONS_POTENTIAL',
        # 'LIGHTING_COST_CURRENT', 'LIGHTING_COST_POTENTIAL',
        #  'HEATING_COST_CURRENT', 'HEATING_COST_POTENTIAL',
        # 'HOT_WATER_COST_CURRENT', 'HOT_WATER_COST_POTENTIAL',
        #   'MULTI_GLAZE_PROPORTION', 'GLAZED_TYPE', 'GLAZED_AREA', 'MAIN_FUEL'
        #  'HOTWATER_DESCRIPTION','HOT_WATER_ENERGY_EFF', 'HOT_WATER_ENV_EFF',
        #   'FLOOR_DESCRIPTION','FLOOR_ENERGY_EFF', 'FLOOR_ENV_EFF',
        #   'WINDOWS_DESCRIPTION', 'WINDOWS_ENERGY_EFF', 'WINDOWS_ENV_EFF',
        #  'WALLS_DESCRIPTION','WALLS_ENERGY_EFF', 'WALLS_ENV_EFF',
        #  'SECONDHEAT_DESCRIPTION', 'SHEATING_ENERGY_EFF', 'SHEATING_ENV_EFF',
        #   'ROOF_DESCRIPTION', 'ROOF_ENERGY_EFF', 'ROOF_ENV_EFF',
        "MAINHEAT_DESCRIPTION",  #'MAINHEAT_ENERGY_EFF', 'MAINHEAT_ENV_EFF',
        #  'MAINHEATCONT_DESCRIPTION','MAINHEATC_ENERGY_EFF', 'MAINHEATC_ENV_EFF',
        #  'LIGHTING_DESCRIPTION','LIGHTING_ENERGY_EFF', 'LIGHTING_ENV_EFF',
    ]
]


def get_EPC_rating_group(ratings):

    groups = []

    for rating in ratings:
        if rating in ["A", "B", "C"]:
            groups.append("A-C")
        else:
            groups.append("D-G")

    return groups


def get_heating_type(heating_types):

    general_type = []
    heating_type = []

    for heating in heating_types:

        print(heating)
        if not pd.isnull(heating):
            heating = heating.lower()

            # print(heating)

            if "ground source heat pump" in heating:
                h_type = "ground source heat pump"
                g_type = "electric"

            elif "air source heat pump" in heating:
                h_type = "air source heat pump"
                g_type = "electric"

            elif "electric storage heaters" in heating:
                h_type = "storage heater"
                g_type = "electric"

            elif "water source heat pump" in heating:
                h_type = "water source heat pump"
                g_type = "electric"

            elif "electric underfloor heating" in heating:
                h_type = "underfloor heating"
                g_type = "electric"

            elif "heat pump" in heating:
                h_type = "heat pump"
                g_type = "electric"

            elif "boiler and radiator" in heating:
                if "gas" in heating:
                    h_type = "boiler and radiator"
                    g_type = "gas"
                elif ", oil" in heating:
                    h_type = "boiler and radiator"
                    g_type = "oil"
                elif "lpg" in heating:
                    h_type = "boiler and radiator"
                    g_type = "LPG"
                elif "electric" in heating:
                    h_type = "boiler and radiator"
                    g_type = "electric"
                else:
                    h_type = "boiler and radiator"
                    g_type = ""

            elif "warm air" in heating:
                h_type = "warm air"
                g_type = "electric"

            elif "boiler and underfloor" in heating or "boiler & underfloor" in heating:
                if "gas" in heating:
                    h_type = "boiler and underfloor"
                    g_type = "gas"
                elif ", oil" in heating:
                    h_type = "boiler and underfloor"
                    g_type = "oil"
                elif "lpg" in heating:
                    h_type = "boiler and underfloor"
                    g_type = "LPG"
                elif "electric" in heating:
                    h_type = "boiler and underfloor"
                    g_type = "electric"
                else:
                    h_type = "boiler and underfloor"
                    g_type = ""

            elif "community scheme" in heating:
                if "gas" in heating:
                    h_type = "community scheme"
                    g_type = "gas"
                elif ", oil" in heating:
                    h_type = "community scheme"
                    g_type = "oil"
                elif "lpg" in heating:
                    h_type = "community scheme"
                    g_type = "LPG"
                elif "electric" in heating:
                    h_type = "community scheme"
                    g_type = "electric"
                else:
                    h_type = "community scheme"
                    g_type = ""

            elif "heater" in heating:
                if "gas" in heating:
                    h_type = "heater"
                    g_type = "gas"
                elif ", oil" in heating:
                    h_type = "heater"
                    g_type = "oil"
                elif "lpg" in heating:
                    h_type = "heater"
                    g_type = "LPG"
                elif "electric" in heating:
                    h_type = "heater"
                    g_type = "electric"
                else:
                    h_type = "heater"
                    g_type = ""

            else:
                h_type = "unknown"
                g_type = "unknown"

        else:
            h_type = "unknown"
            g_type = "unknown"

        general_type.append(g_type)
        heating_type.append(h_type)

    return heating_type, general_type


# dataframe = dataframe.sort_values(by=['CURRENT_ENERGY_RATING'])

dataframe = dataframe.drop(
    dataframe[dataframe.CURRENT_ENERGY_RATING == "INVALID!"].index
)

dataframe["EPC CATEGORY"] = get_EPC_rating_group(dataframe["CURRENT_ENERGY_RATING"])

# dataframe['HEATING_TYPE'], dataframe['HEATING_GENERAL_TYPE'] = get_heating_type(dataframe['MAINHEAT_DESCRIPTION'])

# social_rented = dataframe.loc[data_of_interest['TENURE'] == 'rental (social)']
# social_rented.head()
print(dataframe.shape)
dataframe.head()

# %%
dataframe.loc[dataframe["TENURE"] == "owner-occupied"]["CURRENT_ENERGY_RATING"].unique()

# %%
tenure_type_map = KeplerGl(height=500, config=config)

tenure_type_map.add_data(
    data=dataframe.loc[dataframe["TENURE"] == "rental (social)"], name="social"
)
tenure_type_map.add_data(
    data=dataframe.loc[dataframe["TENURE"] == "rental (private)"], name="private"
)
tenure_type_map.add_data(
    data=dataframe.loc[dataframe["TENURE"] == "owner-occupied"], name="owner-occupied"
)
tenure_type_map

# %%
tenure_type_map.save_to_html(
    file_name="../../outputs/data/Wales HTML/Wales_EPC_rating_by_tenure_type.html"
)
with open("../config/Kepler/tenure_type_correct_colors_config.txt", "w") as outfile:
    outfile.write(str(tenure_type_map.config))

# %%
dataframe["MAINHEAT_DESCRIPTION"].unique()

# %%
dataframe["MAINHEAT_DESCRIPTION"].unique().shape

# %%
heating_map = KeplerGl(height=500)

heating_map.add_data(
    data=dataframe.loc[dataframe["HEATING_GENERAL_TYPE"] == "gas"], name="gas"
)
heating_map.add_data(
    data=dataframe.loc[dataframe["HEATING_GENERAL_TYPE"] == "oil"], name="oil"
)
heating_map.add_data(
    data=dataframe.loc[dataframe["HEATING_GENERAL_TYPE"] == "electric"], name="electric"
)
heating_map

# %%
heating_map.save_to_html(
    file_name="../../outputs/data/Wales HTML/EPC_Rating_Wales_by_heating.html"
)
with open("../config/Kepler/heating_config_.txt", "w") as outfile:
    outfile.write(str(heating_map.config))
