# Generated by Django 4.2.13 on 2024-06-25 19:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.TextField()),
                ('type', models.IntegerField(choices=[(1, 'Megahit'), (2, 'Annotation')])),
                ('status', models.IntegerField(choices=[(1, 'Pending'), (2, 'Success'), (3, 'Failure'), (4, 'Canceled')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='project.project')),
            ],
        ),
    ]
