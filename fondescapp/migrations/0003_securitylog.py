# Generated by Django 5.1.7 on 2025-03-16 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fondescapp', '0002_newslettersubscriber'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField()),
                ('query_string', models.TextField(blank=True, null=True)),
                ('url_path', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_blocked', models.BooleanField(default=False)),
            ],
        ),
    ]
