# Generated by Django 3.1.4 on 2021-04-11 02:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("gestion_association", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Accueil",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_debut", models.DateField(verbose_name="Date de début")),
                ("date_fin", models.DateField(blank=True, verbose_name="Date de fin")),
                ("commentaire", models.CharField(blank=True, max_length=1000)),
                (
                    "animaux",
                    models.ManyToManyField(
                        to="gestion_association.Animal", verbose_name="Animal(aux)"
                    ),
                ),
                (
                    "famille",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="gestion_association.famille",
                    ),
                ),
            ],
        ),
    ]
