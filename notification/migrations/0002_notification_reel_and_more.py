# Generated by Django 5.0.6 on 2024-09-10 13:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
        ('post', '0006_reel_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='reel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_reel', to='post.reel'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_types',
            field=models.IntegerField(blank=True, choices=[(1, 'Like'), (2, 'Comment'), (3, 'Follow'), (4, 'Reel Like')], null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_post', to='post.post'),
        ),
    ]
