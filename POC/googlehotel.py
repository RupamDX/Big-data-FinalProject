import requests
import json

def get_hotel_data(query, check_in_date, check_out_date, api_key=None):
    """
    Fetch hotel data from Google Hotels API via SerpAPI
    """
    if not api_key or api_key == "YOUR_SERPAPI_API_KEY":
        raise ValueError("Please provide a valid SERP API key.")

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_hotels",
        "q": query,
        "hl": "en",
        "gl": "us",
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "api_key": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching hotel data: {e}")
        return None

def extract_important_hotel_info(hotel_data):
    """
    Extract only the important information from the hotel data
    """
    if not hotel_data or 'properties' not in hotel_data:
        return {"error": "No hotel data found or invalid response format"}
    
    extracted_hotels = []
    
    for property_data in hotel_data.get('properties', []):
        hotel = {
            "name": property_data.get('name', 'N/A'),
            "type": property_data.get('type', 'N/A'),
            "hotel_class": property_data.get('hotel_class', 'N/A'),
            "stars": property_data.get('extracted_hotel_class', 'N/A'),
            "overall_rating": property_data.get('overall_rating', 'N/A'),
            "total_reviews": property_data.get('reviews', 'N/A'),
            "location": {
                "coordinates": property_data.get('gps_coordinates', {}),
                "rating": property_data.get('location_rating', 'N/A')
            },
            "check_in_time": property_data.get('check_in_time', 'N/A'),
            "check_out_time": property_data.get('check_out_time', 'N/A'),
            "pricing": {
                "per_night": property_data.get('rate_per_night', {}).get('lowest', 'N/A'),
                "total": property_data.get('total_rate', {}).get('lowest', 'N/A'),
                "providers": [
                    {
                        "source": price.get('source', 'N/A'),
                        "rate": price.get('rate_per_night', {}).get('lowest', 'N/A')
                    } for price in property_data.get('prices', [])[:3]  # Limit to top 3 providers
                ]
            },
            "amenities": property_data.get('amenities', [])[:10],  # Limit to top 10 amenities
            "nearby_places": [
                {
                    "name": place.get('name', 'N/A'),
                    "transportation": [
                        {
                            "type": transport.get('type', 'N/A'),
                            "duration": transport.get('duration', 'N/A')
                        } for transport in place.get('transportations', [])[:2]  # Limit to top 2 transport options
                    ]
                } for place in property_data.get('nearby_places', [])[:3]  # Limit to top 3 nearby places
            ],
            "images": [img.get('thumbnail', 'N/A') for img in property_data.get('images', [])[:5]],  # Limit to 5 images
            "link": property_data.get('link', 'N/A'),
        }
        
        extracted_hotels.append(hotel)
    
    result = {
        "query": hotel_data.get('search_parameters', {}).get('q', 'N/A'),
        "dates": {
            "check_in": hotel_data.get('search_parameters', {}).get('check_in_date', 'N/A'),
            "check_out": hotel_data.get('search_parameters', {}).get('check_out_date', 'N/A')
        },
        "hotels": extracted_hotels,
        "total_hotels": len(extracted_hotels)
    }
    
    return result

def format_hotel_data_for_agent(hotel_info):
    """
    Format the hotel data in a clean, readable format for the agent
    """
    if "error" in hotel_info:
        return hotel_info["error"]
    
    formatted_output = {
        "query_details": {
            "location": hotel_info["query"],
            "check_in": hotel_info["dates"]["check_in"],
            "check_out": hotel_info["dates"]["check_out"],
            "total_results": hotel_info["total_hotels"]
        },
        "hotel_options": []
    }
    
    for hotel in hotel_info["hotels"]:
        hotel_option = {
            "name": hotel["name"],
            "class": f"{hotel['stars']}★" if hotel['stars'] != 'N/A' else hotel["hotel_class"],
            "rating": f"{hotel['overall_rating']}/5 ({hotel['total_reviews']} reviews)" if hotel['overall_rating'] != 'N/A' else "No ratings",
            "price": {
                "nightly": hotel["pricing"]["per_night"],
                "total": hotel["pricing"]["total"]
            },
            "key_amenities": hotel["amenities"],
            "location_highlights": [f"{place['name']} ({place['transportation'][0]['duration']} by {place['transportation'][0]['type']})" 
                                   for place in hotel["nearby_places"] if place.get('transportation')],
            "booking_link": hotel["link"]
        }
        formatted_output["hotel_options"].append(hotel_option)
    
    return formatted_output

if __name__ == "__main__":
    # Example usage
    query = "New York hotels"
    check_in_date = "2025-05-01"
    check_out_date = "2025-05-05"
    serpapi_api_key = "f6494ea08b4832121c76aad00283c4ac0684d13ff6ba27fca055ca93909f242e"  # Replace with your actual API key
    
    # Get raw hotel data
    hotel_results = get_hotel_data(query, check_in_date, check_out_date, api_key=serpapi_api_key)
    
    if hotel_results:
        # Extract important information
        important_info = extract_important_hotel_info(hotel_results)
        
        # Format for agent
        formatted_data = format_hotel_data_for_agent(important_info)
        
        # Print formatted data
        print(json.dumps(formatted_data, indent=2))
        
        # Alternatively, save to a file
        with open("formatted_hotel_data.json", "w") as f:
            json.dump(formatted_data, f, indent=2)
        print("Data saved to formatted_hotel_data.json")
    else:
        print("Failed to fetch hotel data")