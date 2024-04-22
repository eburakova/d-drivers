import os
import pandas as pd
from bs4 import BeautifulSoup
import os
from tqdm import tqdm

print('======== This script scrapes SEO relevant data from downloaded html files ========')

# Initialize i for caching scraped data
i=0

# Path to the folder containing HTML files
folder_path = 'data/pages'

# Initialize a list to hold the scraped data
scraped_data = []

### SCRAPING THE DATA ###

print('Starting the scraping process ...')

# Iterate over HTML files in the folder
for filename in tqdm(os.listdir(folder_path)):
    if filename.endswith('.html') and not filename.endswith('index.html'):  # Check if the file is an HTML file
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract meta data
                url = soup.find('link', {'rel':'canonical'}).get('href')
                meta_title = soup.find('title').text
                meta_description = soup.find('meta', attrs={'name': 'description'}).get('content')
                meta_image_url = soup.find('meta', attrs={'property': 'og:image'}).get('content')

                # Extract media type
                media_type = soup.find('h4', class_='mt-0 credentials open-sans-regular').find_next('div').get('class')
                # media_type_class = media_type_element.get('class') if media_type_element else None
                # media_type = 'img' if 'img-wrapper' in media_type_class else 'video' if 'mb-3 video-player recobar' in media_type_class else None

                # Extract image size
                page_img_size = None
                if 'img-wrapper' in media_type or ['image-gallery', 'mb-lg-7', 'mb-8'] in media_type:
                    page_img_size = soup.find(id='content').find('article').find('div', {'class':'img-wrapper'}).find('img').get('sizes')

                # Extract user-visible data
                h1 = soup.find('h1').text
                author = soup.find(id='content').find('article').find('h4').find('a').text
                date = soup.find(id='content').find('article').find('h4').find('span').text
                abstract = soup.find(id='content').find('article').find('p').get_text(separator=' ', strip=True)
                # removing line breaks
                # abstract = 
                main_article = soup.find('article', class_='single-article')
                if main_article:
                    # Extract the text content of the main text body
                    main_text = main_article.get_text(separator=' ', strip=True)
                    # Calculate the length of the main text body
                    main_text_length = len(main_text.split())
                else:
                    print(f"{filename}: Main text body element not found.")

                # Append scraped data to the list
                scraped_data.append({
                    'filename': filename,                     
                    'url': url,
                    'meta_title': meta_title,
                    'meta_description': meta_description,
                    'meta_image_url': meta_image_url,
                    'media_type': media_type,
                    'page_img_size': page_img_size,
                    'h1': h1,
                    'author': author,
                    'date_scraped': date,
                    'abstract': abstract,
                    'main_text_length': main_text_length
                })

            i+=1
            if i==10000:
                scraped_df = pd.DataFrame(scraped_data)
                scraped_df.to_csv('data/temp_scraped.csv')
                i=0
                print('Scraping progress cached')

        except Exception as e:
            print(f"Error processing file: {file_path}, {e}")

# Convert the list of dictionaries to a DataFrame
scraped_df = pd.DataFrame(scraped_data)

print('Scraping completed')

### BEAUTIFYING THE DATA ###

# Extract page_ID out of filename
scraped_df['page_id'] = scraped_df['filename'].apply(lambda x: x.split('.')[0])
scraped_df.drop('filename', axis=1, inplace=True)

# Get rid of '- EFAHRER.com' at the end of each title
scraped_df['meta_title'] = scraped_df['meta_title'].apply(lambda x: x.rsplit('-', 1)[0])

# Clean data
scraped_df = scraped_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Extract img size number
scraped_df['page_img_size'] = scraped_df['page_img_size'].apply(lambda x: x.split(',')[0] if x else None)
scraped_df['page_img_size'] = scraped_df['page_img_size'].apply(lambda x: x.split(')')[-1] if x else None)

# Reorder columns
scraped_df = scraped_df[['page_id','url','h1','author','date_scraped','abstract','main_text_length','meta_title','meta_description','meta_image_url','media_type','page_img_size']]

print('Saving final csv as data/df_scraped.csv')

# Write the DataFrame to a CSV file
scraped_df.to_csv('data/data_scraped.csv', index=False, lineterminator='')

print('======== Processing complete ========')
