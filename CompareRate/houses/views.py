import requests
import json

from lxml import etree

from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.core.exceptions import SuspiciousOperation

from django.conf import settings
from .forms import SearchForm
from .models import Address

# standardize when no data found in zillow url call
NOT_AVAIL_ERR="Not Available"

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
            Q(street__icontains=search_term) | Q(city__icontains=search_term)).order_by('street')

    context = {
        "form": form,
        "search": search_term,
        "result": results
    }
    return render(request, 'houses/search.html', context)

# clean lxml data...
def clean_data(data):
    if data is not None:
        if hasattr(data,'text'):
            if (data.text is not None):
                return data.text
    return NOT_AVAIL_ERR

def clean_integer(data):
    if data is not None:
        if hasattr(data,'text'):
            if (data.text is not None):
                return int(data.text)
    return NOT_AVAIL_ERR

def get_property_data(zpid, house):
    params = {'zws-id': settings.ZILLOW_API_KEY, 'zpid': zpid}
    r = requests.get('http://www.zillow.com/webservice/GetUpdatedPropertyDetails.htm', params)

    house['details'] = 0
    if r.status_code == 200:
        house_xml = etree.fromstring(r.content)
        error_code = house_xml.find('message/code').text
        if error_code == '0':
            listed_images = []
            images = house_xml.findall('response/images/image/url')
            if images:
                for image_url in images:
                    try:
                        listed_images.append(image_url.text)
                    except:
                        pass
            house['images'] = listed_images
            house['description'] = clean_data(house_xml.find('response/homeDescription'))
            house['type'] = clean_data(house_xml.find('response/editedFacts/useCode'))
            house['bedrooms'] = clean_data(house_xml.find('response/editedFacts/bedrooms'))
            house['bathrooms'] = clean_data(house_xml.find('response/editedFacts/bathrooms'))
            house['sqft'] = clean_integer(house_xml.find('response/editedFacts/finishedSqFt'))
            house['year'] = clean_integer(house_xml.find('response/editedFacts/yearBuilt'))
            house['rooms'] = clean_integer(house_xml.find('response/editedFacts/numRooms'))
            house['details'] = 1
        elif error_code == '2':
            return HttpResponseForbidden("Zillow API Key is not Active...")
    return house

@login_required(login_url='/accounts/login')
def house(request, house_id):
    house = Address.objects.get(pk=house_id)
    params = {'zws-id': settings.ZILLOW_API_KEY, 'address': house.street, 'citystatezip': house.city + "," + house.state}
    r = requests.get('http://www.zillow.com/webservice/GetSearchResults.htm', params)

    search_results = []
    if r.status_code == 200:
        house_xml = etree.fromstring(r.content)
        error_code = house_xml.find('message/code').text
        if error_code == '0':
            for result in house_xml.findall('response/results/result'):
                house = {}
                try:
                    house['zpid'] = result.find('zpid').text
                except:
                    return HttpResponseServerError("No Zillow Property key found...")
                zillow_estimate = clean_integer(result.find('zestimate/amount'))
                if zillow_estimate == "Not Available":
                    continue
                house['estimate'] = zillow_estimate
                house['estimate_range_low'] = clean_integer(result.find('zestimate/valuationRange/low'))
                house['estimate_range_high'] = clean_integer(result.find('zestimate/valuationRange/high'))
                house['homedetail_url'] = clean_data(result.find('links/homedetails'))
                house['comparable_url'] = clean_data(result.find('links/comparables'))
                try:
                    house['address'] = result.find('address/street').text + ", " + result.find(
                        'address/city').text + ", " + result.find('address/state').text + " " + result.find(
                        'address/zipcode').text
                except:
                    return HttpResponseServerError("No Zillow Address Found")
                house = get_property_data(house['zpid'], house)
                house_json = json.loads(json.dumps(house, indent=4, sort_keys=True))
                search_results.append(house_json)
        elif error_code == '2':
            return HttpResponseForbidden("Zillow API Key is not Active...")
        elif error_code in ('3', '4'):
            return HttpResponseServerError("Zillow can't process the request...")
        elif error_code in ['502','508']:
            pass
        else:
            raise SuspiciousOperation('Bad Request Parameters...')

    context = {
        "houses": search_results,
    }
    return render(request, 'houses/house.html', context)
