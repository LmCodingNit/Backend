# Generated by Django 5.2.3 on 2025-07-01 18:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('startups', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('audience', models.TextField()),
                ('niche', models.TextField()),
                ('problem', models.TextField()),
                ('solution', models.TextField()),
                ('startup', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='report', to='startups.startup')),
            ],
        ),
    ]
