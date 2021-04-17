from rest_framework.response import Response
from django.shortcuts import render, redirect
from recommender.models import Preference, History
from recommender.recommender import *
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from rest_framework import views
import pandas as pd
import numpy as np
import ast
import json
import os
import ast
import json


def normalize_preferences(user_preferences):
    try:
        max_value = max(user_preferences.values())
    except:
        return user_preferences
    for key in user_preferences.keys():
        user_preferences[key] = user_preferences[key]/max_value
    return user_preferences


def get_user_preferences(username):
    user_preferences = {}
    preferences = Preference.objects.filter(user=username)
    print(preferences)
    for preference in preferences:
        user_preferences[preference.genre] = preference.n
    user_preferences = normalize_preferences(user_preferences)
    return user_preferences


def get_recent_watches(username, n=5):
    
    #recent = [862]#, 862, 31357, 8844]
    recent = [x.movie_id for x in History.objects.filter(user=username).order_by('-date_updated')]
    recent = recent[:n]
    print("Recent Movies: ", recent)
    return recent
    

def get_movie(movie_id):
    record = df.loc[df["id"]==movie_id]
    name = record["original_title"]
    poster_path = record["poster_path"]
    description = record["overview"][:100]

    movie = {"id": str(movie_id),
             "name": list(name)[0],
             "thumbnail" : list(poster_path)[0][1:],
             "overview": list(description)[0]}

    return movie


def get_random_movies(n=5, genres_required = []):

    if(len(genres_required)>0):
        print("Genres: ", genres_required)
        df_temp = df[pd.Series(np.sum(df[genres_required].values, axis=1) > 0)]
    else:
        df_temp = deepcopy(df)
    df_temp = df_temp[["id", "original_title", "popularity"]]
    df_temp = df_temp.sort_values(by="popularity", ascending=False)
    random_movies = df_temp[:200]["id"].values.ravel()
    random_movies = np.random.choice(random_movies, n)
    return random_movies


class ReccommendationsView(views.APIView):

    def get(self, request):
        
        latest_n = 5
        response = {}

        if True or "username" in request.GET:
            username = request.GET.get("username", "hello")
            genre = request.GET.get("genre", "")
            print(request.GET)
            n = int(request.GET.get("n", 5))

            print("Recommendation for user {} and genre {}".format(username, genre))
            print("n =",n)
            recent_movies = get_recent_watches(username, latest_n)
            user_preferences = get_user_preferences(username)

            genres_required = [genre]  if(genre in genres) else []
            
            try:
                recommendations = get_user_recommendations(n=n, recent_movies = recent_movies, genres_required = genres_required, user_preferences = user_preferences)
                print("Recommendations Found")
                response["movies"] = [get_movie(movie_id) for movie_id in recommendations["id"].values.ravel()]
                response["success"] = True
                print(recommendations)
            except:
                print("No recommendations found")
                movies = get_random_movies(n=n, genres_required=genres_required)
                response["movies"] = [get_movie(movie_id) for movie_id in movies]
                response["success"] = True
            
                
        return Response(response)


class AddMovieView(views.APIView):

    def get(self, request):
        
        response = {"success": False}

        if "username" in request.GET:
            user = request.GET["username"]
            movie = request.GET.get("movie", "")
            print("Adding movie {} for user {}".format(movie, user))
            try:
                movie_id = int(movie)
                try:
                    record = df[df["id"] == movie_id]
                    print(int(record["id"].values[0]))
                    movie_id = int(record["id"].values[0])
                    response["success"] = True
                    print("Adding movie id: ", movie_id)
                    try:
                        record = History.objects.get(user=user, movie_id = movie_id)
                    except:
                        record = History.objects.create(user=user, movie_id = movie_id)
                    record.date_updated = timezone.now()
                    record.save()
                except Exception as e:
                    response["success"] = False
                    response["message"] = str(e)
            except:
                pass
                #try:
                #    record = df[df["original_title"] == movie]
                #    movie_id = int(record["id"][0])
                #    response["success"] = True
                #    print("Adding movie id: ", movie_id)
                #except Exception as e:
                #    response["success"] = False
                #    response["message"] = str(e)

        return Response(response)



class AddPreferenceView(views.APIView):


    def get(self, request):
        
        response = {"success": False}
        if "username" in request.GET:
            user = request.GET["username"]
            movie = request.GET.get("movie", "")
            print("Adding movie genres {} for user {}".format(movie, user))
            try:
                movie_id = int(movie)
                try:
                    record = df[df["id"] == movie_id]
                    print(int(record["id"].values[0]))
                    movie_id = int(record["id"].values[0])
                    response["success"] = True
                    print("Adding preferences movie id: ", movie_id)
                    for genre in genres:
                        if(record[genre].values[0] == 1 ):
                            print("Adding preference for ", genre)
                            try:
                                x = Preference.objects.get(user=user, genre=genre)
                                x.n = x.n + 1
                                x.save()
                            except:
                                Preference.objects.create(user=user, genre=genre)
                except Exception as e:
                    response["success"] = False
                    response["message"] = str(e)
            except:
                pass  


        return Response(response)




#class logUploadView(views.APIView):
#
#	def post(self, request):
#		headers = request.META
#		pprint(headers)
#		response["success"] = verified
#					
#		return Response(response)




