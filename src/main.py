import os
import sys
from datetime import datetime
from utils.email_utils import send_email, load_email_config
from utils.report_utils import shift_times, get_data, render_report
from utils.logging_utils import setup_logger
import traceback

# Set up the logger for debugging and logging purposes
logger = setup_logger()

def main():
    """
    Main function for orchestrating the generation of a report, rendering it as HTML, and sending it via email.
    The function retrieves data within a specified time range, renders a report using the retrieved data,
    and sends the report as an email using SMTP configuration. Any errors that occur during the process are logged.
    """
    
    # Load email configuration from environment variables
    email_config = load_email_config()
    
    # Check for command line arguments to determine the offset for the date range
    # Default offset is 0 if no arguments are provided
    offset = 0 if len(sys.argv) == 1 else int(sys.argv[1])
    
    # Calculate start and end times for the data retrieval based on the current date and the offset
    start_time, end_time = shift_times(datetime.now(), offset)

    try:
        # Log db_config for debugging
        from data.db import db_config

        # Retrieve data from the database within the calculated time range
        data = get_data(start_time, end_time)
        
        # Check if there are no offline monitors
        if not data:
            logger.info("No offline monitors found. No email will be sent.")
            return
        
        # Render the retrieved data into an HTML report
        report_html = render_report(data, start_time.strftime("%Y-%m-%d %I:%M %p"), end_time.strftime("%Y-%m-%d %I:%M %p"))
        
        # Send the rendered HTML report via email
        send_email(report_html, email_config)
        
        # Log a success message indicating the process completed successfully
        logger.info("Report processing and email sending completed successfully.")
    except Exception as e:
        # Catch any exceptions that occur during the process, log the error, and print the traceback for debugging
        logger.error(f"An error occurred in the main process: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    # Entry point for the script when executed directly
    main()

