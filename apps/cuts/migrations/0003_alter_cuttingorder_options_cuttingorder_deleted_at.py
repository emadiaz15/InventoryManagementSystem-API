# Generated by Django 5.1.1 on 2024-11-14 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cuts', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cuttingorder',
            options={'ordering': ['-created_at'], 'permissions': [('can_assign_order', 'Can assign a cutting order'), ('can_process_order', 'Can process a cutting order')]},
        ),
        migrations.AddField(
            model_name='cuttingorder',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
