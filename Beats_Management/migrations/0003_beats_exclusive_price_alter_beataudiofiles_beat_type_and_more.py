# Generated by Django 4.2.1 on 2024-12-09 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Beats_Management', '0002_beatfile_file_extension_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='beats',
            name='exclusive_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='beataudiofiles',
            name='beat_type',
            field=models.CharField(choices=[('Beat', 'Beat')], max_length=25),
        ),
        migrations.AlterField(
            model_name='beatssubmissions',
            name='beat_type',
            field=models.CharField(choices=[('Beat', 'Beat')], default='Beat', max_length=25),
        ),
    ]
