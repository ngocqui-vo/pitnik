# Generated by Django 4.2 on 2024-11-24 16:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0025_page_pagepost'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='social.page'),
        ),
        migrations.DeleteModel(
            name='PagePost',
        ),
    ]