# File: getters/data_cleaning.py
"""Data cleaning.

Created August 2021
@author: Julia Suter
Last updated on 05/08/2021
"""


def reformat_postcode(df):
    """Change the POSTCODE feature in uniform format (without spaces).

    Parameters
    ----------
    df : pandas.Dataframe
        Dataframe to format.

    Return
    ----------
    df : pandas.Dataframe
        Dataframe with reformatted POSTCODE."""

    df["POSTCODE"] = df["POSTCODE"].str.replace(r" ", "")

    return df


def date_formatter(date):

    if isinstance(date, float):
        return date

    if "-" in date:
        return date

    day, month, year = str(date).split("/")

    return year + "-" + month + "-" + day


def standardise_tenure(tenure):
    """Standardise tenure types; one of the four categories:
    rental (social), rental (private), owner-occupied, unknown

    Parameters
    ----------
    tenure : str
        Raw tenure type.

    Return
    ----------
    standardised tenure : str
        Standardised tenure type."""

    if isinstance(tenure, float):
        return tenure

    tenure = tenure.lower()
    tenure_mapping = {
        "owner-occupied": "owner-occupied",
        "rental (social)": "rental (social)",
        "rented (social)": "rental (social)",
        "rental (private)": "rental (private)",
        "rented (private)": "rental (private)",
        "unknown": "unknown",
        "no data!": "unknown",
    }

    return tenure_mapping[tenure]


def clean_epc_data(df):
    """Standardise and clean EPC data.
    For example, reformat dates and standardise cateogories.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw/original EPC dataframe.

    Return
    ----------
    df : pandas.DataFrame
        Standarised and cleaned EPC dataframe."""

    # Drop samples with now lodegement date
    df.dropna(subset=["LODGEMENT_DATE", "INSPECTION_DATE"], inplace=True)

    # Reformat dates
    df["LODGEMENT_DATE"] = df["LODGEMENT_DATE"].apply(date_formatter)
    df["INSPECTION_DATE"] = df["INSPECTION_DATE"].apply(date_formatter)

    # Standarise tenure type
    df["TENURE"] = df["TENURE"].apply(standardise_tenure)

    return df
