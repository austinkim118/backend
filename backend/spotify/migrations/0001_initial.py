# Generated by Django 4.2.7 on 2023-11-23 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SpotifyToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('access_token', models.CharField(max_length=150)),
                ('token_type', models.CharField(max_length=150)),
                ('refresh_token', models.CharField(max_length=50)),
                ('expires_in', models.DateTimeField()),
            ],
        ),
    ]