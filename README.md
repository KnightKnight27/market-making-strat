
# README: Running the Automated Trading App with Docker

## Project Overview
This project is an automated trading system designed to execute a market-making strategy using historical trading tick data. The app is implemented in Python with several custom modules and uses the `hftbacktest` library.

## Prerequisites
- **Docker**: Ensure Docker is installed on your machine. [Install Docker](https://docs.docker.com/get-docker/)
- **Python**: (Optional, if you want to run the app locally without Docker)

## Project Structure
```
project-root/
├── AutomatedTrader.py
├── main.py
├── MMStrategy.py
├── RiskManager.py
├── TradeTickReader.py
├── utils.py
├── requirements.txt
└── Dockerfile
```

## Steps to Run the Project Using Docker

### 1. Create `requirements.txt`
Ensure that your `requirements.txt` file includes all necessary packages:
```plaintext
hftbacktest==2.1.0
numpy
logging
argparse
asyncio
```

### 2. Create the `Dockerfile`
The `Dockerfile` should define the environment for running the app:
```Dockerfile
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
```

### 3. Build the Docker Image
Navigate to your project directory in the terminal and build the Docker image:
```bash
docker build -t trading-bot-app .
```

- `-t trading-bot-app` tags the image with the name `trading-bot-app`.
- `.` indicates that the build context is the current directory.

### 4. Run the Docker Container
Run the container using the specified command-line arguments:
```bash
docker run --rm -v $(pwd):/app trading-bot-app --path "ethusdc_20240730.gz" --instrument "ETH_USDC" -p "market_making"
```

- `--rm`: Automatically removes the container when it exits.
- `-v $(pwd):/app`: Mounts the current directory from your local machine to the `/app` directory in the container for data access.

### Explanation of the Command-Line Arguments:
- `--path`: The path to the tick data file (e.g., `ethusdc_20240730.gz`).
- `--instrument`: The trading pair to be analyzed (e.g., `ETH_USDC`).
- `-p`: Specifies the process (e.g., `market_making`).

### Example Run Command
```bash
docker run --rm -v $(pwd):/app trading-bot-app --path "ethusdc_20240730.gz" --instrument "ETH_USDC" -p "market_making"
```

## Additional Information
- **Logs**: The app logs important events to `output.log` and displays logs in the console. Adjust logging settings in `main.py` if needed.
- **Data Access**: Ensure the `ethusdc_20240730.gz` data file is present in the mounted directory (`$(pwd)`) for the app to access it correctly.

## Troubleshooting
- **File Not Found Error**: Verify that the `ethusdc_20240730.gz` file is in the project directory or adjust the mounted path in the `docker run` command.
- **Docker Build Issues**: Ensure Docker is up-to-date and that you have an active internet connection for `pip install` to work during the build process.
- **Permission Issues**: If you face permission issues when mounting volumes, try running Docker with elevated permissions.
