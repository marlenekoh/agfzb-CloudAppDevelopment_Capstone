from django.db import models
from django.utils.timezone import now
from datetime import datetime


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
# Car make is the brand of the vehicle e.g. Toyota
class CarMake(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, max_length=50)
    description = models.CharField(null=False, max_length=200)

    def __str__(self):
        return "\n".join([
            f"Car Make Name: {self.name}",
            f"Car Make Description: {self.description}"
        ])

# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
# Car model is the specific vehicle model e.g. 2020 Prius
class CarModel(models.Model):
    id = models.AutoField(primary_key=True)

    class CarType(models.TextChoices):
        SEDAN = "sedan"
        SUV = "suv"
        WAGON = "wagon"

    car_type = models.CharField(
        null=False, choices=CarType.choices, max_length=50)
    name = models.CharField(null=False, max_length=50)
    year = models.DateField(null=False)
    dealer_id = models.IntegerField(null=False)

    # One car make has many car models
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)

    def __str__(self):
        return "\n".join([
            f"Car Model Name: {self.name}",
            f"Car Model Type: {self.car_type}",
            f"Car Model Year: {self.year}"
        ])


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer(models.Model):
    id = models.AutoField(primary_key=True)

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview(models.Model):
    id = models.AutoField(primary_key=True)

    def __init__(self, dealership, name, purchase, review, purchase_date, car_make, car_model, car_year, sentiment, id):
        self.dealership = dealership
        self.name = name
        self.purchase = purchase
        self.review = review
        self.purchase_date = datetime.strptime(purchase_date, "%m/%d/%Y")
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment
        self.id = id

    def __str__(self):
        return "Dealer Review name: " + self.name
