# Generated by Django 3.1.5 on 2021-04-17 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0002_preference_n'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='history',
            name='movie',
        ),
        migrations.AddField(
            model_name='history',
            name='movie_id',
            field=models.IntegerField(default=1),
        ),
    ]
