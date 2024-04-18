import requests
from functools import lru_cache


@lru_cache(maxsize=None)
def get_usd_to_eur_rate():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        data = response.json()
        if response.status_code == 200:
            usd_to_eur_rate = float(data['rates']['EUR'])
            return usd_to_eur_rate

    except Exception as e:
        print("Failed to get USD/EUR rate, using 1 approximation", e)

    return 1
