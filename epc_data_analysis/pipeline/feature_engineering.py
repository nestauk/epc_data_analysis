# File: getters/feature_engineering.py
"""Create new features.

Created May 2021
@author: Julia Suter
Last updated on 13/07/2021
"""

# ---------------------------------------------------------------------------------

# Import
import pandas as pd

# ---------------------------------------------------------------------------------


def get_new_EPC_rating_features(df):
    """Get new EPC rating features related to EPC ratings.

        CURR_ENERGY_RATING_NUM: EPC rating representeed as number
        high number = high rating.

        ENERGY_RATING_CAT: EPC category.
        A-B, C-D or E-G

        DIFF_POT_ENERGY_RATING: Difference potential and current
        energy rating.


    Parameters
    ----------
    df : pandas.Dataframe
        EPC dataframe.

    Return
    ---------
    df : pandas.DateFrame
        Updated EPC dataframe with new EPC rating features."""

    # EPC rating dict
    rating_dict = {
        "A": 7,
        "B": 6,
        "C": 5,
        "D": 4,
        "E": 3,
        "F": 2,
        "G": 1,
        "H": 0,
        "INVALID!": 0,
    }

    EPC_cat_dict = {
        "A": "A-B",
        "B": "A-B",
        "C": "C-D",
        "D": "C-D",
        "E": "E-G",
        "F": "E-G",
        "G": "E-G",
    }

    # EPC rating in number instead of letter
    df["CURR_ENERGY_RATING_NUM"] = df.CURRENT_ENERGY_RATING.map(rating_dict)

    # EPC rating in category (A-B, C-D or E-G)
    df["ENERGY_RATING_CAT"] = df.CURRENT_ENERGY_RATING.map(EPC_cat_dict)

    # Numerical difference between current and potential energy rating (A-G)
    df["DIFF_POT_ENERGY_RATING"] = (
        df.POTENTIAL_ENERGY_RATING.map(rating_dict) - df["CURR_ENERGY_RATING_NUM"]
    )

    # Set DIFF_POT_ENERGY_RATING to 0.0
    # if substraction yielded value below 0.0 due to input error (few cases).
    df = df[df.DIFF_POT_ENERGY_RATING >= 0.0]

    return df


def map_quality_to_number(df, list_of_features):

    quality_to_num_dict = {
        "Very Good": 5.0,
        "Good": 4.0,
        "Average": 3.0,
        "Poor": 2.0,
        "Very Poor": 1.0,
    }

    for feature in list_of_features:
        df[feature + "_AS_NUM"] = df[feature].map(quality_to_num_dict)

    return df


def get_heating_features(df, fine_grained_HP_types=False):
    """Get heating type category based on HEATING_TYPE category.
    heating_system: heat pump, boiler, community scheme etc.
    heating_source: oil, gas, LPC, electric.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe that is updated with heating features.

    fine_grained_HP_types : bool, default=False
        If True, get different heat pump types (air sourced, ground sourced etc.).
        If False, return "heat pump" as heating type category.

    Return
    ---------
    df : pandas.DataFrame
        Updated dataframe with heating system and source."""

    # Collections
    heating_system_types = []
    heating_source_types = []

    # Get heating types
    heating_types = df["MAINHEAT_DESCRIPTION"]

    # Get specific and general heating category for each entry
    for heating in heating_types:

        # Set default value
        system_type = "unknown"
        source_type = "unknown"

        # If heating value exists
        if not pd.isnull(heating):

            # Lowercase
            heating = heating.lower()

            # Different heat pump types
            # --------------------------

            if "ground source heat pump" in heating:
                system_type = "ground source heat pump"
                source_type = "electric"

            elif "air source heat pump" in heating:
                system_type = "air source heat pump"
                source_type = "electric"

            elif "water source heat pump" in heating:
                system_type = "water source heat pump"
                source_type = "electric"

            elif "heat pump" in heating:
                system_type = "heat pump"
                source_type = "electric"

            # Electric heaters
            # --------------------------

            elif "electric storage heaters" in heating:
                system_type = "storage heater"
                source_type = "electric"

            elif "electric underfloor heating" in heating:
                system_type = "underfloor heating"
                source_type = "electric"

            # Warm air
            # --------------------------

            elif "warm air" in heating:
                system_type = "warm air"
                source_type = "electric"

            # Boiler and radiator / Boiler and underfloor / Community scheme / Heater (unspecified)
            # --------------------------

            elif (
                ("boiler and radiator" in heating)
                or ("boiler & radiator" in heating)
                or ("boiler and underfloor" in heating)
                or ("boiler & underfloor" in heating)
                or ("community scheme" in heating)
                or ("heater" in heating)  # not specified heater
            ):

                # Set heating system dict
                heating_system_dict = {
                    "boiler and radiator": "boiler and radiator",
                    "boiler & radiator": "boiler and radiator",
                    "boiler and underfloor": "boiler and underfloor",
                    "boiler & underfloor": "boiler and underfloor",
                    "community scheme": "community scheme",
                    "heater": "heater",  # not specified heater (otherwise handeld above)
                }

                # Set heating source dict
                heating_source_dict = {
                    "gas": "gas",
                    ", oil": "oil",  # with preceeding comma (!= "boiler")
                    "lpg": "LPG",
                    "electric": "electric",
                }

                # If heating system word is found, save respective system type
                for word, system in heating_system_dict.items():
                    if word in heating:
                        system_type = system

                # If heating source word is found, save respective source type
                for word, source in heating_source_dict.items():
                    if word in heating:
                        source_type = source

        # Don't differentiate between heat pump types
        if not fine_grained_HP_types:

            if "heat pump" in system_type:
                system_type = "heat pump"

        # Save heating system type and source type
        heating_system_types.append(system_type)
        heating_source_types.append(source_type)

    # Add heating system and source to df
    df["HEATING_SYSTEM"] = heating_system_types
    df["HEATING_SOURCE"] = heating_source_types

    return df
