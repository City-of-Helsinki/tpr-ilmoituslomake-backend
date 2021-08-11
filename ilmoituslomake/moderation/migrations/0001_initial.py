# Generated by Django 2.2.17 on 2021-08-11 13:10

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import moderation.models
import moderation.storage
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalModeratedNotification',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('schema', models.IntegerField(default=1)),
                ('revision', models.IntegerField(db_index=True, default=0)),
                ('status', models.CharField(choices=[('created', 'created'), ('modified', 'modified'), ('rejected', 'rejected'), ('approved', 'approved')], db_index=True, default='created', max_length=16)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('created_at', models.DateTimeField(blank=True, db_index=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, db_index=True, editable=False)),
                ('published', models.BooleanField(db_index=True, default=False)),
                ('notification_id', models.IntegerField(default=0)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical moderated notification',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalModeratedNotificationImage',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, null=True)),
                ('filename', models.TextField(blank=True)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField()),
                ('published', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(blank=True, db_index=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, db_index=True, editable=False)),
                ('data', models.TextField(max_length=100)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical moderated notification image',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalModerationItem',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('notification_target_revision', models.IntegerField(default=0)),
                ('target_revision', models.IntegerField(default=0)),
                ('category', models.CharField(choices=[('change_request', 'change_request'), ('moderator_edit', 'moderator_edit'), ('moderation_task', 'moderation_task')], db_index=True, default='change_request', max_length=16)),
                ('item_type', models.CharField(choices=[('change', 'change'), ('add', 'add'), ('delete', 'delete'), ('created', 'created'), ('modified', 'modified')], db_index=True, default='change', max_length=16)),
                ('status', models.CharField(choices=[('open', 'open'), ('in_progress', 'in_progress'), ('closed', 'closed')], db_index=True, default='open', max_length=16)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('user_place_name', models.TextField(blank=True, default='')),
                ('user_comments', models.TextField(default='')),
                ('user_details', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(blank=True, editable=False)),
                ('updated_at', models.DateTimeField(blank=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
            ],
            options={
                'verbose_name': 'historical moderation item',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='ModeratedNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schema', models.IntegerField(default=1)),
                ('revision', models.IntegerField(db_index=True, default=0)),
                ('status', models.CharField(choices=[('created', 'created'), ('modified', 'modified'), ('rejected', 'rejected'), ('approved', 'approved')], db_index=True, default='created', max_length=16)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('published', models.BooleanField(db_index=True, default=False)),
                ('notification_id', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModeratedNotificationImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, null=True)),
                ('filename', models.TextField(blank=True)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField()),
                ('published', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('data', models.ImageField(storage=moderation.storage.PublicAzureStorage(), upload_to=moderation.models.upload_image_to)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModerationItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_target_revision', models.IntegerField(default=0)),
                ('target_revision', models.IntegerField(default=0)),
                ('category', models.CharField(choices=[('change_request', 'change_request'), ('moderator_edit', 'moderator_edit'), ('moderation_task', 'moderation_task')], db_index=True, default='change_request', max_length=16)),
                ('item_type', models.CharField(choices=[('change', 'change'), ('add', 'add'), ('delete', 'delete'), ('created', 'created'), ('modified', 'modified')], db_index=True, default='change', max_length=16)),
                ('status', models.CharField(choices=[('open', 'open'), ('in_progress', 'in_progress'), ('closed', 'closed')], db_index=True, default='open', max_length=16)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('user_place_name', models.TextField(blank=True, default='')),
                ('user_comments', models.TextField(default='')),
                ('user_details', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
