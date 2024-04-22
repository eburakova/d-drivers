# D-Drivers: data-driven investigation of traffic drivers

## Setup

Use the requirements file in this repo to create a new environment.

```BASH
make setup

#or

pyenv local 3.11.3
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements_dev.txt
```

The `requirements.txt` file contains the libraries needed for deployment. of model or dashboard - thus no jupyter or other libs used during development.

## Data preprocessing
1. Have the source tables from both data deliveries in the `data` folder:
    - `data/data_d-drivers_2024-03-26.xlsx`
    - `data/data_d-drivers_2024-03-26.xlsx`

Make sure the targets are masked.

2. Find the scraped pages archive `pages.zip` in Slack or on our server; extract it into the `data` folder

3. In the root directory, give permissions to the preprocessing script:
```bash
chmod +x preprocess.sh
```

And (in the root directory) run it:
```bash
./preprocess.sh
```

It will create a bunch of CSVs for all intermediate preprocessing steps

