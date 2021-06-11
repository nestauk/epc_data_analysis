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


def get_heating_type(heating_types):

    general_type = []
    heating_type = []

    for heating in heating_types:

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
                    g_type = "unknown"

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
                    g_type = "unknown"

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
                    g_type = "unknown"

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
                    g_type = "unknown"

            else:
                h_type = "unknown"
                g_type = "unknown"

        else:
            h_type = "unknown"
            g_type = "unknown"

        if "heat pump" in h_type:
            h_type = "heat pump"

        general_type.append(g_type)
        heating_type.append(h_type)

    return heating_type, general_type
