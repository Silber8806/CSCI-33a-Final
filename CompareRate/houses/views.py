from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .forms import SearchForm
from .models import Address


# Create your views here.
@login_required(login_url='/accounts/login')
def zipcode(request):
    search_term = ''
    if request.POST:
        form = SearchForm(request.POST)
        if form.is_valid():
            search_term = form.cleaned_data['search']
    form = SearchForm(initial={'search': search_term})

    if not search_term:
        results = []
    else:
        results = Address.objects.filter(
            Q(street__icontains=search_term) | Q(city__icontains=search_term) | Q(zipcode__icontains=search_term))

    context = {
        "form": form,
        "search": search_term,
        "result": results
    }
    return render(request, 'houses/search.html', context)


@login_required(login_url='/accounts/login')
def house(request, house_id):
    context = {
        "house": house_id,
    }
    return render(request, 'houses/house.html', context)
