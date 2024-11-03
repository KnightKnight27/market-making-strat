# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Default command to run the app; arguments can be overridden during container run
CMD ["python", "main.py", "-p", "market_making", "--path", "ethusdc_20240730.gz", "--instrument", "ETH_USDC"]
