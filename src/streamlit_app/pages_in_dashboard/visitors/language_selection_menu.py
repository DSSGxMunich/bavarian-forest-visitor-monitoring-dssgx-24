import streamlit as st


# Add a dropdown menu for language selection with emojis
LANGUAGE_OPTIONS= {
    "German": "🇩🇪 Deutsch",
    "English": "🇬🇧 English",
    }
# Language dictionary with translations
TRANSLATIONS = {
    "English": {
        'title': 'Plan Your Trip to the Bavarian Forest 🌲',
        'select_language': 'Select Language',
        'visitor_counts_forecasted': 'Popular Times (Forecast)',
        'forecasted_visitor_data': 'The following data represents forecasted visitor traffic',
        'select_day': 'Select a day',
        'monday': 'Monday',
        'tuesday': 'Tuesday',
        'wednesday': 'Wednesday',
        'thursday': 'Thursday',
        'friday': 'Friday',
        'saturday': 'Saturday',
        'sunday': 'Sunday',
        'visitor_foot_traffic_for_day': 'Relative Visitor Foot Traffic (Hourly)',
        'visitor_foot_traffic': 'Visitor Foot Traffic',
        'low_traffic': 'Low Traffic',
        'moderate_traffic': 'Moderate Traffic',
        'peak_traffic': 'Peak Traffic',
        'real_time_parking_occupancy': 'Real Time Parking Occupancy',
        'select_parking_section': 'Select a parking section',
        'available_spaces': 'Available Spaces',
        'capacity': 'Capacity',
        'occupancy_rate': 'Occupancy Rate',
        'occupancy_status': 'Occupancy Status',
        'weather_forecast': 'Weather Forecast',
        '7_day_hourly_weather': '7-Day Hourly Weather Forecast',
        'temperature': 'Temperature (°C)',
        'date': 'Date',
        'mon': 'Mon',
        'tue': 'Tue',
        'wed': 'Wed',
        'thu': 'Thu',
        'fri': 'Fri',
        'sat': 'Sat',
        'sun': 'Sun',
        'peaks': 'Peaks',
        'recreational_activities': 'Recreational Activities',
        'hiking': 'Hiking',
        'hiking_description': 'Explore trails through the scenic wilderness.',
        'cycling': 'Cycling',
        'cycling_description': 'Cycle through picturesque routes.',
        'camping': 'Camping',
        'camping_description': 'Relax under the stars at designated camping spots.',
        'snowshoeing': 'Snowshoeing',
        'snowshoeing_description': 'Enjoy snowshoeing during the winter months.',
        'skiing': 'Skiing',
        'skiing_description': 'Ski on the best cross-country trails.',
        'hiking_link': "https://www.nationalpark-bayerischer-wald.bayern.de/english/visitor/hiking/index.htm",
        'cycling_link': "https://www.nationalpark-bayerischer-wald.bayern.de/english/visitor/bicycling/index.htm",
        'camping_link': "https://www.nationalpark-bayerischer-wald.bayern.de/english/visitor/facilities/camping/index.htm",
        'snowshoeing_link': "https://www.nationalpark-bayerischer-wald.bayern.de/english/visitor/snowshoeing/index.htm",
        'skiing_link': "https://www.nationalpark-bayerischer-wald.bayern.de/english/visitor/cross_country_skiing/index.htm",
        'learn_more': 'Learn More',
        'other_information': 'Other Information',
        'visitor_centers': 'Visitor Centers',
        'popular_entrances': 'Popular Entrances to the Park',
        'best_way_to_get_there': 'Best Way to Get There',
        'select_region': 'Select a region to view',
        'parking_data_last_updated': 'Parking Data Last Updated (CET/CEST):',
        'parking_status_low': 'Pick any spot 😎',
        'parking_status_moderate': 'A bit busy 😵‍💫',
        'parking_status_high': 'Too crowded 😡',
        'weather_data_last_updated': 'Weather Data Last Updated (CET/CEST):',
        'visitor_centers_description': '🏛️ Find information about the main visitor centers in the Bavarian Forest.',
        'visitor_centers_link': 'https://www.nationalpark-bayerischer-wald.bayern.de/english/visitor/facilities/index.htm',
        'entrances_description': '🚪 Explore the two most popular entrances to the park.',
        'getting_there_description': '🚌 Learn about the best ways to reach the Bavarian Forest.',
        'admin_page_title': 'Bavarian Forest - Admin - Visitor Monitoring',
    },
    "German": {
        'title': 'Planen Sie Ihren Besuch im Nationalpark Bayerischer Wald 🌲',
        'select_language': 'Sprache auswählen',
        'visitor_counts_forecasted': 'Besucheraufkommen (Prognose)',
        'forecasted_visitor_data': 'Diese Grafik zeigt den prognostizierten Besucherverkehr',
        'select_day': 'Tag auswählen',
        'monday': 'Montag',
        'tuesday': 'Dienstag',
        'wednesday': 'Mittwoch',
        'thursday': 'Donnerstag',
        'friday': 'Freitag',
        'saturday': 'Samstag',
        'sunday': 'Sonntag',
        'visitor_foot_traffic_for_day': 'Voraussichtliches Besucheraufkommen (pro Stunde)',
        'visitor_foot_traffic': 'Besucheraufkommen',
        'low_traffic': 'Niedrig',
        'moderate_traffic': 'Mittel',
        'peak_traffic': 'Hoch',
        'real_time_parking_occupancy': 'Parkplatzbelegung (LIVE)',
        'select_parking_section': 'Parkplatz auswählen',
        'available_spaces': 'Aktuell verfügbare Stellplätze',
        'capacity': 'Kapazität',
        'occupancy_rate': 'Belegungsrate',
        'occupancy_status': 'Belegungsstatus',
        'weather_forecast': 'Wettervorhersage',
        '7_day_hourly_weather': '7-Tage Wetter',
        'temperature': 'Temperatur (°C)',
        'date': 'Datum',
        'mon': 'Mo',
        'tue': 'Di',
        'wed': 'Mi',
        'thu': 'Do',
        'fri': 'Fr',
        'sat': 'Sa',
        'sun': 'So',
        'peaks': 'Spitzen',
        'recreational_activities': 'Aktivitäten im Nationalpark Bayerischer Wald',
        'hiking': 'Wandern',
        'hiking_description': '350 Kilometer bestens markiertes Wanderwegenetz.',
        'cycling': 'Radfahren',
        'cycling_description': '200 km ausgewiesene Radwege.',
        'camping': 'Camping',
        'camping_description': 'Ausgewiesene Zelt- und Wohnmobilstellplätze',
        'snowshoeing': 'Schneeschuhwandern',
        'snowshoeing_description': 'Das Wanderwegenetz auch im Winter erkunden.',
        'skiing': 'Langlaufen',
        'skiing_description': '80 Kilometer Langlaufloipen durch den winterlichen Nationalpark Bayerischer Wald.',
        'hiking_link': "https://www.nationalpark-bayerischer-wald.bayern.de/besucher/wandern/index.htm",
        'cycling_link': "https://www.nationalpark-bayerischer-wald.bayern.de/besucher/rad_fahren/index.htm",
        'camping_link': "https://www.nationalpark-bayerischer-wald.bayern.de/besucher/einrichtungen/camping/index.htm",
        'snowshoeing_link': "https://www.nationalpark-bayerischer-wald.bayern.de/besucher/schneeschuh/index.htm",
        'skiing_link': "https://www.nationalpark-bayerischer-wald.bayern.de/besucher/langlaufen/index.htm",
        'learn_more': 'Mehr Infos',
        'other_information': 'Weitere Informationen',
        'visitor_centers': 'Besucherzentren',
        'popular_entrances': 'Beliebte Zugänge zum Park',
        'best_way_to_get_there': 'Anreise und ÖPNV',
        'select_region': 'Wähle eine Region zum Anzeigen',
        'parking_data_last_updated': 'Parkdaten zuletzt aktualisiert (CET/CEST):',
        'parking_status_low': 'Freie Platzwahl 😎',
        'parking_status_moderate': 'Ein bisschen busy 😵‍💫',
        'parking_status_high': 'Sehr voll 😡',
        'weather_data_last_updated': 'Wetterdaten zuletzt aktualisiert (CET/CEST):',
        'visitor_centers_description': '🏛️ Hier findest du Informationen zu den wichtigsten Besucherzentren im Bayerischen Wald.',
        'visitor_centers_link': 'https://www.nationalpark-bayerischer-wald.bayern.de/besucher/einrichtungen/index.htm',
        'entrances_description': '🚪 Erkunde die beiden beliebtesten Eingänge zum Park.',
        'getting_there_description': '🚌 Erfahre mehr über die besten Möglichkeiten, den Bayerischen Wald zu erreichen.',
        'admin_page_title': 'Bayerischer Wald - Admin - Besucher Monitoring',
    }
}

# Initialize language in session state if it doesn't exist
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'German'  # Default language

def update_language():
    if st.session_state.selected_language == 'German':
        st.session_state.selected_language = 'English'
    else:
        st.session_state.selected_language = 'German'

def get_language_selection_menu():
    # Custom CSS to position the dropdown menu in the top right corner
    st.markdown(
    """
    <style>
    /* Style the selectbox for top right corner positioning */
    .stSelectbox {
        position: relative;
        top: 10px; /* Adjust top positioning */
        right: 10px; /* Adjust right positioning */
        width: 50px; /* Set dropdown width */
        z-index: 100; /* Ensure it's on top */
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    selected_language = st.selectbox(TRANSLATIONS[st.session_state.selected_language]['select_language'], 
                            options=list(LANGUAGE_OPTIONS.values()),
                            index=0 if st.session_state.selected_language == 'German' else 1,
                            # Update the session_state when changing the input
                            on_change=update_language,
                            )