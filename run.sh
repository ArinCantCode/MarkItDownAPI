#!/bin/bash

# Build the Docker image
docker build -t markitdown-server .

# Run the Docker container in the background (detached mode)
docker run -p 5000:5000 --name markitdown-container markitdown-server
