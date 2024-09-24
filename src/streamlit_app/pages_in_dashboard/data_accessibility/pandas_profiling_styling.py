from ydata_profiling import ProfileReport
import streamlit as st

def custom_pandas_profiling_report(data):

    report = ProfileReport(data, minimal=True)

    """Injects custom CSS into the Pandas Profiling report, including header, footer, and other components."""
    report_html = report.to_html()

    # Define custom CSS styles for theming
    custom_styles = """
    <style>
        /* General body styles */
        body {
            background-color: #000000;
            color: #fafafa;
            font-family: 'sans serif';
        }

        /* Header styling */
        .profile-header {
            background-color: #000000 !important;
            color: #fafafa !important;
        }
        .profile-header h1 {
            color: #fafafa !important;
        }
        /* Customize the icon dropdown menu */
        .profile-header .icon-menu, .profile-header .icon-menu:hover {
            color: #fafafa !important;
        }

        /* Sidebar (Overview, Variables) */
        .nav-tabs {
            background-color: #333333 !important;
        }
        .nav-tabs .nav-link {
            color: #fafafa !important;
        }
        .nav-tabs .nav-link.active {
            background-color: #f63366 !important;  /* Highlight active tab */
            color: #000000 !important;
        }

        /* Footer styling */
        .profile-footer {
            background-color: #000000 !important;
            color: #fafafa !important;
        }
        .profile-footer p {
            color: #fafafa !important;
        }

        /* Content area styling */
        .report-content, .container {
            background-color: #000000 !important;
            color: #fafafa !important;
        }

        /* Headings and section titles */
        .title, .section-header, h1, h2, h3, h4, h5, h6 {
            color: #fafafa !important;
        }

        /* Tables */
        .table, .dataframe, .df {
            color: #fafafa !important;
        }
        .dataframe thead th {
            color: #fafafa !important;
            background-color: #333333; /* Darker background for table headers */
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: #333333;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #444444;
        }
        .dataframe td {
            color: #fafafa !important;
        }

        /* Dropdowns */
        .dropdown-menu, .selectbox {
            background-color: #333333;
            color: #fafafa;
        }
        .dropdown-menu a, .selectbox option {
            color: #fafafa;
        }

        /* Form elements */
        input, textarea, select {
            background-color: #333333;
            color: #fafafa;
        }
        input::placeholder, textarea::placeholder {
            color: #fafafa;
        }
    </style>
    """
    
    # Inject the custom styles into the report's HTML
    report_html = custom_styles + report_html

    # Render the report in Streamlit
    st.components.v1.html(report_html, height=800, scrolling=True)

