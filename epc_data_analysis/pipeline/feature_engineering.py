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

    # EPC rating in number instead of letter
    df["CURR_ENERGY_RATING_NUM"] = df.CURRENT_ENERGY_RATING.map(rating_dict)

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

    general_type = []
    heating_type = []

    heating_types = df["MAINHEAT_DESCRIPTION"]

    # Get specific and general heating category for each entry
    for heating in heating_types:

        if not pd.isnull(heating):

            # Lowercase
            heating = heating.lower()

            # Different heat pump types

            if "ground source heat pump" in heating:
                h_type = "ground source heat pump"
                g_type = "electric"

            elif "air source heat pump" in heating:
                h_type = "air source heat pump"
                g_type = "electric"

            elif "water source heat pump" in heating:
                h_type = "water source heat pump"
                g_type = "electric"

            elif "heat pump" in heating:
                h_type = "heat pump"
                g_type = "electric"

            # Electric heaters

            elif "electric storage heaters" in heating:
                h_type = "storage heater"
                g_type = "electric"

            elif "electric underfloor heating" in heating:
                h_type = "underfloor heating"
                g_type = "electric"

            # Boiler and radiator

            elif "boiler and radiator" in heating:
                if "gas" in heating:
                    h_type = "boiler and radiator"
                    g_type = "gas"

                elif ", oil" in heating:  # with preceeding comma (!= "boiler")
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
                    g_type = "unknown"

            # Boiler and underfloor heating

            elif "boiler and underfloor" in heating or "boiler & underfloor" in heating:

                if "gas" in heating:
                    h_type = "boiler and underfloor"
                    g_type = "gas"

                elif ", oil" in heating:  # with preceeding comma (!= "boiler")
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
                    g_type = "unknown"

            # Community scheme

            elif "community scheme" in heating:
                if "gas" in heating:
                    h_type = "community scheme"
                    g_type = "gas"

                elif ", oil" in heating:  # with preceeding comma (!= "boiler")
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
                    g_type = "unknown"

            # Heater (not specified)

            elif "heater" in heating:
                if "gas" in heating:
                    h_type = "heater"
                    g_type = "gas"

                elif ", oil" in heating:  # with preceeding comma (!= "boiler")
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
                    g_type = "unknown"

            # Warm air

            elif "warm air" in heating:
                h_type = "warm air"
                g_type = "electric"

            else:
                h_type = "unknown"
                g_type = "unknown"

        # Unknown heating system

        else:
            h_type = "unknown"
            g_type = "unknown"

        # Don't differentiate between heat pump types
        if not fine_grained_HP_types:

            if "heat pump" in h_type:
                h_type = "heat pump"

        # Save heating type
        general_type.append(g_type)
        heating_type.append(h_type)

    df["HEATING_SYSTEM"] = heating_type
    df["HEATING_SOURCE"] = general_type

    return df
