import requests
import json
from requests.auth import HTTPBasicAuth

# import related models here
from .models import CarDealer, DealerReview


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        api_key = kwargs.get("api_key", None)
        if api_key:
            # Basic authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            # no authentication GET
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        # If any error occurs
        print("Network exception occurred")

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.post(url, headers={'Content-Type': 'application/json'},
                                 params=kwargs,
                                 json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        return json_data
    except:
        # If any error occurs
        print("Network exception occurred")

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    # - Call get_request() with specified arguments
    # - Parse JSON results into a CarDealer object list
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(f"{url}/api/dealer", **kwargs)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["entries"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id):
    # - Call get_request() with specified arguments
    # - Parse JSON results into a DealerView object list
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(f"{url}/api/review", dealerId=dealer_id)
    if json_result and "entries" in json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["entries"]
        # For each dealer object
        for review in reviews:
            # Get its content in `doc` object
            # Create a CarDealer object with values in `doc` object
            dealer_review = DealerReview(
                dealership=review.get("dealership", None),
                name=review.get("name", None),
                purchase=review.get("purchase", None),
                review=review.get("review", None),
                purchase_date=review.get("purchase_date", None),
                car_make=review.get("car_make", None),
                car_model=review.get("car_model", None),
                car_year=review.get("car_year", None),
                sentiment=analyze_review_sentiments(review.get("review", "")),
                id=review.get("id", None))
            results.append(dealer_review)
    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    # - Call get_request() with specified arguments
    # - Get the returned sentiment label such as Positive or Negative
    # Natural language understanding url
    NLU_URL = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/83818e5d-26e0-4750-b4d1-87d578a56285"
    NLU_API_KEY = "kBZADBKxL_YqrHZIvUqiuCfiPqviqWkbbSTXY34peBBc"

    # Call get_request with a URL parameter
    json_result = get_request(f"{NLU_URL}/v1/analyze",
                              api_key=NLU_API_KEY,
                              text=text,
                              version="2019-07-12",
                              features={
                                  "sentiment": {},
                              },
                              return_analyzed_text=True)
    if json_result and "sentiment" in json_result:
        sentiment = json_result["sentiment"]["document"]["label"]
        return sentiment
