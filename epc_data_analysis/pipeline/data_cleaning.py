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
