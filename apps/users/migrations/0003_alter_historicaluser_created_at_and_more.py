# Generated by Django 5.1.1 on 2024-10-24 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_historicaluser_created_at_user_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluser',
            name='created_at',
            field=models.DateTimeField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
