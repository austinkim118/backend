# Generated by Django 4.2.7 on 2023-12-04 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotifytoken',
            name='user',
            field=models.TextField(unique=True),
        ),
    ]