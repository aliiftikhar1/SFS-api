# Generated by Django 4.2.1 on 2024-01-26 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MusicContentInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('worked', models.BooleanField(default=False)),
                ('released', models.BooleanField(default=False)),
                ('talent', models.CharField(choices=[('Instrumentalist', 'Instrumentalist')], max_length=255)),
                ('daw', models.CharField(choices=[('Pro Tools', 'Protools')], max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('auth_token', models.CharField(blank=True, max_length=1000, null=True)),
                ('profile_picture', models.ImageField(blank=True, default=None, max_length=1000, null=True, upload_to='profile_pics/')),
                ('google_signup', models.BooleanField(default=False)),
                ('usertype', models.CharField(choices=[('Admin', 'Admin'), ('Staff', 'Staff'), ('Member', 'Member'), ('Supplier', 'Supplier')], max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('verified', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AdminOrStaff',
            fields=[
                ('admin_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='adminOrStaff_details', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('member_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='member_details', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('country_or_state', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=1000)),
                ('username', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('complete_residence_address', models.CharField(max_length=1000)),
                ('major_city', models.CharField(max_length=255)),
                ('country_or_state', models.CharField(max_length=255)),
                ('bio', models.CharField(max_length=1000)),
                ('content_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_info_artist', to='User_Management.musiccontentinformation')),
            ],
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('supplier_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='supplier_details', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('contract', models.FileField(blank=True, default=None, null=True, upload_to='contracts/')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='artist_supplier', to='User_Management.artist')),
            ],
        ),
        migrations.CreateModel(
            name='Requests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('status', models.CharField(default='Applied', max_length=20)),
                ('hidden', models.BooleanField(default=False)),
                ('interview_date', models.DateField(blank=True, default=None, null=True)),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request', to='User_Management.supplier')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
