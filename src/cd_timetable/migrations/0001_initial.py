# Generated by Django 3.2.8 on 2021-12-02 15:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cd_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lecture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(null=True, verbose_name='Vorlesungstermin')),
                ('start_time', models.TimeField(null=True, verbose_name='Vorlesungsbeginn')),
                ('end_time', models.TimeField(null=True, verbose_name='Vorlesungsende')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Kommentar')),
                ('lecturer', models.ForeignKey(limit_choices_to={'role': 'Lec'}, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Dozent')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cd_core.module', verbose_name='Modul')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cd_core.room', verbose_name='Raum')),
                ('seminargroup', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='cd_core.seminargroup', verbose_name='Seminargruppe')),
            ],
            options={
                'verbose_name': 'Vorlesung',
                'verbose_name_plural': 'Vorlesungen',
            },
        ),
    ]
