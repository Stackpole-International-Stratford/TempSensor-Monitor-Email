# src/utils/report_utils.py

from datetime import datetime, timedelta
from utils.logging_utils import setup_logger
import jinja2
import traceback
import os
import mysql.connector
from data.db import db_config

logger = setup_logger()

def shift_times(date, date_offset=0):
    """
    Shifts the given date by a specified number of days and returns the start and end dates.

    Parameters:
    - date: The base date for shifting.
    - date_offset (optional): The number of days to offset the date. Defaults to 0.

    Returns:
    - start_date: The start date after shifting.
    - end_date: The end date after shifting.
    """
    # Calculate the end date as the specified date at 7 AM, adjusted by the date offset
    end_date = date.replace(hour=7, minute=0, second=0, microsecond=0) - timedelta(days=date_offset)
    
    # Calculate the start date as 24 hours before the end date
    start_date = end_date - timedelta(hours=24)
    
    # Adjust the end date by subtracting one second to ensure the time range is exclusive of the end date
    end_date = end_date - timedelta(seconds=1)
    
    return start_date, end_date

def get_data(start, end):
    """
    Retrieve data for report generation within the specified time range by querying the database.

    Parameters:
    - start (datetime): The start time for data retrieval.
    - end (datetime): The end time for data retrieval.

    Returns:
    - list: A list of dictionaries, each containing information about the non-reporting temperature sensors.
            Each dictionary contains the following keys:
            - 'ip_address': The IP address of the monitor.
            - 'timestamp': The human-readable timestamp of the last report from the monitor.
            - 'temp': The temperature recorded by the monitor.
            - 'humidity': The humidity recorded by the monitor.
            - 'humidex': The humidex calculated from the temperature and humidity.
            - 'zone': The zone in which the monitor is located.
            - 'area': The area in which the monitor is located.
    """
    try:
        # Establish a connection to the MySQL database using the provided configuration
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        # Define the query to fetch monitors with a timestamp older than 5 minutes
        query = """
        SELECT ip_address, timestamp, temp, humidity, humidex, zone, area
        FROM temp_monitors
        WHERE timestamp < UNIX_TIMESTAMP() - 300
        """
        
        # Execute the query
        cursor.execute(query)
        
        # Fetch all the rows returned by the query
        data = cursor.fetchall()
        
        # Format the timestamp to a human-readable format with minutes and AM/PM
        for item in data:
            item['timestamp'] = datetime.fromtimestamp(item['timestamp']).strftime('%Y-%m-%d %I:%M %p')
        
        # Close the cursor and the connection to free up resources
        cursor.close()
        connection.close()
        
        return data
    except mysql.connector.Error as err:
        # Log any errors that occur during the database connection or query execution
        logger.error(f"Error: {err}")
        raise

def render_report(data, start, end):
    """
    Render a report as an HTML string using Jinja2 templates based on the provided data, start time, and end time.

    Parameters:
    - data (list of dict): The data to be included in the report, typically containing information about non-reporting sensors.
    - start (datetime): The start time for the report period.
    - end (datetime): The end time for the report period.

    Returns:
    - str: The rendered HTML content of the report.

    Raises:
    - jinja2.TemplateError: If there is an error during template rendering.
    """
    try:
        # Get the directory path where the current script is located
        current_directory = os.path.dirname(__file__)
        
        # Construct the path to the templates directory
        template_path = os.path.join(current_directory, '..', 'templates')

        # Load the Jinja2 environment and the template from the templates directory
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path))
        template = env.get_template('template.html')
        
        # Render the template with the provided data and return the resulting HTML string
        return template.render(data=data, start=start, end=end)
    except Exception as e:
        # Log any errors that occur during the template rendering
        logger.error(f"Error rendering template: {str(e)}")
        traceback.print_exc()
        raise