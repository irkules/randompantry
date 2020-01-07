# Generated by Django 2.2.5 on 2020-01-07 03:50

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True)),
                ('ingredient_ids', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None)),
                ('tag_ids', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None)),
                ('nutrition', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None)),
                ('calorie_level', models.PositiveIntegerField()),
                ('minutes', models.PositiveIntegerField()),
                ('steps', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('img_url', models.TextField(default='https://images.pexels.com/photos/574114/pexels-photo-574114.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField()),
                ('review', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Recipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]