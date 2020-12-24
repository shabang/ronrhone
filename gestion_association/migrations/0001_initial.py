# Generated by Django 3.0.5 on 2020-12-24 10:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_mise_a_jour', models.DateField(auto_now=True, verbose_name='Date de mise à jour')),
                ('prenom', models.CharField(max_length=30)),
                ('nom', models.CharField(max_length=150)),
                ('email', models.EmailField(error_messages={'unique': 'A user with that username already exists.'}, max_length=150, unique=True)),
                ('adresse', models.CharField(max_length=500)),
                ('code_postal', models.CharField(max_length=5, validators=[django.core.validators.RegexValidator(message='Veuillez entrer un code postal valide.', regex='^[0-9]*$')])),
                ('ville', models.CharField(max_length=100)),
                ('telephone', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(message='Veuillez entrer un numéro de téléphone valide.', regex='[0-9]{10}')])),
                ('date_inscription', models.DateField(auto_now_add=True)),
                ('profession', models.CharField(max_length=250)),
                ('commentaire', models.CharField(blank=True, max_length=1000)),
                ('inactif', models.BooleanField(default=False, verbose_name="Desactivé (Ne cocher que si vous ne souhaitez                                       plus gérer cette personne dans l'application) ")),
                ('is_famille', models.BooleanField(default=False, verbose_name="Famille d'accueil")),
                ('is_adoptante', models.BooleanField(default=False, verbose_name='Adoptante')),
                ('is_benevole', models.BooleanField(default=False, verbose_name='Bénévole')),
                ('commentaire_benevole', models.CharField(blank=True, max_length=1000)),
            ],
        ),
    ]
