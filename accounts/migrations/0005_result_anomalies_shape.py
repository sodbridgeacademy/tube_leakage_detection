# Generated by Django 4.2.4 on 2023-09-06 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_result"),
    ]

    operations = [
        migrations.AddField(
            model_name="result",
            name="anomalies_shape",
            field=models.CharField(max_length=10, null=True),
        ),
    ]
