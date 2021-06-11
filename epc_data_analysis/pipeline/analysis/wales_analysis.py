import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR

# Load config file
epc_data_config = get_yaml_config(
    Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml")
)
FIG_PATH = str(PROJECT_DIR) + epc_data_config["FIGURE_PATH"]


def emissions_by_tenure_type(df, feature):

    # Emissions by tenure type
    print(df.groupby("TENURE")["CO2_EMISSIONS_CURRENT"].sum())

    # Total emissions
    total_wales_emissions = np.sum(df["CO2_EMISSIONS_CURRENT"].sum())
    total_wales_emissions_by_area = np.sum(df["CO2_EMISS_CURR_PER_FLOOR_AREA"].sum())

    if feature == "CO2_EMISSIONS_CURRENT":
        total = total_wales_emissions
    else:
        total = total_wales_emissions_by_area

    emissions_by_tenure_rel = df.groupby("TENURE")[feature].sum() / total * 100
    emissions_by_tenure_abs = df.groupby("TENURE")[feature].sum()
    emissions_by_tenure_mean = df.groupby("TENURE")[feature].mean()
    emission_by_dwelling = emissions_by_tenure_abs / df["TENURE"].value_counts()

    if feature == "CO2_EMISSIONS_CURRENT":

        emissions_by_tenure_rel.plot(kind="bar", color="lightseagreen")
        plt.title("CO2 Emissions by Tenure Type (%)")
        plt.ylabel(
            "CO2 Emissions (%)\n(total of {}k tonnes/year)".format(
                str(round(total_wales_emissions, 0))[:-3]
            )
        )

        ax = plt.gca()
        for i, cty in enumerate(emissions_by_tenure_rel.values):
            ax.text(i, cty + 2, str(round(cty, 1)) + "%", horizontalalignment="center")

        ax.set_ylim([0.0, 80.0])
        plt.xticks(rotation=0)
        plt.xlabel("")
        plt.tight_layout()
        plt.savefig(FIG_PATH + "CO2 Emissions by Tenure Type Wales (%)")
        plt.show()

        emissions_by_tenure_mean.plot(kind="bar", color="lightseagreen")
        plt.title("Mean CO2 Emissions by Tenure Type")
        plt.ylabel("Mean CO2 Emissions")

        ax = plt.gca()
        for i, cty in enumerate(emissions_by_tenure_mean.values):
            ax.text(i, cty + 0.1, str(round(cty, 1)), horizontalalignment="center")

        ax.set_ylim([0.0, 6])
        plt.xticks(rotation=0)
        plt.xlabel("")
        plt.tight_layout()
        plt.savefig(FIG_PATH + "Mean CO2 Emissions by Tenure Type Wales (%)")
        plt.show()

        emissions_by_tenure_abs.plot(kind="bar", color="lightseagreen")
        ax = plt.gca()
        plt.title("CO2 Emissions by Tenure Type")
        plt.ylabel("CO2 Emissions\n[tonnes/year]")

        ylabels = ["{:.0f}".format(x / 1000) + "k" for x in ax.get_yticks()]
        ax.set_yticklabels(ylabels)

        for i, cty in enumerate(emissions_by_tenure_abs.values):
            ax.text(
                i, cty + 50000, str(int(cty / 1000)) + "k", horizontalalignment="center"
            )

        ax.set_ylim([0.0, 3000000])
        plt.xticks(rotation=0)
        plt.xlabel("")

        plt.tight_layout()
        plt.savefig(FIG_PATH + "CO2 Emissions by Tenure Type Wales (absolute)")
        plt.show()

        n_dwellings = df.shape[0]
        emission_by_dwelling.plot(kind="bar", color="lightseagreen")

        plt.title("CO2 Emissions by Tenure Type per Dwelling")
        plt.ylabel("CO2 Emissions\n[tonnes/year/dwelling]")

        ax = plt.gca()

        for i, cty in enumerate(emission_by_dwelling.values):
            ax.text(i, cty + 0.1, round(cty, 1), horizontalalignment="center")

        ylabels = ["{:.0f}".format(x) for x in ax.get_yticks()]
        ax.set_yticklabels(ylabels)
        plt.xticks(rotation=0)
        ax.set_ylim([0.0, 6])

        plt.tight_layout()
        plt.savefig(FIG_PATH + "CO2 Emissions by Tenure Type Wales per dwelling")

    elif feature == "CO2_EMISS_CURR_PER_FLOOR_AREA":

        emissions_by_tenure_rel.plot(kind="bar", color="lightseagreen")
        plt.title("CO2 Emissions per Floor Area by Tenure Type (%)")
        plt.ylabel(
            "CO2 Emissions (%) [kg/m²]".format(
                str(round(total_wales_emissions, 0))[:-3]
            )
        )

        ax = plt.gca()
        for i, cty in enumerate(emissions_by_tenure_rel.values):
            ax.text(i, cty + 2, str(round(cty, 1)) + "%", horizontalalignment="center")

        ax.set_ylim([0.0, 75])
        plt.xticks(rotation=0)
        plt.xlabel("")
        plt.tight_layout()
        plt.savefig(FIG_PATH + "CO2 Emissions per Floor Area by Tenure Type Wales (%)")
        plt.show()

        emissions_by_tenure_abs.plot(kind="bar", color="lightseagreen")
        ax = plt.gca()

        for i, cty in enumerate(emissions_by_tenure_abs.values):
            ax.text(
                i,
                cty + 250000,
                str(int(cty / 1000)) + "k",
                horizontalalignment="center",
            )

        ylabels = ["{:.0f}".format(x / 1000) + "k" for x in ax.get_yticks()]
        ax.set_yticklabels(ylabels)
        plt.xticks(rotation=0)
        plt.xlabel("")

        plt.title("CO2 Emissions per Floor Area by Tenure Type")
        plt.ylabel("CO2 Emissions (%) [kg/m²]")

        plt.tight_layout()
        plt.savefig(
            FIG_PATH + "CO2 Emissions per Floor Area by Tenure Type Wales (absolute)"
        )
        plt.show()

    else:
        print("Not implemented")


def emissions_by_wimd_type(df, feature_1, feature_2):

    # Emissions by tenure type
    print(df.groupby(feature_2)["CO2_EMISSIONS_CURRENT"].sum())

    # Total emissions
    total_wales_emissions = np.sum(df["CO2_EMISSIONS_CURRENT"].sum())
    total_wales_emissions_by_area = np.sum(df["CO2_EMISS_CURR_PER_FLOOR_AREA"].sum())

    if feature_1 == "CO2_EMISSIONS_CURRENT":
        total = total_wales_emissions
    else:
        total = total_wales_emissions_by_area

    emissions_by_tenure_rel = df.groupby(feature_2)[feature_1].sum() / total * 100
    emissions_by_tenure_abs = df.groupby(feature_2)[feature_1].sum()
    emissions_by_tenure_mean = df.groupby(feature_2)[feature_1].mean()
    emission_by_dwelling = emissions_by_tenure_abs / df[feature_2].value_counts()

    if feature_1 == "CO2_EMISSIONS_CURRENT":

        emissions_by_tenure_rel.plot(kind="bar", color="lightseagreen")
        plt.title("CO2 Emissions by Tenure Type (%)")
        plt.ylabel(
            "CO2 Emissions (%)\n(total of {}k tonnes/year)".format(
                str(round(total_wales_emissions, 0))[:-3]
            )
        )

        ax = plt.gca()
        for i, cty in enumerate(emissions_by_tenure_rel.values):
            ax.text(i, cty + 2, str(round(cty, 1)) + "%", horizontalalignment="center")

        ax.set_ylim([0.0, 80.0])
        plt.xticks(rotation=0)
        plt.xlabel("")
        plt.tight_layout()
        plt.savefig(FIG_PATH + "CO2 Emissions by Tenure Type Wales (%)")
        plt.show()

        emissions_by_tenure_mean.plot(kind="bar", color="lightseagreen")
        plt.title("Mean CO2 Emissions by IMD Decile")
        plt.ylabel("Mean CO2 Emissions")

        ax = plt.gca()
        for i, cty in enumerate(emissions_by_tenure_mean.values):
            ax.text(i, cty + 0.1, str(round(cty, 1)), horizontalalignment="center")

        ax.set_ylim([0.0, 6])
        plt.xticks(rotation=0)
        plt.xlabel("")
        plt.tight_layout()
        plt.savefig(FIG_PATH + "Mean CO2 Emissions by IMD Decile Wales (%)")
        plt.show()

        emissions_by_tenure_abs.plot(kind="bar", color="lightseagreen")
        ax = plt.gca()
        plt.title("CO2 Emissions by IMD Decile")
        plt.ylabel("CO2 Emissions\n[tonnes/year]")

        ylabels = ["{:.0f}".format(x / 1000) + "k" for x in ax.get_yticks()]
        ax.set_yticklabels(ylabels)

        for i, cty in enumerate(emissions_by_tenure_abs.values):
            ax.text(
                i, cty + 50000, str(int(cty / 1000)) + "k", horizontalalignment="center"
            )

        ax.set_ylim([0.0, 3000000])
        plt.xticks(rotation=0)
        plt.xlabel("")

        plt.tight_layout()
        plt.savefig(FIG_PATH + "CO2 Emissions by IMD Decile Wales (absolute)")
        plt.show()

        n_dwellings = df.shape[0]
        emission_by_dwelling.plot(kind="bar", color="lightseagreen")

        plt.title("CO2 Emissions by IMD Decile per Dwelling")
        plt.ylabel("CO2 Emissions\n[tonnes/year/dwelling]")

        ax = plt.gca()

        for i, cty in enumerate(emission_by_dwelling.values):
            ax.text(i, cty + 0.1, round(cty, 1), horizontalalignment="center")

        ylabels = ["{:.0f}".format(x) for x in ax.get_yticks()]
        ax.set_yticklabels(ylabels)
        plt.xticks(rotation=0)
        ax.set_ylim([0.0, 6])

        plt.tight_layout()
        plt.savefig(FIG_PATH + "CO2 Emissions by IMD Decile Wales per dwelling")

    elif feature_1 == "CO2_EMISS_CURR_PER_FLOOR_AREA":

        emissions_by_tenure_rel.plot(kind="bar", color="lightseagreen")
        plt.title("CO2 Emissions per Floor Area by IMD Decile (%)")
        plt.ylabel(
            "CO2 Emissions (%) [kg/m²]".format(
                str(round(total_wales_emissions, 0))[:-3]
            )
        )

        ax = plt.gca()
        for i, cty in enumerate(emissions_by_tenure_rel.values):
            ax.text(i, cty + 2, str(round(cty, 1)) + "%", horizontalalignment="center")

        ax.set_ylim([0.0, 75])
        plt.xticks(rotation=0)
        plt.xlabel("")
        plt.tight_layout()
        plt.savefig(FIG_PATH + "CO2 Emissions per Floor Area by IMD Decile Wales (%)")
        plt.show()

        emissions_by_tenure_abs.plot(kind="bar", color="lightseagreen")
        ax = plt.gca()

        for i, cty in enumerate(emissions_by_tenure_abs.values):
            ax.text(
                i,
                cty + 250000,
                str(int(cty / 1000)) + "k",
                horizontalalignment="center",
            )

        ylabels = ["{:.0f}".format(x / 1000) + "k" for x in ax.get_yticks()]
        ax.set_yticklabels(ylabels)
        plt.xticks(rotation=0)
        plt.xlabel("")

        plt.title("CO2 Emissions per Floor Area by IMD Decile")
        plt.ylabel("CO2 Emissions (%) [kg/m²]")

        plt.tight_layout()
        plt.savefig(
            FIG_PATH + "CO2 Emissions per Floor Area by IMD Decile Wales (absolute)"
        )
        plt.show()

    else:
        print("Not implemented")
