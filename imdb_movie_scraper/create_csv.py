import pandas as pd

class CreateCsvFile:

    columns = ['title', 'year']

    def __init__(self, data):
        self.data = data
        self.create_dataframe_from_data(self.data)

    def create_dataframe_from_data(self, data):
        df = pd.DataFrame(data, columns = self.columns) 
        df.to_csv('imdb_movie_scraper/test_csv.csv', index=False)