import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth

# Define the base URLs from get-dealership.js and reviews.py
DEALERSHIP_BASE_URL = "https://rumadirivo18-3000.theiadocker-3-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"

# REVIEWS_BASE_URL = 'https://plumball33-5000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews?id={dealer_id}'

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, api_key=None, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Create headers with the API key
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic {}'.format(api_key)
        }
        
        # Call get method of requests library with URL, headers, and parameters
        response = requests.get(url, headers=headers, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, dealerId, **kwargs):
    try:
        params = {}
        if dealerId is not None:
            params['dealerId'] = dealerId

        response = requests.post(url, json=json_payload, params=params, **kwargs)
        return response
    except requests.exceptions.RequestException as e:
        raise Exception(f'Error making POST request: {e}')


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    state = kwargs.get("state")
    if state:
        json_result = get_request(url, state=state)
    else:
        json_result = get_request(url)

    print('json_result RESTAPIS', json_result)    

    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result

        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            # print(dealer_doc)
            # Create a CarDealer object with values in `doc` object

    return results

def get_dealer_by_id(dealer_id):
    # Call get_request with the base URL for dealerships and dealerId parameter
    url = REVIEWS_BASE_URL.format(dealer_id=dealer_id)
    json_result = get_request(url)

    results = []
    if json_result and "docs" in json_result:
        dealers = json_result["docs"]
        for dealer in dealers:
            # Create a CarDealer object with values in `dealer` dictionary
    return results

def get_dealers_by_state(state):
    # Call get_request with the base URL for dealerships and state parameter
    url = f"{DEALERSHIP_BASE_URL}?state={state}"
    json_result = get_request(url)

    results = []
    if json_result and "docs" in json_result:
        dealers = json_result["docs"]
        for dealer in dealers:
            # Create a CarDealer object with values in `dealer` dictionary
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(dealer_id):
    # Call get_request with the base URL for reviews and dealerId parameter
    url = REVIEWS_BASE_URL.format(dealer_id=dealer_id)
    # Pass the API key to the get_request function
    api_key = "OkANvrZmn9NYhSIQNSO1z5lIlZ5c3ays3FsQDOBUdrhx"
    json_result = get_request(url, api_key=api_key)

    results = []
    if json_result:
        for review_data in json_result:
            # Check if all required fields exist in review_data
            if "id" in review_data and "dealership" in review_data and "review" in review_data \
                    and "purchase" in review_data and "purchase_date" in review_data \
                    and "car_make" in review_data and "car_model" in review_data and "car_year" in review_data:
                # If all fields are available, create the DealerReview object
                dealer_review = DealerReview(
                    review_id=review_data["id"],
                    dealer_id=review_data["dealership"],
                    review=review_data["review"],
                    purchase=review_data["purchase"],
                    purchase_date=review_data["purchase_date"],
                    car_make=review_data["car_make"],
                    car_model=review_data["car_model"],
                    car_year=review_data["car_year"],
                    sentiment=None
                )
                results.append(dealer_review)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(dealerreview):
    # Define the URL for sentiment analysis
    url = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/ae38d3e7-7f76-412f-9ea3-da080c263c49'

    # Debugging: Print the review text
    print("Review Text:", dealerreview.review)
    # Construct the parameters from the dealerreview object
    params = {
        "text": dealerreview.review,
        "version": "2022-04-07",
        "features": "sentiment",
        "return_analyzed_text": True
    }

    # Your API key for Watson NLU
    api_key = 'OkANvrZmn9NYhSIQNSO1z5lIlZ5c3ays3FsQDOBUdrhx'

    try:
        # Make the GET request to Watson NLU
        response = get_request(url, api_key=api_key, **params)
        
        print("API Response:", response)  # Print the response for debugging

        # Check if the response is successful
        if "sentiment" in response:
            sentiment = response["sentiment"]["document"]["label"]
            print("Sentiment:", sentiment)  # Print the extracted sentiment for debugging
            return sentiment
        else:
            return None
    except Exception as e:
        # Handle any exceptions here
        print("Error analyzing sentiment:", str(e))
        return None