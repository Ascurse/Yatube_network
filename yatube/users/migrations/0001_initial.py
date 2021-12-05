# Generated by Django 2.2.9 on 2021-11-09 15:40

from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, validators=[users.validators.validate_not_empty])),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(max_length=100)),
                ('body', models.TextField(validators=[users.validators.validate_not_empty])),
                ('is_answered', models.BooleanField(default=False)),
            ],
        ),
    ]
