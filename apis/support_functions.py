import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, Timeout

# Set up a session with the Retry adapter
session = requests.Session()
retry = HTTPAdapter(max_retries=3)
session.mount('https://', retry)
retry_exceptions = (ConnectionError, Timeout)


def enrich_user(user, ip_address):
    # Using a third-party API to get the geolocation data for the user's IP address
    user.ip_address = ip_address
    geolocation_data = get_geolocation_data(ip_address)
    if "country" in geolocation_data:
        # print(geolocation_data)
        user.country = geolocation_data['country']
        # Use a third-party API to check if the signup date is a holiday in the user's country
        holiday_data = get_holiday_data(user.country, user.date_joined)
        if 'holiday' in holiday_data:
            user.holiday = holiday_data['holiday']
            print()
        else:
            user.holiday = False
    user.save()
    print("Enriched")


def validate_email(email):
    response = requests.get(
        f"https://emailvalidation.abstractapi.com/v1/?api_key=a5691bb339014688938b5c0a26adf3d9&email={email}")
    return response.json()["deliverability"] == 'DELIVERABLE'


def get_geolocation_data(ip_address):
    try:
        response = session.get(
            f"https://ipgeolocation.abstractapi.com/v1/?api_key=ab9e6c2eee9e4f72acb20df054ee583d&ip_address={ip_address}")
        return response.json()
    except:
        return {}


def get_holiday_data(country, date):

    try:
        response = session.get(
            f"https://holidays.abstractapi.com/v1/?api_key=f64fc7cc482b49be9bd058a5b62f72a2&country={country}&year={date.year}")
        # response.raise_for_status()
        holidays = response.json()['holidays']
        # Check if the signup date is a holiday
        print(holiday)
        for holiday in holidays:
            if holiday['date'] == date.strftime('%Y-%m-%d'):
                return True
        # Return an empty dictionary if the date is not a holiday
        return False
    except:
        # Return an empty dictionary if the request fails
        return {}
