import requests

class FlightSearch:
    """
    A class to search for flights using SERP API's Google Flights engine.
    """

    def __init__(self, api_key, base_url="https://serpapi.com/search"):
        """
        Initialize the FlightSearch instance.

        Args:
            api_key (str): Your SERP API key.
            base_url (str): The base URL for the SERP API endpoint.
        """
        self.api_key = api_key
        self.base_url = base_url

    def search_flights(self, origin, destination, departure_date, return_date=None, hl="en", gl="us"):
        """
        Search for flights using the SERP API Google Flights engine.

        Args:
            origin (str): The departure airport/city code (e.g., "JFK").
            destination (str): The arrival airport/city code (e.g., "LAX").
            departure_date (str): Departure date in 'YYYY-MM-DD' format.
            return_date (str, optional): Return date in 'YYYY-MM-DD' format.
            hl (str): Language setting (default is "en").
            gl (str): Country code (default is "us").

        Returns:
            dict: A JSON response from the API containing flight details, or None if an error occurs.
        """
        # Construct the natural language query string
        query = f"flights from {origin} to {destination} on {departure_date}"
        if return_date:
            query += f" returning on {return_date}"

        # Build the parameters with required parameters including outbound_date and arrival_id
        params = {
            "engine": "google_flights",
            "q": query,
            "hl": hl,
            "gl": gl,
            "departure_id": origin,      # Required departure parameter
            "arrival_id": destination,   # Required arrival parameter
            "outbound_date": departure_date,  # Added outbound_date parameter
            "api_key": self.api_key
        }
        
        # Include return_date if provided
        if return_date:
            params["return_date"] = return_date
        
        try:
            response = requests.get(self.base_url, params=params)
            # Debug: print the complete request URL
            print("Request URL:", response.url)
            response.raise_for_status()  # Raise an error for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error searching flights:", e)
            print("Response content:", response.text)
            return None

# Example usage:
if __name__ == "__main__":
    # Replace with your actual SERP API key
    serp_api_key = "f6494ea08b4832121c76aad00283c4ac0684d13ff6ba27fca055ca93909f242e"
    flight_search = FlightSearch(api_key=serp_api_key)

    # Define your search parameters
    origin = "JFK"                   # Example: John F. Kennedy International Airport
    destination = "LAX"              # Example: Los Angeles International Airport
    departure_date = "2025-05-01"      # Departure date in YYYY-MM-DD format
    return_date = "2025-05-10"         # Optional return date

    flights = flight_search.search_flights(origin, destination, departure_date, return_date=return_date)
    if flights:
        print("Flight Data:")
        print(flights)
