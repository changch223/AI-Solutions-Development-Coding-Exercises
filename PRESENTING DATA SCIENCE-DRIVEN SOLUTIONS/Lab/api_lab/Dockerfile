# Use an official Python base image; pin a version for reproducibility
FROM python:3.10-slim

# Set a working directory in the container
WORKDIR /app

# Copy your code and requirements into the container
COPY requirements.txt ./
COPY app.py ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose an environment variable for the GLA API key (optional):
# This line doesn't "inject" the key, it just declares a default empty key.
ENV GLA_API_KEY=""

# The default command to run your main script
CMD ["python", "app.py"]


# CMD to build
# docker build -t my-3player-blackjack .

#cmd to run 
# docker run -it --rm  -e GLA_API_KEY="PUT UR KEY HERE" my-3player-blackjack