# File: getters/feature_engineering.py
"""Create new features.

Created May 2021
@author: Julia Suter
Last updated on 13/07/2021
"""

# ---------------------------------------------------------------------------------

# Import
import pandas as pd
import re
from hashlib import md5

# ---------------------------------------------------------------------------------


def short_hash(text):
    """Generate a unique short hash for given string.

    Parameters
    ----------
    text: str
        String for which to get ID.

    Return
    ---------

    short_code: int
        Unique ID."""

    hx_code = md5(text.encode()).hexdigest()
    int_code = int(hx_code, 16)
    short_code = str(int_code)[:16]
    return int(short_code)


def get_unique_building_ID(df):
    """Add unique building ID column to dataframe.

    Parameters
    ----------
    text: str
        String for which to get ID.

    Return
    ---------

    short_code: int
        Unique ID."""

    # Remove samples with no address
    df.dropna(subset=["ADDRESS1"], inplace=True)

    # Create unique address and building ID
    df["UNIQUE_ADDRESS"] = df["ADDRESS1"] + df["POSTCODE"]
    df["BUILDING_ID"] = df["UNIQUE_ADDRESS"].apply(short_hash)

    return df


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
        if not (pd.isnull(heating) and isinstance(heating, float)):

            # Lowercase
            heating = heating.lower()

            other_heating_system = [
                ("boiler and radiator" in heating),
                ("boiler & radiator" in heating),
                ("boiler and underfloor" in heating),
                ("boiler & underfloor" in heating),
                ("community scheme" in heating),
                ("heater" in heating),  # not specified heater
            ]

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

            elif any(other_heating_system):

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


def get_year(date):
    """Year for given date.

    Parameters
    ----------
    date : str
        Given date in format year-month-day.

    Return
    ---------
    year : int
        Year derived from date."""

    if date == "unknown":
        return "unknown"

    year = date.split("-")[0]

    if len(year) != 4:
        return "unknown"

    return int(year)


def get_date_as_int(date):
    """Transform date into integer to compute earliest/latest date.

    Parameters
    ----------
    date : str
        Given date in format year-month-day or yearmonthday.

    Return
    ---------
    date : int
        Date as integer."""

    if date == "unknown":
        return "unknown"

    # Remove delimiters
    date = re.sub("-", "", date)
    date = re.sub("/", "", date)

    return int(date)


def get_date_features(df):
    """Get year of inspection and date as integer as features.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to which new features are added.

    Return
    ---------
    df : pandas.DataFrame
        Dataframe with new features."""

    df["YEAR"] = df["INSPECTION_DATE"].apply(get_year)
    df["DATE_INT"] = df["INSPECTION_DATE"].apply(get_date_as_int)

    return df


def filter_by_year(df, building_reference, year, up_to=True, selection=None):
    """Filter EPC dataset by year of inspection/entry.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe to which new features are added.

    building_reference : str
        Which building reference to use,
        e.g. "BUILDING_REFERENCE_NUMBER" or "BUILDING_ID".

    year : int, None, "all"
        Year by which to filter data.
        If None or "all", use all data.

    up_to : bool, default=True
        If True, get all samples up to given year.
        If False, only get sample from given year.

    selection : {"first entry", "latest entry"} or None, default=None
        For duplicates, get only first or latest entry.
        If None, do not remove any duplicates.

    Return
    ---------
    df : pandas.DataFrame
        Dataframe with new features."""

    # If year is given for filtering
    if year != "all" and year is not None:

        if up_to:
            df = df.loc[df["YEAR"] <= year]
        else:
            df = df.loc[df["YEAR"] == year]

    # Filter by selection
    selection_dict = {"first entry": "first", "latest entry": "last"}

    if selection in ["first entry", "latest entry"]:
        df = (
            df.sort_values("DATE_INT", ascending=True)
            .drop_duplicates(
                subset=[building_reference], keep=selection_dict[selection]
            )
            .sort_index()
        )

    elif selection is None:
        df = df

    else:
        raise IOError("{} not implemented.".format(selection))

    return df


def count_number_of_entries(row, feature, ref_counts):
    """Count the number entries for given building based on
    building reference number.

    row : pandas.Series
        EPC dataset row.

    feature: str
        Feature by which to count building entries.
        e.g. "BUILDING_REFERNCE_NUMBER" or "BUILDING_ID"

    ref_counts : pandas.Series
        Value counts for building reference number.

    Return
    ---------
    counts : int
        How many entries are there for given building."""

    building_ref = row[feature]
    try:
        counts = ref_counts[building_ref]
    except KeyError:
        return building_ref

    return counts


def get_building_entry_feature(df, feature):
    """Create feature that shows number of entries for any given building
    based on BUILDING_REFERENCE_NUMBER or BUILDING_ID.

    df : pandas.DataFrame
        EPC dataframe.

    feature: str
        Feature by which to count building entries.
        Has to be "BUILDING_REFERNCE_NUMBER" or "BUILDING_ID".

    Return
    ---------
    df : pandas.DataFrame
        EPC dataframe with # entry feature."""

    # Catch invalid inputs
    if feature not in ["BUILDING_REFERENCE_NUMBER", "BUILDING_ID"]:
        raise IOError("Feature '{}' is not a valid feature.".format(feature))

    feature_name_dict = {
        "BUILDING_REFERENCE_NUMBER": "N_ENTRIES",
        "BUILDING_ID": "N_ENTRIES_BUILD_ID",
    }

    # Get name of new feature
    new_feature_name = feature_name_dict[feature]

    # Count IDs
    counts = df[feature].value_counts()

    # Create new feature representing how many entries there are for building
    df[new_feature_name] = df.apply(
        lambda row: count_number_of_entries(row, feature, counts), axis=1
    )
    return df


def get_additional_features(df):

    df = get_date_features(df)

    df = get_unique_building_ID(df)
    df = get_building_entry_feature(df, "BUILDING_REFERENCE_NUMBER")
    df = get_building_entry_feature(df, "BUILDING_ID")

    df = get_heating_features(df)
    df = get_new_EPC_rating_features(df)

    return df
