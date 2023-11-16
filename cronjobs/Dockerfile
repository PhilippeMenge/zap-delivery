# Use an official Python runtime as a parent image
FROM python:3.12-slim


# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Make the entry point script executable
RUN chmod +x entrypoint.sh

# Set the entry point script as the entry point
ENTRYPOINT ["./entrypoint.sh"]