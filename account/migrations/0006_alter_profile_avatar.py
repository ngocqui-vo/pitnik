# Generated by Django 4.2 on 2024-10-25 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_alter_profile_avatar_alter_profile_background_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='avatars/default.png', upload_to='avatars/'),
        ),
    ]