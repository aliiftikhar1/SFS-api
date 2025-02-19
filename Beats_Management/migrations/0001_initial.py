# Generated by Django 4.2.1 on 2024-12-05 10:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BeatAudioFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('likes_count', models.IntegerField(default=0)),
                ('downloads_count', models.IntegerField(default=0)),
                ('beat_type', models.CharField(choices=[('mp3', 'Mp3'), ('wav', 'Wav'), ('zip', 'Zip')], max_length=25)),
                ('source', models.CharField(choices=[('Electronic', 'Electronic'), ('Live Recorded', 'Live Recorded')], max_length=25)),
                ('message', models.CharField(blank=True, default=None, max_length=1000, null=True)),
                ('status', models.CharField(choices=[('Uploaded', 'Uploaded'), ('Revise', 'Revise'), ('Revised', 'Revised'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Uploaded', max_length=25)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatBPM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('start_value', models.CharField(max_length=10)),
                ('end_value', models.CharField(max_length=10)),
                ('bpm_type', models.CharField(choices=[('Exact', 'Exact'), ('Range', 'Range')], max_length=25)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatDownloads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(blank=True, default=None, max_length=1000, null=True, upload_to='audio-files/')),
                ('file_name', models.CharField(max_length=1000)),
                ('file_size', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatGenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatInstrument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(choices=[('D#', 'Ds'), ('E#', 'Es'), ('G#', 'Gs'), ('A#', 'As'), ('B#', 'Bs'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'), ('Db', 'Db'), ('Eb', 'Eb'), ('Gb', 'Gb'), ('Ab', 'Ab'), ('Bb', 'Bb'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G')], max_length=10)),
                ('key_scale', models.CharField(choices=[('Minor', 'Minor'), ('Major', 'Major')], max_length=10)),
                ('key_type', models.CharField(choices=[('Flat', 'Flat'), ('Sharp', 'Sharp')], max_length=25)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatMood',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatPlugin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('extension', models.CharField(max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Beats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(default='', max_length=500)),
                ('beats_artwork', models.ImageField(blank=True, default=None, max_length=1000, null=True, upload_to='beats_artworks/')),
                ('downloads_count', models.IntegerField(default=0)),
                ('audio_files', models.ManyToManyField(blank=True, related_name='beats', to='Beats_Management.beataudiofiles')),
                ('demo_file', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='demo', to='Beats_Management.beataudiofiles')),
                ('genre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beats', to='Beats_Management.beatgenre')),
                ('mood', models.ManyToManyField(blank=True, related_name='beats', to='Beats_Management.beatmood')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatSubInstrument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_instrument', to='Beats_Management.beatinstrument')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatSubGenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_genre', to='Beats_Management.beatgenre')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatsSubmissions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('beat_type', models.CharField(choices=[('mp3', 'Mp3'), ('wav', 'Wav'), ('zip', 'Zip')], default='mp3', max_length=25)),
                ('status', models.CharField(choices=[('Uploaded', 'Uploaded'), ('Process', 'Process'), ('Submitted', 'Submitted'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Uploaded', max_length=25)),
                ('approval_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beats_review', to=settings.AUTH_USER_MODEL)),
                ('beat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_submissions', to='Beats_Management.beats')),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beats_submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='beats',
            name='sub_genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beats', to='Beats_Management.beatsubgenre'),
        ),
        migrations.CreateModel(
            name='BeatLikes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('beat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_likes', to='Beats_Management.beats')),
                ('file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_like', to='Beats_Management.beataudiofiles')),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatFileDownloads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('audio_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_downloads', to='Beats_Management.beataudiofiles')),
                ('download', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_files', to='Beats_Management.beatdownloads')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='beatdownloads',
            name='beat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_downloads', to='Beats_Management.beats'),
        ),
        migrations.AddField(
            model_name='beatdownloads',
            name='member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_downloads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='BeatCollections',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_collections', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeatCollectionFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('audio_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_collection_files', to='Beats_Management.beataudiofiles')),
                ('beat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_collection_files', to='Beats_Management.beats')),
                ('collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='beat_collection_files', to='Beats_Management.beatcollections')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='beataudiofiles',
            name='bpm',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audio_files', to='Beats_Management.beatbpm'),
        ),
        migrations.AddField(
            model_name='beataudiofiles',
            name='file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audio_files', to='Beats_Management.beatfile'),
        ),
        migrations.AddField(
            model_name='beataudiofiles',
            name='genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audio_files', to='Beats_Management.beatgenre'),
        ),
        migrations.AddField(
            model_name='beataudiofiles',
            name='instrument',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audio_files', to='Beats_Management.beatinstrument'),
        ),
        migrations.AddField(
            model_name='beataudiofiles',
            name='key',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audio_files', to='Beats_Management.beatkey'),
        ),
        migrations.AddField(
            model_name='beataudiofiles',
            name='mood',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audio_files', to='Beats_Management.beatmood'),
        ),
        migrations.AddField(
            model_name='beataudiofiles',
            name='sub_genre',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audio_files', to='Beats_Management.beatsubgenre'),
        ),
        migrations.AddField(
            model_name='beataudiofiles',
            name='sub_instrument',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audio_files', to='Beats_Management.beatsubinstrument'),
        ),
    ]
