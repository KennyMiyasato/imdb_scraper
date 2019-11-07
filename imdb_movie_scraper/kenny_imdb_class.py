import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from imdb_movie_scraper import config


class IMDB:
    # List of static variables
    columns = ['title', 'year', 'rating', 'movie_poster_str', 'movie_summary', 'user_rating_count', 'user_review_count', 'critic_review_count', 'movie_mpaa_rating',
               'movie_runtime', 'movie_genres', 'movie_release_date', 'box_office_gross_domestic', 'box_office_gross_intl', 'url']
    remove_duplicates_csv_filename = 'kenny_master_list_no_dupes.csv'
    sleep_timer_for_scraping_site = .10
    db_name = 'movies'
    db_table = 'movies_imdb'

    cnx = mysql.connector.connect(
        host=config.host,
        user=config.user,
        passwd=config.password,
        database=db_name,
        buffered=True
    )

    cursor = cnx.cursor()

    def __init__(self, df_of_csv_file='imdb_movie_scraper/test_csv.csv'):
        if df_of_csv_file is None:
            self.df_of_csv_file = None
        else:
            self.df_of_csv_file = df_of_csv_file

        self.create_dict_to_store_titles_urls()
        self.tuples_from_site_scraping = self.return_tuples_from_site_scraping(
            self.dict_titles_urls)
        self.data_ready_for_db_export = self.remove_duplicates()

    def __repr__(self):
        # return f'{self.df_of_csv_file}'
        # return f'{self.tuples_from_site_scraping}'
        return f'{self.data_ready_for_db_export}'

    @staticmethod
    def scrape_imdb_for_url_link(title, year):
        title_first_letter = title[0].lower()
        title_lowercase = title.lower().replace(" ", "_").replace(
            "(", "_").replace(")", "").replace("__", "_")[:20]

        # IMDB's JSON is finicky with these
        if title == 'Super Monsters Save Halloween' or title == 'Vampyr':
            imdb_direct_url = "--"
            return imdb_direct_url

        url = f'https://v2.sg.media-imdb.com/suggestion/{title_first_letter}/{title_lowercase}.json'
        response = requests.get(url)
        data = response.json()

        imdb_unique_movie_id = 0

        try:
            while imdb_unique_movie_id == 0:
                for index in range(0, len(data['d'])):
                    if (
                        data['d'][index]['id'].startswith('tt') and
                        data['d'][index]['y'] == int(year) or
                        data['d'][index]['y'] == int(year)+1 or
                        data['d'][index]['y'] == int(year)-1 or
                        data['d'][index]['y'] == int(year)+2 or
                        data['d'][index]['y'] == int(year)-2
                    ):
                        imdb_unique_movie_id = data['d'][index]['id']
                        imdb_unique_movie_id += 1
                    else:
                        imdb_unique_movie_id = "--"
        except Exception as e:
            imdb_direct_url = None

        if imdb_unique_movie_id != "--":
            imdb_direct_url = f'https://www.imdb.com/title/{imdb_unique_movie_id}/'
        else:
            imdb_direct_url = "--"

        if imdb_direct_url == "https://www.imdb.com/title/0/":
            imdb_direct_url = "--"

        return imdb_direct_url

    # @classmethod
    # def create_dict_to_store_titles_urls(cls, df_list_movies=None):
    #     if df_list_movies is None:
    #         df_list_movies = []
    #     else:
    #         df_list_movies = df_list_movies

    #     dict_titles_urls = {}
    #     for index in range(0, len(df_list_movies)):
    #         title = df_list_movies['title'][index]
    #         year = df_list_movies['year'][index]
    #         dict_titles_urls[title] = cls.scrape_imdb_for_url_link(title, year)
    #         print(f'index: {index}   title: {title}   year: {year}')
    #         print(dict_titles_urls[title])
    #         print()
    #         time.sleep(self.sleep_timer_for_scraping_site)
    #     return dict_titles_urls

    def create_dict_to_store_titles_urls(self):

        self.dict_titles_urls = {}
        for index in range(0, len(self.df_of_csv_file)):
            title = self.df_of_csv_file['title'][index]
            year = self.df_of_csv_file['year'][index]
            self.dict_titles_urls[title] = self.scrape_imdb_for_url_link(
                title, year)
            print(f'index: {index}   title: {title}   year: {year}')
            print(self.dict_titles_urls[title])
            print()
            time.sleep(self.sleep_timer_for_scraping_site)
        return self.dict_titles_urls

    @staticmethod
    def imdb_single_site_scrape(url):

        if url == "https://www.imdb.com/title/0/" or url == "--":
            print("--")
            return

        page = requests.get(url)
        soup1 = BeautifulSoup(page.content, 'html.parser')

        imdb_movie_details = soup1.find('div', class_='heroic-overview')
        imdb_movie_details_bottom = soup1.find('div', {'id': 'titleDetails'})

        movie_title = imdb_movie_details.find('h1').text
        regexd_movie_title_search = re.search(
            "([a-z,\- '.\d])+", movie_title, flags=re.I)
        regexd_movie_title = regexd_movie_title_search.group(0)
        print(f'Movie Name: {regexd_movie_title}')

        movie_year = imdb_movie_details.find('h1').text
        regexd_movie_year_search = re.search("\d{4}", movie_year)
        regexd_movie_year = regexd_movie_year_search.group(0)
        print(f'Movie Year: {regexd_movie_year}')

        movie_rating = imdb_movie_details.find(
            'div', class_='ratingValue').span.text
        print(f'Movie Rating: {movie_rating}')

        movie_poster = imdb_movie_details.find('div', class_='poster').img
        movie_poster_str = str(movie_poster).split(
            '=')[2].replace(' title', '').replace('"', '')
        print(movie_poster)
        print(f'Movie Poster: {movie_poster_str}')

        movie_summary = imdb_movie_details.find('div', class_='summary_text').text.strip()
        print(f'Plot Summary: {movie_summary}')

        movie_user_rating_count = imdb_movie_details.find(
            'div', class_='imdbRating').a.text.replace(",", "")
        print(f'Movie User Rating Count: {movie_user_rating_count}')

        movie_user_review_count = imdb_movie_details.find(
            'div', class_='titleReviewbarItemBorder').span.text.strip().replace(",", "")
        regexd_movie_user_review_count_search = re.search(
            "^\d+ user", movie_user_review_count, flags=re.M)
        regexd_movie_user_review_count = regexd_movie_user_review_count_search.group(
            0).replace(" user", "")
        print(f'Movie User Review Count: {regexd_movie_user_review_count}')

        regexd_movie_critic_review_count_search = re.search(
            "^\d+ critic", movie_user_review_count, flags=re.M)
        regexd_movie_critic_review_count = regexd_movie_critic_review_count_search.group(
            0).replace(" critic", "")
        print(f'Movie Critic Review Count: {regexd_movie_critic_review_count}')

        movie_mpaa_rating = imdb_movie_details.find(
            'div', class_='subtext').text.split("|")[0].strip()
        print(f'Movie MPAA Rating: {movie_mpaa_rating}')

        movie_genres = imdb_movie_details.find(
            'div', class_='subtext').text.split("|")
        movie_genres_str = movie_genres[2].strip().replace('\n', '')
        print(f'Movie Genres: {movie_genres_str}')

        movie_release_date = imdb_movie_details.find(
            'div', class_='subtext').text.split("|")[-1].strip()
        movie_release_date_str = movie_release_date.replace(
            "TV Movie ", '').replace("TV Short ", '').replace("Video ", '')
        print(f'Movie Release Date: {movie_release_date_str}')

        try:
            imdb_movie_runtime = imdb_movie_details_bottom.find(
                'time').text.strip().replace(" min", "")
        except Exception as e:
            imdb_movie_runtime = "--"
        print(f'Movie Runtime: {imdb_movie_runtime}')

        try:
            movie_box_office_gross_domestic = imdb_movie_details_bottom.select_one(
                'div:nth-child(14)').text.strip()
            regexd_box_office_gross_domestic_search = re.search(
                "\d.[^']+", movie_box_office_gross_domestic)
            regexd_box_office_gross_domestic = regexd_box_office_gross_domestic_search.group(
                0).replace(",", "")
            if 'min' in regexd_box_office_gross_domestic:
                regexd_box_office_gross_domestic = "--"
        except Exception as e:
            regexd_box_office_gross_domestic = "--"
        print(
            f'Movie Box Office Domestic Gross: {regexd_box_office_gross_domestic}')

        try:
            movie_box_office_gross_intl = imdb_movie_details_bottom.select_one(
                'div:nth-child(15)').text.strip()
            regexd_box_office_gross_intl_search = re.search(
                "\d.[^']+", movie_box_office_gross_intl)
            regexd_box_office_gross_intl = regexd_box_office_gross_intl_search.group(
                0).replace(",", "")
            if 'min' in regexd_box_office_gross_intl:
                regexd_box_office_gross_intl = "--"
        except Exception as e:
            regexd_box_office_gross_intl = "--"
        print(f'Movie Box Office Int Gross: {regexd_box_office_gross_intl}')

        return (regexd_movie_title, regexd_movie_year, 
                movie_rating, movie_poster_str, movie_summary, movie_user_rating_count,
                regexd_movie_user_review_count, regexd_movie_critic_review_count,
                movie_mpaa_rating, imdb_movie_runtime,
                movie_genres_str, movie_release_date_str,
                regexd_box_office_gross_domestic, regexd_box_office_gross_intl, url)

    # @classmethod
    # def return_tuples_from_site_scraping(cls, dict_titles_urls=None):
    #     if dict_titles_urls is None:
    #         dict_titles_urls = {}
    #     else:
    #         dict_titles_urls = dict_titles_urls

    #     list_tuples_movie_info = []
    #     counter = 0
    #     for url in dict_titles_urls.values():
    #         if url == "--":
    #             continue
    #         else:
    #             print(counter)
    #             list_tuples_movie_info.append(cls.imdb_single_site_scrape(url))
    #             time.sleep(self.sleep_timer_for_scraping_site)
    #             print()
    #             counter += 1

    #     return list_tuples_movie_info

    def return_tuples_from_site_scraping(self, dict_titles_urls):

        list_tuples_movie_info = []
        counter = 0
        for url in dict_titles_urls.values():
            if url == "--":
                continue
            else:
                print(counter)
                list_tuples_movie_info.append(
                    self.imdb_single_site_scrape(url))
                time.sleep(self.sleep_timer_for_scraping_site)
                print()
                counter += 1

        return list_tuples_movie_info

    def remove_duplicates(self):
        df = pd.DataFrame(self.tuples_from_site_scraping, columns=self.columns)
        df.sort_values("url", inplace=True)
        df.drop_duplicates(subset="url", keep=False, inplace=True)
        df.sort_values("title", inplace=True)
        df.to_csv(
            f"imdb_movie_scraper/{self.remove_duplicates_csv_filename}", index=False)

        with open(f"imdb_movie_scraper/{self.remove_duplicates_csv_filename}") as remove_duplicates:
            self.data_ready_for_db_export = [
                tuple(line) for line in csv.reader(remove_duplicates)]
        self.data_ready_for_db_export.pop(0)

        return self.data_ready_for_db_export

    def save_to_db(self):
        insert_statement = f"""INSERT INTO {self.db_table} (title, year, rating, movie_poster_str, movie_summary,
                                                    user_rating_count, user_review_count, critic_review_count, 
                                                    movie_mpaa_rating, movie_runtime, movie_genres, 
                                                    movie_release_date, box_office_gross_domestic, box_office_gross_intl, 
                                                    url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self.cursor.executemany(
            insert_statement, self.data_ready_for_db_export)
        self.cnx.commit()
        print(
            f"Successfully added to database: '{self.db_name}' on table: '{self.db_table}'")
