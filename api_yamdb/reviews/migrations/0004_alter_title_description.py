# Generated by Django 3.2 on 2024-11-03 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20241103_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='description',
            field=models.TextField(blank=True, default=1, verbose_name='Описание'),
            preserve_default=False,
        ),
    ]
