# EPC_data_analysis

### **Analysis of the EPC dataset**

You can use this repository to faciliate the analysis of the EPC dataset.

### **Example Application: Wales**

As a first application, we analysed the **CO2 emissions and housing energy efficiency of properties in Wales**, with a special focus on differences **across sectors** (social rental, private rental and owner-occupied). The full report can be found [here](https://docs.google.com/document/d/1F-1_5ZZal20pfOWwBaQ-6scv-p4oxDkUdR62ADFJyF4/edit?usp=sharing). Have a look at the following Jupyter Notebooks in this directory `EPC_data_analysis/analysis/notebooks/`:

- [General Wales EPC Analysis](https://github.com/nestauk/EPC_data_analysis/blob/dev/epc_data_analysis/analysis/notebooks/Wales_EPC_IMD_Analysis.ipynb)
- [Visualisation with Kepler](https://github.com/nestauk/EPC_data_analysis/blob/dev/epc_data_analysis/analysis/notebooks/Wales_EPC_IMD_Analysis_with_Kepler.ipynb)

You can check out some EPC visualisations [here](https://athrado.github.io/data_viz/).

### **Data**

You can find and download the entire EPC dataset from [here](https://epc.opendatacommunities.org/).

### Ongoing and Future Work

- [ ] Analysis on the entire UK

- [ ] Cleaning of EPC free text features

- [ ] Kepler Visualisation: Normalisation by density

- [ ] Integration of data from different years

- [ ] And much more...

### Setup

**Before getting started**, meet the data science cookiecutter [requirements](http://nestauk.github.io/ds-cookiecutter/quickstart), in brief:

- Install: `git-crypt` and `conda`

- Have a Nesta AWS account configured with `awscli`

```bash
# Get the repository
$ git clone https://github.com/nestauk/EPC_data_analysis.git

# Setup
$ cd EPC_data_analysis
$ make install
$ conda activate epc_data_analysis

# Prepare input data
$ make inputs-pull
$ unzip "inputs/EPC_data/all-domestic-certificates.zip" -d inputs/EPC_data/.

# If Kepler.gl is required
$ pip install keplergl
```
