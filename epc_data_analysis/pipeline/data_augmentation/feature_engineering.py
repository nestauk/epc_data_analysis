import pandas as pd


def get_new_EPC_rating_features(df: pd.DataFrame) -> pd.DataFrame:
    """Get new EPC rating features related to EPC ratings."""

    rating_dict = {
        "A": 7,
        "B": 6,
        "C": 5,
        "D": 4,
        "E": 3,
        "F": 2,
        "G": 1,
        "INVALID!": 0,
    }

    # EPC rating in number instead of letter
    df["CURR_ENERGY_RATING_NUM"] = df.CURRENT_ENERGY_RATING.map(rating_dict)

    # Numerical difference between current and potential energy rating (A-G)
    df["DIFF_ENERGY_RATING"] = (
        df.POTENTIAL_ENERGY_RATING.map(rating_dict) - df["CURR_ENERGY_RATING_NUM"]
    )

    return df
