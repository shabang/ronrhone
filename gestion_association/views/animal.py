
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.views.generic import CreateView, UpdateView
from rest_framework import viewsets
from django.utils import timezone


from gestion_association.forms import PreferenceForm
from gestion_association.forms.animal import (
    AnimalCreateForm,
    AnimalInfoUpdateForm,
    AnimalOtherInfosForm,
    AnimalSanteUpdateForm,
    AnimalSearchForm, AnimalSelectForm, ParrainageForm,
)
from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import Animal, AnimalGroup, statuts_association, Parrainage
from gestion_association.models.person import Person
from gestion_association.serializers import AnimalSerializer


@login_required()
def search_animal(request):
    animals = Animal.objects.filter(inactif=False).all()
    selected = "animals"
    title = "Liste des animaux"

    if request.method == "POST":
        form = AnimalSearchForm(request.POST)
        if form.is_valid():
            base_url = reverse('animals')
            query_string = form.data.urlencode()
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)

    else:
        form = AnimalSearchForm()
        nom_form = request.GET.get("nom", "")
        identification_form = request.GET.get("identification", "")
        sterilise_form = request.GET.get("sterilise", "")
        perimetre_form = request.GET.get("perimetre", "")
        sans_fa_form = request.GET.get("sans_fa", "")
        nekosable_form = request.GET.get("nekosable", "")
        statuts_form = request.GET.getlist("statuts","")
        date_naissance_min = request.GET.get("date_naissance_min", "")
        date_naissance_max = request.GET.get("date_naissance_max", "")
        date_arrivee_min = request.GET.get("date_arrivee_min", "")
        date_arrivee_max = request.GET.get("date_arrivee_max", "")
        date_prochain_vaccin_min = request.GET.get("date_prochain_vaccin_min", "")
        date_prochain_vaccin_max = request.GET.get("date_prochain_vaccin_max", "")
        date_vermifuge_min = request.GET.get("date_vermifuge_min", "")
        date_vermifuge_max = request.GET.get("date_vermifuge_max", "")
        fiv_felv_form = request.GET.get("fiv_felv", "")
        # Pas dans le formulaire uniquement critère d'url provenant du tableau de bord
        vaccin_ok_url = request.GET.get("vaccin_ok", "")
        identifie_url = request.GET.get("identifie", "")
        soin_manquant_url = request.GET.get("soin_manquant", "")

        if vaccin_ok_url:
            animals = animals.filter(vaccin_ok=vaccin_ok_url)
        if identifie_url and identifie_url == OuiNonChoice.OUI.name:
            animals = animals.exclude(identification__exact="")
        if soin_manquant_url:
            today = timezone.now().date()
            interval_5_months_ago = today - relativedelta(months=5)
            animals = animals.filter(statut__in=statuts_association) \
                .filter(Q(Q(sterilise=OuiNonChoice.NON.name)&Q(date_naissance__lte=interval_5_months_ago))| Q(vaccin_ok=OuiNonChoice.NON.name) | \
                        Q(fiv='NT') | Q(felv='NT') | Q(identification__exact=''))
        if nom_form:
            animals = animals.filter(nom__icontains=nom_form)
            form.fields["nom"].initial = nom_form
        if identification_form:
            animals = animals.filter(identification__icontains=identification_form)
            form.fields["identification"].initial = identification_form
        if sterilise_form:
            animals = animals.filter(sterilise=sterilise_form)
            form.fields["sterilise"].initial = sterilise_form
        if perimetre_form:
            animals = animals.filter(perimetre=perimetre_form)
            form.fields["perimetre"].initial = perimetre_form
        if sans_fa_form:
            form.fields["sans_fa"].initial = sans_fa_form
            if sans_fa_form == OuiNonChoice.OUI.name:
                animals = animals.filter(famille__isnull=True)
            if sans_fa_form == OuiNonChoice.NON.name:
                animals = animals.filter(famille__isnull=False)
        if nekosable_form:
            form.fields["nekosable"].initial = nekosable_form
            if nekosable_form == OuiNonChoice.OUI.name:
                animals = animals.filter(nekosable=True).exclude(famille__neko=True)
            if nekosable_form == OuiNonChoice.NON.name:
                animals = animals.filter(nekosable=False)
        if statuts_form:
            form.fields["statuts"].initial = statuts_form
            animals = animals.filter(statut__in=statuts_form)
        if date_naissance_min:
            form.fields["date_naissance_min"].initial = date_naissance_min
            animals = animals.filter(date_naissance__gte=parse_date(date_naissance_min))
        if date_naissance_max:
            form.fields["date_naissance_max"].initial = date_naissance_max
            animals = animals.filter(date_naissance__lte=parse_date(date_naissance_max))
        if date_arrivee_min:
            form.fields["date_arrivee_min"].initial = date_arrivee_min
            animals = animals.filter(date_arrivee__gte=parse_date(date_arrivee_min))
        if date_arrivee_max:
            form.fields["date_arrivee_max"].initial = date_arrivee_max
            animals = animals.filter(date_arrivee__lte=parse_date(date_arrivee_max))
        if date_prochain_vaccin_min:
            form.fields["date_prochain_vaccin_min"].initial = date_prochain_vaccin_min
            animals = animals.filter(date_prochain_vaccin__gte=parse_date(date_prochain_vaccin_min))
        if date_prochain_vaccin_max:
            form.fields["date_prochain_vaccin_max"].initial = date_prochain_vaccin_max
            animals = animals.filter(date_prochain_vaccin__lte=parse_date(date_prochain_vaccin_max))
        if fiv_felv_form:
            form.fields["fiv_felv"].initial = fiv_felv_form
            if fiv_felv_form == OuiNonChoice.OUI.name:
                animals = animals.exclude(Q(fiv='NT')|Q(felv='NT'))
            if fiv_felv_form == OuiNonChoice.NON.name:
                animals = animals.filter(Q(fiv='NT')|Q(felv='NT'))

    # Pagination : 20 éléments par page
    paginator = Paginator(animals.order_by("-date_mise_a_jour"), 20)
    nb_results = animals.count()
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        animal_list = paginator.page(page)
    except EmptyPage:
        # Si on dépasse la limite de pages, on prend la dernière
        animal_list = paginator.page(paginator.num_pages())

    return render(request, "gestion_association/animal/animal_list.html", locals())

@login_required()
def create_animal(request):
    title = "Créer un animal"
    if request.method == "POST":
        animal_form = AnimalCreateForm(data=request.POST)
        preference_form = PreferenceForm(data=request.POST)
        if animal_form.is_valid() and preference_form.is_valid():
            # Rattachement manuel de l'animal et des préférences
            preference = preference_form.save()
            animal = animal_form.save(commit=False)
            animal.preference = preference
            animal.save()
            return redirect("detail_animal", pk=animal.id)
    else:
        animal_form = AnimalCreateForm()
        preference_form = PreferenceForm()
        id_animal = request.GET.get("animal", "")
        if id_animal:
            animal_to_copy = Animal.objects.get(id=id_animal)
            animal_form.fields["date_naissance"].initial = animal_to_copy.date_naissance
            animal_form.fields["circonstances"].initial = animal_to_copy.circonstances
            animal_form.fields["date_arrivee"].initial = animal_to_copy.date_arrivee
            animal_form.fields["statut"].initial = animal_to_copy.statut
            animal_form.fields["sterilise"].initial = animal_to_copy.sterilise
            animal_form.fields["date_sterilisation"].initial = animal_to_copy.date_sterilisation
            animal_form.fields["type_vaccin"].initial = animal_to_copy.type_vaccin
            animal_form.fields["primo_vaccine"].initial = animal_to_copy.primo_vaccine
            animal_form.fields["fiv"].initial = animal_to_copy.fiv
            animal_form.fields["felv"].initial = animal_to_copy.felv
            animal_form.fields["commentaire_sante"].initial = animal_to_copy.commentaire_sante
            animal_form.fields["ancien_proprio"].initial = animal_to_copy.ancien_proprio
            preference_form.fields["sociabilisation"].initial = animal_to_copy.preference.sociabilisation
            preference_form.fields["exterieur"].initial = animal_to_copy.preference.exterieur
            preference_form.fields["quarantaine"].initial = animal_to_copy.preference.quarantaine
            preference_form.fields["biberonnage"].initial = animal_to_copy.preference.biberonnage
        else :
            preference_form.fields['quarantaine'].initial = OuiNonChoice.OUI.value
    return render(request, "gestion_association/animal/animal_create_form.html", locals())


@login_required()
def update_preference(request, pk):
    animal = Animal.objects.get(id=pk)
    title = "Modification des préférences de " + animal.nom
    if request.method == "POST":
        preference_form = PreferenceForm(data=request.POST, instance=animal.preference)
        animal_other_form = AnimalOtherInfosForm(data=request.POST, instance=animal)
        animal_group_form = AnimalSelectForm(data=request.POST)
        if preference_form.is_valid() and animal_other_form.is_valid() and animal_group_form.is_valid():
            preference_form.save()
            animal_other_form.save()
            set_groups = set([])
            set_animals = set([])
            if animal_group_form.cleaned_data['animaux']:
                new_group = AnimalGroup.objects.create()
                for animal_select in animal_group_form.cleaned_data['animaux']:
                    if animal_select.groupe:
                        set_groups.add(animal_select.groupe)
                    animal_select.groupe = new_group
                    animal_select.save()
                animal.groupe = new_group
                animal.save()
                new_group.save()
            else :
                if animal.groupe:
                    for animal_select in animal.groupe.animal_set.all():
                        if animal_select.groupe:
                            set_groups.add(animal_select.groupe)
                        animal_select.groupe = None
                        animal_select.save()
            for group in set_groups:
                group.delete()

            return redirect("detail_animal", pk=pk)
    else:
        preference_form = PreferenceForm(instance=animal.preference)
        animal_other_form = AnimalOtherInfosForm(instance=animal)
        animal_group_form = AnimalSelectForm()
        animal_group_form.fields['animaux'].queryset = Animal.objects.filter\
            (statut__in=statuts_association).filter(inactif=False).order_by('nom').exclude(id=pk)

    return render(request, "gestion_association/animal/preference_form.html", locals())


class UpdateInformation(LoginRequiredMixin, UpdateView):
    model = Animal
    template_name = "gestion_association/animal/information_form.html"
    form_class = AnimalInfoUpdateForm

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.id})


class UpdateSante(LoginRequiredMixin, UpdateView):
    model = Animal
    template_name = "gestion_association/animal/sante_form.html"
    form_class = AnimalSanteUpdateForm

    def get_success_url(self):
        return reverse_lazy("detail_animal", kwargs={"pk": self.object.id})


class AnimalViewSet(viewsets.ModelViewSet):
    queryset = Animal.objects.filter(inactif=False).all()
    serializer_class = AnimalSerializer


class UpdateParrainage(LoginRequiredMixin, UpdateView):
    model = Parrainage
    form_class = ParrainageForm
    template_name = "gestion_association/person/parrainage_form.html"

    def get_success_url(self):
        return reverse_lazy("detail_person", kwargs={"pk": self.object.personne.id})

    def get_context_data(self, **kwargs):
        context = super(UpdateParrainage, self).get_context_data(**kwargs)
        context['title'] = "Mise à jour du parrainage"
        return context


@login_required
def create_parrainage(request, pk):
    person = Person.objects.get(id=pk)
    title = "Nouveau parrainage pour " + person.prenom + " " + person.nom
    if request.method == "POST":
        form = ParrainageForm(data=request.POST)
        if form.is_valid():
            parrainage = form.save(commit=False)
            parrainage.personne = person
            person.is_parrain = True
            parrainage.save()
            person.save()
            return redirect("detail_person", pk=person.id)

    else:
        form = ParrainageForm()

    return render(request, "gestion_association/person/parrainage_form.html", locals())
