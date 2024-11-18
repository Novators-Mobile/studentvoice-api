# Generated by Django 5.1.1 on 2024-11-18 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pollresult',
            name='question1',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='pollresult',
            name='question2',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='pollresult',
            name='question3',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='pollresult',
            name='question4',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='pollresult',
            name='question5',
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='pollresult',
            name='comment1',
            field=models.CharField(max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='pollresult',
            name='comment2',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]
