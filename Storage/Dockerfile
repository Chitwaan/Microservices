# Use Ubuntu as the base image
FROM ubuntu:20.04

# Set your email as the maintainer of this Dockerfile
LABEL maintainer="kaurchitwan7@gmail.com"

# Avoid prompts from apt
ARG DEBIAN_FRONTEND=noninteractive

# Update apt-get, install Python, pip, and other utilities you might need
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

# Set the working directory inside the container
# WORKDIR /app

# Copy only the requirements.txt file to leverage Docker cache
# Note: You will have different requirements.txt for each service, make sure to adjust the source path as needed
COPY ./requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip3 install -r /app/requirements.txt

# Copy the rest of your application's code to the container
COPY . /app

# Set the default command to run your application
# Replace 'app.py' with the main script of your microservice
ENTRYPOINT ["python3"]
CMD ["app.py"]
