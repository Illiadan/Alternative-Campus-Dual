# Generated by Django 3.2.8 on 2021-12-02 15:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageBox',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('posted', models.DateTimeField(auto_now_add=True, null=True, verbose_name='veröffentlicht')),
                ('lastEdited', models.DateTimeField(auto_now=True, null=True, verbose_name='zuletzt bearbeitet')),
                ('title', models.CharField(max_length=100, null=True, verbose_name='Titel')),
                ('message', models.TextField(max_length=250, null=True, verbose_name='Nachricht')),
                ('readableByStudents', models.BooleanField(default=False, verbose_name='lesbar für Studenten')),
                ('readableByLecturers', models.BooleanField(default=False, verbose_name='lesbar für Dozenten')),
                ('readableByOrganisator', models.BooleanField(default=True, editable=False, verbose_name='lesbar für Organisator')),
                ('author', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Verfasser')),
            ],
            options={
                'verbose_name': 'Kurzmitteilung',
                'verbose_name_plural': 'Kurzmitteilungen',
            },
        ),
    ]