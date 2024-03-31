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
WORKDIR /app

# Copy only the requirements.txt file to leverage Docker cache
# Adjust the source path if your Event Logger service's requirements.txt is located elsewhere
COPY ./requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip3 install -r /app/requirements.txt

# Copy the rest of your Event Logger application's code to the container
COPY . /app

# Set the default command to run your application
# Adjust if your Event Logger service uses a different main script
ENTRYPOINT ["python3"]
CMD ["app.py"]
