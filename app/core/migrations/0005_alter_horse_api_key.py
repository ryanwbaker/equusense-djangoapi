# Generated by Django 3.2.18 on 2023-03-15 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_horse_api_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='horse',
            name='api_key',
            field=models.CharField(default='EZsEIBzieghp', max_length=12, unique=True),
        ),
    ]