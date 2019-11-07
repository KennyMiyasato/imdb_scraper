import os
from flask import render_template, url_for, flash, redirect, session, request, send_from_directory
from werkzeug.utils import secure_filename
from imdb_movie_scraper import app
from imdb_movie_scraper.forms import Title_Year
from imdb_movie_scraper.kenny_imdb_class import IMDB
from imdb_movie_scraper.random_color import RandomColor
from imdb_movie_scraper.create_csv import CreateCsvFile
from imdb_movie_scraper.models import ImdbTitleYear
import pandas as pd
from random import choice

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = Title_Year()
    if form.validate_on_submit():
        return redirect(url_for('movie_added', title=form.title.data, year=form.year.data))
    return render_template('home.html', form=form)


@app.route('/movie_added')
def movie_added():
    title = request.args.get('title')
    year = request.args.get('year')
    search_movie = [[title, year]]
    create_csv = CreateCsvFile(search_movie)
    df_list_movie = pd.read_csv('imdb_movie_scraper/test_csv.csv')
    imdb = IMDB(df_list_movie)
    df = pd.read_csv('imdb_movie_scraper/kenny_master_list_no_dupes.csv')
    color_choice = RandomColor()
    return render_template('movie_added.html', title=title, year=year, search_movie=search_movie, create_csv=create_csv, imdb=imdb, df=df, color_choice=color_choice)


@app.route('/movies_added')
def movies_added():
    # filename = request.args.get('filename')
    # df_list_movies = pd.read_csv(f'imdb_movie_scraper/uploads/{filename}')
    # imdb = IMDB(df_list_movies)
    df_movies = pd.read_csv('imdb_movie_scraper/kenny_master_list_no_dupes_sample.csv')
    color_choices = RandomColor()
    return render_template('movies_added.html',  df_movies=df_movies, color_choices=color_choices) # imdb=imdb, filename=filename,


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('movies_added', filename=filename))
    return render_template('upload.html')