![Project logo](images/banner.png)

# D-Drivers: data-driven serach of traffic drivers | for [EFAHRER.com](https://efahrer.chip.de)

---
### This repo has the sole purpose of showcasing the code base. The dataset is propietary. The scripts will not run without the data. A mock up may be later included in this repo for the demonstration.
---

EFAHRER.com is a media portal focussing on e-mobility and carbon reduction technologies. Their business model includes affiliated marketing. They depend on the user traffic attracted to their articles. 

The aim of this project is to identify the drivers for the web traffic from the available content history, including reverse-engineering the algorithm of some news feed provider (a.k.a. The News Feed).

# Table of contents
* [Slides](slides.pdf)
* [Streamlit app](streamlit_app)
* [Notebooks](notebooks)

# Dataset specification
<details>
<summary>Click to unfold</summary>

<div>
<p>
    
| Column | Description |
| --- | --- |
| ID  | ID of the page in the system. Unique identifier.  |
| DATE | the date on which the metrics per page were grouped.    |
| PUBLISHED_AT | time the actual version of the article was published.    |
| PUBLISH_DATE_EQUAL_TO_DATE  | if the grouping date is the same as a published date.  |
| PAGE_CANONICAL_URL | full and actual URL of the page.    |
| PAGE_NAME | actual page name, full ID and the title.    |
| CLASSIFICATION_PRODUCT | the product to which the page refers. |
| CLASSIFICATION_TYPE | the type of the page. |
| TITLE | title of the page. Page name but without the full ID. |
| PAGE_AUTHOR | author or authors of the article. |
| VIDEO_PLAYER_TYPE | the standard way of video player implementation or widget. |
| DAILY_LIKES | the difference between the number of likes the day before the reported date and the reported date. |
| DAILY_DISLIKES  | the difference between the number of dislikes the day before the reported date and the reported date. |
| WORD_COUNT | number of words on the page. |
| VIDEO_PLAY  | number of times the video on the page was played. |
| IMPRESSIONS | number of times the page was loaded by the user |
| CLICKOUTS | numbers of clicks made on the page that lead to the external resources |
| EXTERNAL_CLICKS |  clicks to the Efahrer page done in The News Feed |
| EXTERNAL_IMPRESSIONS  |  views of the Efahrer page in The News Feed but do not necessarily ended with clicks on them. |

Except for metrics named "external_", others are not distinguished by traffic source. No other filters are used. The data is grouped  by all the above mentioned dimensions. 

The reported period is 01.01.2023 - 23.03.2024.</p>
</div>

</details>

---
# The tech stack
## Data wrangling
* Jupyter notebooks
* `pandas`
## Machine learning
* `sklearn`
* `pycaret`
## Natural language processing 🤗
* Preprocessing (vectorizing, stop words): `nltk`
* Sentiment analysis: [German Sentiment BERT](https://huggingface.co/oliverguhr/german-sentiment-bert) by [Oliver Guhr](https://github.com/oliverguhr)
* Clickbait analysis: [RoBERTa base clickbait](https://huggingface.co/Stremie/roberta-base-clickbait) by [Alberto Martin](https://github.com/Albmargar1)
* Classification: Zero-shot classification with [xlm-roberta-large-xnli](https://huggingface.co/joeddav/xlm-roberta-large-xnli)
---
# Internal
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
1. Have the source tables from the three data deliveries in the `data` folder:
    - `data/data_d-drivers_2024-03-24.xlsx`
    - `data/data_d-drivers_2024-03-26.xlsx`
    - `data/video_players_types_per_article.csv`
2. Obtain other features with the code from the notebooks:
    - `data/data_scraped.csv`
    - `data/clickbait.csv`
    - `data/data_trends_classified.csv`

>Unfortunately, nothing will work if you don't have the data

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

