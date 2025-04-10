import requests
import json
from datetime import datetime

class FlightDataExtractor:
    """
    A class to search for flights using SERP API's Google Flights engine
    and extract the most important information in a clean format.
    """

    def __init__(self, api_key, base_url="https://serpapi.com/search"):
        """
        Initialize the FlightDataExtractor instance.

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

        # Build the parameters
        params = {
            "engine": "google_flights",
            "q": query,
            "hl": hl,
            "gl": gl,
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": departure_date,
            "api_key": self.api_key
        }
        
        # Include return_date if provided
        if return_date:
            params["return_date"] = return_date
        
        try:
            response = requests.get(self.base_url, params=params)
            # Debug: print the request URL with redacted API key
            print(f"Request URL: {response.url.split('api_key=')[0]}api_key=REDACTED")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error searching flights: {e}")
            return None

    def extract_important_flight_info(self, flight_data):
        """
        Extract only the important information from the flight data.
        
        Args:
            flight_data (dict): The raw flight data from the API.
            
        Returns:
            dict: A simplified dictionary with important flight information.
        """
        if not flight_data:
            return {"error": "No flight data found"}
        
        # Initialize the result structure
        result = {
            "search_info": {
                "origin": self._extract_location_info(flight_data.get("airports", []), "departure"),
                "destination": self._extract_location_info(flight_data.get("airports", []), "arrival"),
                "departure_date": flight_data.get("search_parameters", {}).get("outbound_date", "N/A"),
                "return_date": flight_data.get("search_parameters", {}).get("return_date", None)
            },
            "price_insights": self._extract_price_insights(flight_data.get("price_insights", {})),
            "outbound_flights": [],
            "return_flights": []
        }
        
        # Process best flights first, then other flights
        all_flights = []
        if "best_flights" in flight_data and flight_data["best_flights"]:
            for flight in flight_data["best_flights"]:
                flight["is_best"] = True
                all_flights.append(flight)
                
        if "other_flights" in flight_data and flight_data["other_flights"]:
            for flight in flight_data["other_flights"]:
                flight["is_best"] = False
                all_flights.append(flight)
        
        # Sort flights by price
        all_flights = sorted(all_flights, key=lambda x: x.get("price", float("inf")))
        
        # Extract flight details and separate by outbound/return
        for flight in all_flights:
            flight_type = flight.get("type", "").lower()
            flight_info = self._extract_flight_details(flight)
            
            if flight_type == "returning":
                result["return_flights"].append(flight_info)
            else:
                result["outbound_flights"].append(flight_info)
        
        return result
    
    def _extract_location_info(self, airports_data, direction):
        """Extract airport/city information."""
        if not airports_data or not airports_data[0].get(direction):
            return {"code": "N/A", "name": "N/A", "city": "N/A", "country": "N/A"}
        
        airport_info = airports_data[0].get(direction, [])[0]
        return {
            "code": airport_info.get("airport", {}).get("id", "N/A"),
            "name": airport_info.get("airport", {}).get("name", "N/A"),
            "city": airport_info.get("city", "N/A"),
            "country": airport_info.get("country", "N/A")
        }
    
    def _extract_price_insights(self, price_insights):
        """Extract price insights information."""
        if not price_insights:
            return {"lowest_price": "N/A", "price_level": "N/A", "typical_range": "N/A"}
        
        return {
            "lowest_price": price_insights.get("lowest_price", "N/A"),
            "price_level": price_insights.get("price_level", "N/A"),
            "typical_range": price_insights.get("typical_price_range", "N/A")
        }
    
    def _extract_flight_details(self, flight):
        """Extract important details from a flight."""
        if not flight:
            return {}
        
        # Basic flight info
        flight_info = {
            "price": flight.get("price", "N/A"),
            "is_best_flight": flight.get("is_best", False),
            "total_duration_minutes": flight.get("total_duration", "N/A"),
            "total_duration_formatted": self._format_duration(flight.get("total_duration", 0)),
            "carbon_footprint": self._extract_carbon_info(flight.get("carbon_emissions", {})),
            "segments": [],
            "layovers": []
        }
        
        # Extract flight segments
        for segment in flight.get("flights", []):
            flight_info["segments"].append({
                "airline": segment.get("airline", "N/A"),
                "flight_number": segment.get("flight_number", "N/A"),
                "aircraft": segment.get("airplane", "N/A"),
                "departure": {
                    "airport_code": segment.get("departure_airport", {}).get("id", "N/A"),
                    "airport_name": segment.get("departure_airport", {}).get("name", "N/A"),
                    "time": segment.get("departure_airport", {}).get("time", "N/A")
                },
                "arrival": {
                    "airport_code": segment.get("arrival_airport", {}).get("id", "N/A"),
                    "airport_name": segment.get("arrival_airport", {}).get("name", "N/A"),
                    "time": segment.get("arrival_airport", {}).get("time", "N/A")
                },
                "duration_minutes": segment.get("duration", "N/A"),
                "duration_formatted": self._format_duration(segment.get("duration", 0)),
                "class": segment.get("travel_class", "N/A"),
                "features": segment.get("extensions", []),
                "overnight": segment.get("overnight", False)
            })
        
        # Extract layover information
        for layover in flight.get("layovers", []):
            flight_info["layovers"].append({
                "airport_code": layover.get("id", "N/A"),
                "airport_name": layover.get("name", "N/A"),
                "duration_minutes": layover.get("duration", "N/A"),
                "duration_formatted": self._format_duration(layover.get("duration", 0)),
                "overnight": layover.get("overnight", False)
            })
        
        return flight_info
    
    def _extract_carbon_info(self, carbon_data):
        """Extract and format carbon emissions data."""
        if not carbon_data:
            return "No data"
        
        this_flight = carbon_data.get("this_flight", "N/A")
        typical = carbon_data.get("typical_for_this_route", "N/A")
        difference = carbon_data.get("difference_percent", "N/A")
        
        if this_flight != "N/A" and typical != "N/A" and difference != "N/A":
            if difference < 0:
                return f"{this_flight}g ({abs(difference)}% below average)"
            elif difference > 0:
                return f"{this_flight}g ({difference}% above average)"
            else:
                return f"{this_flight}g (average)"
        else:
            return f"{this_flight}g"
    
    def _format_duration(self, minutes):
        """Format duration from minutes to hours and minutes."""
        if minutes == "N/A" or not isinstance(minutes, (int, float)):
            return "N/A"
        
        hours, mins = divmod(minutes, 60)
        if hours > 0 and mins > 0:
            return f"{hours}h {mins}m"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{mins}m"
    
    def format_flight_data_for_agent(self, flight_data):
        """
        Format the flight data into a clean, agent-friendly format.
        
        Args:
            flight_data (dict): The extracted flight data.
            
        Returns:
            dict: A cleanly formatted dictionary for agent consumption.
        """
        if "error" in flight_data:
            return flight_data
        
        # Basic trip info
        trip_type = "Round Trip" if flight_data["search_info"]["return_date"] else "One Way"
        origin = flight_data["search_info"]["origin"]
        destination = flight_data["search_info"]["destination"]
        
        formatted_data = {
            "trip_summary": {
                "type": trip_type,
                "route": f"{origin['city']} ({origin['code']}) to {destination['city']} ({destination['code']})",
                "departure_date": flight_data["search_info"]["departure_date"],
                "return_date": flight_data["search_info"]["return_date"],
                "price_range": f"${flight_data['price_insights']['lowest_price']} ({flight_data['price_insights']['price_level']})"
                if flight_data['price_insights']['lowest_price'] != "N/A" else "Price information not available"
            },
            "outbound_options": self._format_flight_options(flight_data["outbound_flights"]),
            "return_options": self._format_flight_options(flight_data["return_flights"]) if flight_data["return_flights"] else []
        }
        
        return formatted_data
    
    def _format_flight_options(self, flights, max_options=5):
        """Format flight options in a clean way, limited to a reasonable number."""
        formatted_options = []
        
        # Limit to max_options
        for flight in flights[:max_options]:
            segments = flight["segments"]
            first_segment = segments[0] if segments else {}
            last_segment = segments[-1] if segments else {}
            
            option = {
                "price": f"${flight['price']}" if flight['price'] != "N/A" else "Price not available",
                "duration": flight["total_duration_formatted"],
                "recommended": flight["is_best_flight"],
                "departure": first_segment.get("departure", {}).get("time", "N/A") if first_segment else "N/A",
                "arrival": last_segment.get("arrival", {}).get("time", "N/A") if last_segment else "N/A",
                "airlines": ", ".join(set([segment.get("airline", "Unknown") for segment in segments])),
                "stops": len(flight["layovers"]),
                "layover_info": [],
                "segments_info": []
            }
            
            # Add layover information
            for layover in flight["layovers"]:
                option["layover_info"].append(
                    f"{layover['airport_code']} ({layover['duration_formatted']})"
                )
            
            # Add segment information
            for segment in segments:
                option["segments_info"].append({
                    "flight": f"{segment['airline']} {segment['flight_number']}",
                    "from": f"{segment['departure']['airport_code']} at {segment['departure']['time']}",
                    "to": f"{segment['arrival']['airport_code']} at {segment['arrival']['time']}",
                    "duration": segment["duration_formatted"],
                    "aircraft": segment["aircraft"]
                })
            
            formatted_options.append(option)
        
        return formatted_options

# Example usage:
if __name__ == "__main__":
    # Replace with your actual SERP API key
    serp_api_key = "f6494ea08b4832121c76aad00283c4ac0684d13ff6ba27fca055ca93909f242e"
    extractor = FlightDataExtractor(api_key=serp_api_key)

    # Define your search parameters
    origin = "JFK"
    destination = "LAX"
    departure_date = "2025-05-01"
    return_date = "2025-05-10"

    # Search for flights
    raw_flight_data = extractor.search_flights(origin, destination, departure_date, return_date=return_date)
    
    if raw_flight_data:
        # Extract important information
        extracted_data = extractor.extract_important_flight_info(raw_flight_data)
        
        # Format for agent consumption
        formatted_data = extractor.format_flight_data_for_agent(extracted_data)
        
        # Print formatted data
        print(json.dumps(formatted_data, indent=2))
        
        # Save to file
        with open("formatted_flight_data.json", "w") as f:
            json.dump(formatted_data, f, indent=2)
        print("Data saved to formatted_flight_data.json")
    else:
        print("Failed to fetch flight data")