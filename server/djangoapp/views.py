from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import date, datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Cloud function url
CF_URL = "https://ff2978a1.au-syd.apigw.appdomain.cloud"

# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request


def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['password']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
        return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request


def registration_request(request):
    context = {}
    # If it is a POST request
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships


def get_dealerships(request):
    if request.method == "GET":
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(CF_URL)
        context = {"dealer_names": dealerships}
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        # Get reviews by dealer_id from the URL
        dealership = get_dealers_from_cf(CF_URL, dealerId=dealer_id)
        reviews = get_dealer_reviews_from_cf(CF_URL, dealer_id=dealer_id)
        context = {"dealers": dealership, "dealer_reviews": reviews}
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review


def add_review(request, dealer_id):
    context = {}
    context["dealers"] = get_dealers_from_cf(CF_URL, dealerId=dealer_id)
    print(context["dealers"])
    if request.method == "GET":
        context["cars"] = CarModel.objects.all().filter(dealer_id=dealer_id)
        print(context["cars"])
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == "POST":
        review = {}
        json_payload = {}
        submitted = request.POST
        car = get_object_or_404(CarModel, pk=submitted["car"])
        car_model = None
        car_make = None
        car_year = None
        if car:
            car_model = car.name
            car_make = car.car_make.name
            car_year = car.year.strftime("%Y")

        review = {
            "name": request.user.username,
            "dealership": dealer_id,
            "review": submitted["content"],
            "purchase": len(submitted["purchasecheck"]) > 0,
            "purchase_date": datetime.strptime(submitted["purchasedate"], "%Y-%m-%d").strftime("%m/%d/%Y"),
            "car_model": car_model,
            "car_make": car_make,
            "car_year": car_year,
            "time": datetime.utcnow().isoformat(),
        }

        json_payload["review"] = review
        response = post_request(
            f"{CF_URL}/api/review", json_payload, dealerId=dealer_id)
        print(response)
        return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
