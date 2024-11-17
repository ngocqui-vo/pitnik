# Generated by Django 4.2 on 2024-11-16 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0022_post_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmember',
            name='role',
            field=models.CharField(choices=[('member', 'Member'), ('admin', 'Admin')], default='member', max_length=20),
        ),
    ]
