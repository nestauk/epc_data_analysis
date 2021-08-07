# File: getters/my_widgets.py
"""Set iPython widgets.

Created May 2021
@author: Julia Suter
Last updated on 13/07/2021
"""

# ---------------------------------------------------------------------------------

# Import
from ipywidgets import widgets, interact, Layout, Select, Dropdown
from IPython.display import display

# ---------------------------------------------------------------------------------

# EPC column/feature sets

EPC_columns = [
    "LMK_KEY",
    "ADDRESS1",
    "ADDRESS2",
    "ADDRESS3",
    "POSTCODE",
    "BUILDING_REFERENCE_NUMBER",
    "CURRENT_ENERGY_RATING",
    "POTENTIAL_ENERGY_RATING",
    "CURRENT_ENERGY_EFFICIENCY",
    "POTENTIAL_ENERGY_EFFICIENCY",
    "PROPERTY_TYPE",
    "BUILT_FORM",
    "INSPECTION_DATE",
    "LOCAL_AUTHORITY",
    "CONSTITUENCY",
    "COUNTY",
    "LODGEMENT_DATE",
    "TRANSACTION_TYPE",
    "ENVIRONMENT_IMPACT_CURRENT",
    "ENVIRONMENT_IMPACT_POTENTIAL",
    "ENERGY_CONSUMPTION_CURRENT",
    "ENERGY_CONSUMPTION_POTENTIAL",
    "CO2_EMISSIONS_CURRENT",
    "CO2_EMISS_CURR_PER_FLOOR_AREA",
    "CO2_EMISSIONS_POTENTIAL",
    "LIGHTING_COST_CURRENT",
    "LIGHTING_COST_POTENTIAL",
    "HEATING_COST_CURRENT",
    "HEATING_COST_POTENTIAL",
    "HOT_WATER_COST_CURRENT",
    "HOT_WATER_COST_POTENTIAL",
    "TOTAL_FLOOR_AREA",
    "ENERGY_TARIFF",
    "MAINS_GAS_FLAG",
    "FLOOR_LEVEL",
    "FLAT_TOP_STOREY",
    "FLAT_STOREY_COUNT",
    "MAIN_HEATING_CONTROLS",
    "MULTI_GLAZE_PROPORTION",
    "GLAZED_TYPE",
    "GLAZED_AREA",
    "EXTENSION_COUNT",
    "NUMBER_HABITABLE_ROOMS",
    "NUMBER_HEATED_ROOMS",
    "LOW_ENERGY_LIGHTING",
    "NUMBER_OPEN_FIREPLACES",
    "HOTWATER_DESCRIPTION",
    "HOT_WATER_ENERGY_EFF",
    "HOT_WATER_ENV_EFF",
    "FLOOR_DESCRIPTION",
    "FLOOR_ENERGY_EFF",
    "FLOOR_ENV_EFF",
    "WINDOWS_DESCRIPTION",
    "WINDOWS_ENERGY_EFF",
    "WINDOWS_ENV_EFF",
    "WALLS_DESCRIPTION",
    "WALLS_ENERGY_EFF",
    "WALLS_ENV_EFF",
    "SECONDHEAT_DESCRIPTION",
    "SHEATING_ENERGY_EFF",
    "SHEATING_ENV_EFF",
    "ROOF_DESCRIPTION",
    "ROOF_ENERGY_EFF",
    "ROOF_ENV_EFF",
    "MAINHEAT_DESCRIPTION",
    "MAINHEAT_ENERGY_EFF",
    "MAINHEAT_ENV_EFF",
    "MAINHEATCONT_DESCRIPTION",
    "MAINHEATC_ENERGY_EFF",
    "MAINHEATC_ENV_EFF",
    "LIGHTING_DESCRIPTION",
    "LIGHTING_ENERGY_EFF",
    "LIGHTING_ENV_EFF",
    "MAIN_FUEL",
    "WIND_TURBINE_COUNT",
    "HEAT_LOSS_CORRIDOOR",
    "UNHEATED_CORRIDOR_LENGTH",
    "FLOOR_HEIGHT",
    "PHOTO_SUPPLY",
    "SOLAR_WATER_HEATING_FLAG",
    "MECHANICAL_VENTILATION",
    "ADDRESS",
    "LOCAL_AUTHORITY_LABEL",
    "CONSTITUENCY_LABEL",
    "POSTTOWN",
    "CONSTRUCTION_AGE_BAND",
    "LODGEMENT_DATETIME",
    "TENURE",
    "FIXED_LIGHTING_OUTLETS_COUNT",
    "LOW_ENERGY_FIXED_LIGHT_COUNT",
]

EPC_columns_selection = [
    "CURRENT_ENERGY_RATING",
    "POTENTIAL_ENERGY_RATING",
    "CURRENT_ENERGY_EFFICIENCY",
    "TENURE",
    "MAINHEAT_ENERGY_EFF",
    "MAINHEAT_ENV_EFF",
    "HOT_WATER_ENERGY_EFF",
    "HOT_WATER_ENV_EFF",
    "FLOOR_ENERGY_EFF",
    "FLOOR_ENV_EFF",
    "WINDOWS_ENERGY_EFF",
    "WINDOWS_ENV_EFF",
    "WALLS_ENERGY_EFF",
    "WALLS_ENV_EFF",
    "ROOF_ENERGY_EFF",
    "ROOF_ENV_EFF",
    "MAINHEATC_ENERGY_EFF",
    "MAINHEATC_ENV_EFF",
    "LIGHTING_ENERGY_EFF",
    "LIGHTING_ENV_EFF",
    "POSTCODE",
    "MAINHEAT_DESCRIPTION",
    "CO2_EMISSIONS_CURRENT",
    "CO2_EMISS_CURR_PER_FLOOR_AREA",
    "LIGHTING_COST_CURRENT",
    "LIGHTING_COST_POTENTIAL",
    "HEATING_COST_CURRENT",
    "HEATING_COST_POTENTIAL",
    "HOT_WATER_COST_CURRENT",
    "HOT_WATER_COST_POTENTIAL",
    "BUILDING_REFERENCE_NUMBER",
    "LODGEMENT_DATE",
    "INSPECTION_DATE",
    "BUILT_FORM",
    "PROPERTY_TYPE",
]

# ---------------------------------------------------------------------------------

# Set box layout
box_layout = Layout(
    display="flex",
    flex_flow="column",
    align_items="stretch",
    border="solid",
    width="40%",
)

# Widget for tenure type
tenure_type_widget = Dropdown(
    options=["rental (social)", "rental (private)", "owner-occupied", "unknown"],
    value="rental (social)",
    description="Tenure Type",
    # layout=box_layout,
)

# Widget for tenure type
quartile_type_widget = Dropdown(
    options=[1, 2, 3, 4],
    value=1,
    description="WIMD Quartile",
    # layout=box_layout,
)

# Widget for features
feature_widget = widgets.SelectMultiple(
    options=EPC_columns,
    value=EPC_columns_selection,
    description="EPC Dataset Columns",
    disabled=False,
    continuous_update=True,
    layout=box_layout,
)

# Widget for UK part
UK_part_widget = widgets.Dropdown(
    options=["Wales", "England", "Scotland", "all"],
    value="all",
    description="Part of UK",
    # layout=box_layout,
)

ylim_slider_widget = widgets.IntSlider(
    value=75,
    min=0,
    max=200,
    step=1,
    description="ylim:",
    disabled=False,
    continuous_update=False,
    orientation="horizontal",
    readout=True,
    readout_format="d",
)


def get_custom_widget(
    options, default_value=None, description="Options", widget_type="dropdown"
):
    """Create custom dropdown or select widget with different options.

    Parameters
    ----------
    options : list
        Options to select from in Widget.

    default_value : str, default=None
        This option is selected as default.
        If None is selected, first option becomes default.

    description : str, default='Options'
        Description for the widget.

    widget_type : {"select", "dropdown"}
        Widget type (selection or dropdown).

    Return
    ---------

    custom_widget : ipywidgets.Widget
        Custom widget with given options, default value and description.
    """

    # Use first option as default value
    if default_value is None:
        default_value = options[0]

    # Create custom select widget
    if widget_type == "select":
        custom_widget = widgets.Select(
            options=options,
            value=default_value,
            description=description,
            layout=box_layout,
        )

    # Create custom dropdown widget
    elif widget_type == "dropdown":
        custom_widget = widgets.Dropdown(
            options=options, value=default_value, description=description
        )
    else:
        raise IOError(
            "Widget type '{}' is unknown. Please choose 'select' or 'dropdown'.".format(
                widget_type
            )
        )

    return custom_widget


# Create efficiency widget
efficiency_widget = get_custom_widget(
    [
        "MAINHEAT_ENERGY_EFF",
        "MAINHEAT_ENV_EFF",
        "HOT_WATER_ENERGY_EFF",
        "HOT_WATER_ENV_EFF",
        "FLOOR_ENERGY_EFF",
        "FLOOR_ENV_EFF",
        "WINDOWS_ENERGY_EFF",
        "WINDOWS_ENV_EFF",
        "WALLS_ENERGY_EFF",
        "WALLS_ENV_EFF",
        "ROOF_ENERGY_EFF",
        "ROOF_ENV_EFF",
        "MAINHEATC_ENERGY_EFF",
        "MAINHEATC_ENV_EFF",
        "LIGHTING_ENERGY_EFF",
        "LIGHTING_ENV_EFF",
    ],
    widget_type="dropdown",
    description="Efficiency",
)

# Create WIMD widget
WIMD_widget = get_custom_widget(
    ["WIMD Decile", "WIMD Quartile", "WIMD Quintile", "WIMD Score", "WIMD Rank"],
    widget_type="dropdown",
    description="WIMD",
)


# Create Cost widget

cost_widget = get_custom_widget(
    [
        "LIGHTING_COST_CURRENT",
        "LIGHTING_COST_POTENTIAL",
        "HEATING_COST_CURRENT",
        "HEATING_COST_POTENTIAL",
        "HOT_WATER_COST_CURRENT",
        "HOT_WATER_COST_POTENTIAL",
    ],
    widget_type="dropdown",
    description="Costs",
)
