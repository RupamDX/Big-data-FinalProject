import requests

def get_hotel_data(query, check_in_date, check_out_date, api_key=None):
    if not api_key or api_key == "YOUR_SERPAPI_API_KEY":
        raise ValueError("Please provide a valid SERP API key.")

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_hotels",   # Use the Google Hotels API engine
        "q": query,                  # Search query (e.g., "New York hotels")
        "hl": "en",                  # Language setting (English)
        "gl": "us",                  # Country code (United States)
        "check_in_date": check_in_date,   # Check-in date in YYYY-MM-DD format
        "check_out_date": check_out_date, # Check-out date in YYYY-MM-DD format
        "api_key": api_key           # Your SERP API key
    }
    
    try:
        response = requests.get(url, params=params)
        # Debug: print the full request URL
        print("Request URL:", response.url)
        response.raise_for_status()  # Raise an error for bad responses
        hotels = response.json()
        return hotels
    except requests.exceptions.RequestException as e:
        print("Error fetching hotel data:", e)
        print("Response content:", response.text)
        return None

if __name__ == "__main__":
    # Example usage:
    query = "New York hotels"         # Query for hotels in New York
    check_in_date = "2025-05-01"        # Example check-in date
    check_out_date = "2025-05-05"       # Example check-out date
    serpapi_api_key = "f6494ea08b4832121c76aad00283c4ac0684d13ff6ba27fca055ca93909f242e"  # Your valid SERP API key

    hotel_results = get_hotel_data(query, check_in_date, check_out_date, api_key=serpapi_api_key)
    if hotel_results:
        print("Hotel Data:")
        print(hotel_results)
