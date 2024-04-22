#!/bin/bash

# Function to display a message and read user input
function read_choice {
    local message=$1
    local choice
    read -p "$message (yes/no): " choice
    echo $choice
}
choice_scrape=$(read_choice "Do you want to run the scraping script? (Type 'yes' ONLY if you do not have data_scraped.csv yet!)")
choice_sentiment=$(read_choice "Do you want to run the sentiment analysis over all articles all over again? (Type 'yes' ONLY if you do not have data_nlp.csv yet!)")

echo "Updating the requirements..."
pip install -r requirements_dev.txt

if [ "$choice_scrape" == "yes" ]; then
    echo "+++++ Running data scraping script +++++"
    python scripts/2a_get_df_scraped.py
else
    echo "-----> Skipping data scraping"
fi

echo ""
echo "+++++ Combining data deliveries +++++"
python scripts/1_merge_source.py

echo ""
echo "+++++ Aggregating by page_id and date +++++"
python scripts/2b_get_df_aggr.py

echo ""
echo "+++++ Aggregating by page_id +++++"
python scripts/3_page_id_agg.py

echo ""
echo "+++++ Extracting features +++++"
python scripts/4_get_df_features.py

if [ "$choice_sentiment" == "yes" ]; then
    echo "+++++ Running sentiment analysis script +++++"
    python scripts/5_sentiment_analysis.py
else
    echo "-----> Skipping sentiment analysis"
    python scripts/5A_sentiment_merge.py

fi
echo ""
echo "+++++ Prettifying the data segments for the D-Drivers Data App +++++"
python scripts/6_prepare_for_demo.py