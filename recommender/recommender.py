import pandas as pd
import numpy as np
import ast
from collections import Counter
from django.conf import settings
import os
from copy import deepcopy


movies_file = os.path.join(settings.BASE_DIR, "data", "movies.csv")
columns_file = os.path.join(settings.BASE_DIR, "data","metric_columns.txt")
df = pd.read_csv(movies_file)
df["popularity"] = np.minimum(df["popularity"], 25)
metric_columns = ["id",
                    "popularity",
                    "vote_average",
                    "vote_count",
                    "age",
                    "release_date",
                    "runtime",
                    "adult",
                    "Thriller",
                    "Action",
                    "Family",
                    "GoHands",
                    "Drama",
                    "Crime",
                    "Comedy",
                    "War",
                    "Fantasy",
                    "Horror",
                    "Mystery",
                    "Music",
                    "Foreign",
                    "Adventure",
                    "Romance",
                    "History",
                    "Western",
                    "Animation",
                    "Documentary",
                    "Science Fiction",
                    "language_en",
                    "language_fr",
                    "language_it",
                    "language_ja",
                    "language_de",
                    "language_es",
                    "language_ru",
                    "language_hi",
                    "language_ko",
                    "language_zh",
                    "language_sv",
                    "language_pt",
                    "language_cn",
                    "language_fi",
                    "language_nl",
                    "language_da",
                    "language_pl",
                    "language_tr",
                    "language_cs",
                    "language_el",
                    "language_no",
                    "language_fa",
                    "language_hu",
                    "language_ta",
                    "language_th",
                    "language_he",
                    "language_sr",
                    "language_ro",
                    "language_te",
                    "language_ar",
                    "language_ml",
                    "language_xx",
                    "language_bn",
                    "language_hr",
                    "language_mr",
                    "language_is",
                    "language_et",
                    "language_tl",
                    "language_id",
                    "language_ka",
                    "Paramount Pictures",
                    "Metro-Goldwyn-Mayer (MGM)",
                    "Twentieth Century Fox Film Corporation",
                    "Warner Bros.",
                    "Universal Pictures",
                    "Columbia Pictures",
                    "Columbia Pictures Corporation",
                    "RKO Radio Pictures",
                    "United Artists",
                    "Walt Disney Pictures",
                    "New Line Cinema",
                    "Mosfilm",
                    "Miramax Films",
                    "TriStar Pictures",
                    "Toho Company",
                    "Gaumont",
                    "BBC Films",
                    "Orion Pictures",
                    "Touchstone Pictures",
                    "France 2 Cin??ma",
                    "Fox Searchlight Pictures",
                    "Walt Disney Productions",
                    "Village Roadshow Pictures",
                    "Universal International Pictures (UI)",
                    "British Broadcasting Corporation (BBC)",
                    "Shaw Brothers",
                    "DreamWorks SKG",
                    "Hammer Film Productions",
                    "Channel Four Films",
                    "TLA Releasing",
                    "Lions Gate Films",
                    "First National Pictures",
                    "New World Pictures",
                    "The Rank Organisation",
                    "Nikkatsu",
                    "Canal+",
                    "American International Pictures (AIP)",
                    "Lionsgate",
                    "Regency Enterprises",
                    "Sh??chiku Eiga",
                    "StudioCanal",
                    "Monogram Pictures",
                    "Nordisk Film",
                    "Imagine Entertainment",
                    "Fox Film Corporation",
                    "CJ Entertainment",
                    "Hollywood Pictures",
                    "Summit Entertainment",
                    "Rai Cinema",
                    "United States of America",
                    "United Kingdom",
                    "France",
                    "Canada",
                    "Japan",
                    "Italy",
                    "Germany",
                    "Russia",
                    "India",
                    "Spain",
                    "Australia",
                    "Hong Kong",
                    "South Korea",
                    "Sweden",
                    "Finland",
                    "China",
                    "Belgium",
                    "Denmark",
                    "Brazil",
                    "Poland",
                    "Mexico",
                    "Netherlands",
                    "Argentina",
                    "Czech Republic",
                    "Austria",
                    "Ireland",
                    "Turkey",
                    "Greece",
                    "Norway"]
model_columns = metric_columns[5:]

genres = ['Thriller', 'Action', 'Family', 'Drama', 'Crime', 'Comedy', 'War',  'Fantasy', 'Horror', 'Mystery', 'Music', 
          'Foreign', 'Adventure', 'Romance', 'History', 'Western', 'Animation', 'Documentary', 'Science Fiction']


def similarity_func(metrics):
    all_metrics = df[model_columns].values
    movie_similarity = np.sqrt(np.square(all_metrics - metrics)).sum(axis= 1)
    score = movie_similarity
    return score
    
    
def get_similar_movies(movie_id, n=1, user_preferences={}, max_genre_reward=1, maximum_popularity_reward=1 , max_recency_reward = 0.2, genres_required = []):
    print(n)
    print("Preferences:", user_preferences)
    record = df[df["id"]==movie_id]
    #print(movie_id, n)
    metrics = record[model_columns].values
    if(len(genres_required)>0):
        print("Genres: ", genres_required)
        df_temp = df[pd.Series(np.sum(df[genres_required].values, axis=1) > 0)]
    else:
        df_temp = deepcopy(df)
    df_temp = df_temp.reset_index()
    df_temp = df_temp.reindex() 
    #print(df_temp)
    all_metrics = df_temp[model_columns].values
    movie_similarity = np.sqrt(np.square(all_metrics - metrics)).sum(axis= 1)
    lowest_similarity = movie_similarity[(movie_similarity>-1)==True].max()
    #print(lowest_similarity)
    #print(movie_similarity[(movie_similarity>-1)==False])
    movie_similarity[(movie_similarity>-1)==False] = lowest_similarity
    #print(movie_similarity[(movie_similarity>-1)==False])
    #movie_similarity = (lowest_similarity - movie_similarity)/lowest_similarity  
    
    genre_multiple = 1.0
    for genre in user_preferences.keys():
        wiegth = int(record[genre]) * user_preferences[genre]
        genre_multiple = genre_multiple *  (1 + (max_genre_reward*wiegth) )
    print("Genre Multiple: ", genre_multiple)
    
    def get_recency_metric(x):
        if(str(x).isnumeric()):
            metric = 1 + np.maximum((20-float(x))/20, 0)
        return metric
    
    #recency_multiple = df_temp["age"].apply(get_recency_metric) * max_recency_reward
    recency_multiple = (20.0-df_temp["age"])/20.0
    recency_multiple = np.maximum(recency_multiple, 0)
    recency_multiple = np.minimum(recency_multiple, 1)
    recency_multiple = recency_multiple * max_recency_reward
    recency_multiple = 1 + recency_multiple
    recency_multiple = 1.0
    
    popularity = np.sqrt(df_temp["vote_average"])
    popularity = np.sqrt(df_temp["popularity"])
    popularity_multiple = (popularity.max() - popularity)/popularity.max()
    popularity_multiple = 1 + popularity_multiple * maximum_popularity_reward
    #print(popularity_multiple.describe())
    #print(np.isnan(popularity_multiple).sum())
    #popularity_multiple = 1.0
    #print(recency_multiple.min())
    
    scores = movie_similarity #* recency_multiple * popularity_multiple
    scores = scores #/ genre_multiple
    args = np.argsort(scores)[:n+1]
    #print(args)
    #print(df_temp)
    result = df_temp.loc[args, ["id", "original_title"]]#, "age", "popularity", "vote_average"]]
    result["score"] = scores[args]
    
    #result = result[result["id"]!=movie_id]
    return result



def combine_results(results, n):
    if(len(results)>0):
        #print([x.values.shape for x in results])
        values = np.vstack([x.values for x in results])
        #print(values.shape)
        result = pd.DataFrame(values, columns=results[0].columns)
        
        result = result.drop_duplicates()
        result = result.iloc[np.random.permutation(result.shape[0])[:n]]
    else:
        raise Exception("Not so fast")
    return result

def get_user_recommendations(n = 5, recent_movies = [], genres_required = [], user_preferences = {}):
    print("Recent Movies:", recent_movies)
    results = []
    for movie_id in recent_movies:
        print("Movie: ", movie_id)
        result = get_similar_movies(movie_id, n=n, 
                                    user_preferences = user_preferences,
                                    genres_required = genres_required, 
                                    max_genre_reward = 1.0, 
                                    maximum_popularity_reward = 0.5,   
                                    max_recency_reward = 0.1)
        #print(result)
        #print(result.values.shape)
        results.append(result)
    
    result = combine_results(results, n)
    return result

