import yaml
from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR

# Load config file
config = get_yaml_config(Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml"))

# Load Kepler configs
MAPS_OUTPUT_PATH = str(PROJECT_DIR) + config["KEPLER_OUTPUT_PATH"]
MAPS_CONFIG_PATH = str(PROJECT_DIR) + config["KEPLER_MAPS_PATH"]

EPC_WITH_LOC = str(PROJECT_DIR) + config["PREPROC_EPC_WITH_LOC_PATH"]
EPC_DEDUPL_WITH_LOC = str(PROJECT_DIR) + config["PREPROC_EPC_DEDUPL_WITH_LOC_PATH"]


def get_config(path):
    """Return Kepler config in yaml format."""

    with open(path, "r") as infile:
        config = infile.read()
        config = yaml.load(config, Loader=yaml.FullLoader)

    return config


def save_config(map, config_path):

    with open(config_path, "w") as outfile:
        outfile.write(str(map.config))
