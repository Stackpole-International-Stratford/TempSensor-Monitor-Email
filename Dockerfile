FROM python:3.7

# Install cron and other necessary tools
RUN apt-get update && apt-get -y install cron nano

# Set the working directory
WORKDIR /app

# Set the timezone
ENV TZ=America/Toronto
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the crontab file to the appropriate location
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab

# Apply the crontab
RUN crontab /etc/cron.d/crontab

# Copy the rest of the application code
COPY . .

# Ensure environment variables are set correctly
ENV PYTHONPATH=/app

# Debugging prints
RUN echo "PYTHONPATH is set to: $PYTHONPATH"

# Run cron in the foreground
CMD ["cron", "-f"]
