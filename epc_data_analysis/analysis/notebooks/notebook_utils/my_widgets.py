from ipywidgets import widgets, interact, Layout, Select
from IPython.display import display


tenure_type_midi_old = widgets.Dropdown(
    options=[
        "rental (social)",
        "rental (private)",
        "owner-occupied",
        "unknown",
    ],
    value="rental (social)",
    description="Tenure Type",
    disabled=False,
)

# style = {"description_width": "150px"}


# Set box layout
box_layout = Layout(
    display="flex",
    flex_flow="column",
    align_items="stretch",
    border="solid",
    width="40%",
)


# Set feature set widget
tenure_type_midi = Select(
    options=["rental (social)", "rental (private)", "owner-occupied", "unknown"],
    value="rental (social)",
    description="Tenure Type",
    layout=box_layout,
)


def get_dropdown_midi(df):

    midi = widgets.Dropdown(
        options=df.columns, description="Column name", value="TENURE"
    )
    return midi


def get_custom_dropdown_midi(options):
    midi = widgets.Dropdown(options=options, description="Options")
    return midi
