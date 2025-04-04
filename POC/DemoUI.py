import streamlit as st
from datetime import date

def main():
    # Set up the page configuration
    st.set_page_config(page_title="Real-Time Personalized Travel Planner", layout="wide")
    
    # Title and introductory text
    st.title("Real-Time Personalized Travel Planner")
    st.write("Plan your trip with integrated flight & hotel search, personalized itineraries, and real-time travel alerts!")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Select Mode", ["Home", "Flight Search", "Hotel Search", "Itinerary", "Alerts"])
    
    if app_mode == "Home":
        st.header("Welcome to Your Travel Planner")
        st.image("https://via.placeholder.com/800x300.png?text=Travel+Planner", use_column_width=True)
        st.write("Manage all your travel needs in one place. Use the sidebar to navigate between searching flights, hotels, and generating your itinerary.")
    
    elif app_mode == "Flight Search":
        st.header("Flight Search")
        col1, col2 = st.columns(2)
        with col1:
            origin = st.text_input("Origin Airport/City", value="JFK")
            departure_date = st.date_input("Departure Date", min_value=date.today())
        with col2:
            destination = st.text_input("Destination Airport/City", value="LAX")
            return_date = st.date_input("Return Date (optional)", min_value=date.today())
        if st.button("Search Flights"):
            st.write(f"Searching for flights from **{origin}** to **{destination}** departing on **{departure_date}**" +
                     (f" and returning on **{return_date}**." if return_date else "."))
            # Dummy flight results display
            st.subheader("Flight Results")
            st.write("Flight 1: $350, Non-stop")
            st.write("Flight 2: $299, 1 stop")
            st.write("Flight 3: $410, Non-stop")
    
    elif app_mode == "Hotel Search":
        st.header("Hotel Search")
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("City", value="New York")
            check_in = st.date_input("Check-in Date", min_value=date.today())
        with col2:
            check_out = st.date_input("Check-out Date", min_value=date.today())
        if st.button("Search Hotels"):
            st.write(f"Searching hotels in **{location}** from **{check_in}** to **{check_out}**.")
            # Dummy hotel results display
            st.subheader("Hotel Results")
            st.write("Hotel A: $150/night, 4-star")
            st.write("Hotel B: $120/night, 3-star")
            st.write("Hotel C: $200/night, 5-star")
    
    elif app_mode == "Itinerary":
        st.header("Your Itinerary")
        st.write("Based on your preferences, here is a sample itinerary:")
        st.subheader("Day 1")
        st.write("- Arrive at destination and check into your hotel.")
        st.write("- Afternoon: City tour and local attractions.")
        st.subheader("Day 2")
        st.write("- Morning: Visit museums and parks.")
        st.write("- Evening: Enjoy local cuisine.")
        st.subheader("Day 3")
        st.write("- Morning: Shopping and local market visit.")
        st.write("- Afternoon: Relax at a café or park.")
        st.write("*(This is a dummy itinerary. Actual itineraries would be dynamically generated based on user inputs.)*")
    
    elif app_mode == "Alerts":
        st.header("Real-Time Travel Alerts")
        st.write("Stay informed with the latest travel advisories:")
        st.info("No current alerts. Your travel plans are clear!")
        st.write("*(Alerts will be updated in real time when connected to the backend.)*")

if __name__ == "__main__":
    main()
