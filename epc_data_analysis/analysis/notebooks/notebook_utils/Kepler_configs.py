import yaml
from epc_data_analysis import get_yaml_config, Path, PROJECT_DIR

# Load config file
config = get_yaml_config(Path(str(PROJECT_DIR) + "/epc_data_analysis/config/base.yaml"))

# Load Kepler configs
KEPLER_OUTPUT_PATH = str(PROJECT_DIR) + config["KEPLER_OUTPUT_PATH"]
KEPLER_CONFIG_FILE_PATH = str(PROJECT_DIR) + config["KEPLER_CONFIG_PATH"]
KEPLER_CONFIG_FILE = str(PROJECT_DIR) + config["KEPLER_CONFIG_FILE"]


def get_Kepler_config():
    """Return Kepler config in yaml format."""

    with open(KEPLER_CONFIG_FILE, "r") as infile:
        config = infile.read()
        config = yaml.load(config, Loader=yaml.FullLoader)

    return config
