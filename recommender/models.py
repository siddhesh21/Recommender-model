from django.db import models
from django.utils import timezone

class History(models.Model):
    
    user = models.CharField(unique = False, max_length = 100, db_index=True, default='')
    movie_id = models.IntegerField(default=1)
    date_updated = models.DateTimeField(default=timezone.now)


class Preference(models.Model):
    
    user = models.CharField(unique = False, max_length = 100, db_index=True, default='')
    genre = models.CharField(unique = False, max_length = 100, db_index=True, default='')
    n = models.IntegerField(default=1)


