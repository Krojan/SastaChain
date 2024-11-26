# Use Python 3.13 slim as the base image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /GaribChain/src

# Install Flask (specific version 3.0.3)
RUN apt-get update && \
 pip install Flask==3.0.3\
 && pip install requests==2.32.2\
 && pip install python-dotenv

