from django.http import HttpResponse
from django.shortcuts import render, redirect
from webserver import settings
from datetime import datetime
import pyrebase

# Create your views here.
months_list = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]

firebase = pyrebase.initialize_app(settings.firebaseConfig)
authe = firebase.auth()
database = firebase.database()


def home(request):
    all_sellers = get_sellers()
    all_weighmen = get_weighmen()

    data = {
        'all_sellers': all_sellers,
        'all_weighmen': all_weighmen,
    }
    return render(request, 'home.html', data)


def seller_page(request):
    all_sellers = get_sellers()
    data = {
        'all_sellers': all_sellers
    }
    return render(request, 'seller.html', data)


def weighmen_page(request):
    all_weighmen = get_weighmen()
    data = {
        'all_weighmen': all_weighmen
    }
    return render(request, 'weighmen.html', data)


def add_sales(request):
    sales_ref = database.child('Sales')
    time_line = request.POST['date'].split('-')
    sales_ref.child(time_line[0]).child(months_list[int(time_line[1]) - 1]).push({
            'date': request.POST['date'],
            'seller_name': request.POST['seller_name'].split('-')[0],
            'seller_id': request.POST['seller_name'].split('-')[1],
            'weighmen_name': request.POST['weighmen_name'],
            'num_bags': request.POST['num_bags'],
    })
    response = redirect('/')
    return response


def add_seller(request):
    seller_ref = database.child('Sellers')
    seller_ref.child(request.POST['id']).set({
            'seller_id': request.POST['id'],
            'full_name': request.POST['name']
    })
    response = redirect('/seller')
    return response


def add_weighmen(request):
    weighmen_ref = database.child('Weighmen')
    weighmen_ref.push({
        'weighmen_id': request.POST['id'] if 'id' in request.POST else None,
        'full_name': request.POST['name']
    })
    response = redirect('/weighmen')
    return response


def get_sales(year, month, persona):
    sales = dict(database.child('Sales').child(str(year)).child(months_list[int(month) - 1]).get().val()).values()
    if persona == 'seller':
        seller_sales = []
        sellers = []
        for sale in sales:
            sales_dict = {}
            if sale['seller_id'] not in sellers:
                sales_dict['seller_name'] = sale['seller_name']
                sales_dict['seller_id'] = sale['seller_id']
                sales_dict['num_bags'] = int(sale['num_bags'])
                seller_sales.append(sales_dict)
                sellers.append(sale['seller_id'])
            else:
                for seller_sale in seller_sales:
                    if seller_sale['seller_id'] == sale['seller_id']:
                        seller_sale['num_bags'] += int(sale['num_bags'])
        sales = seller_sales
    elif persona == 'weighmen':
        weighmen_records = {}
        for sale in sales:
            weighmen_dict = {}
            weighmen_dict['seller_name'] = sale['seller_name']
            weighmen_dict['seller_id'] = sale['seller_id']
            weighmen_dict['num_bags'] = int(sale['num_bags'])
            weighmen_dict['date'] = sale['date']
            if sale['weighmen_name'] not in weighmen_records.keys():
                weighmen_records[sale['weighmen_name']] = [weighmen_dict]
            else:
                weighmen_records[sale['weighmen_name']].append(weighmen_dict)
        sales = weighmen_records

    return sales if sales is not None else []


def get_sellers():
    sellers = dict(database.child('Sellers').get().val()).values()
    return sellers


def get_weighmen():
    weighmen = dict(database.child('Weighmen').get().val()).values()
    return weighmen


def view_sales(request):
    year = request.POST['month_year'].split('-')[0] if 'month_year' in request.POST else datetime.now().year
    month = request.POST['month_year'].split('-')[1] if 'month_year' in request.POST else datetime.now().month
    persona = request.POST['persona'] if 'persona' in request.POST else 'all'
    
    month_year = str(year) + '-' + str(month)

    all_sellers = get_sellers()
    all_weighmen = get_weighmen()
    all_sales = get_sales(year, month, persona)

    data = {
        'all_sellers': all_sellers,
        'all_weighmen': all_weighmen,
        'all_sales': all_sales,
        'month_year': month_year,
        'persona': persona,
    }
    return render(request, 'sales.html', data)