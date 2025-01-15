FROM ubuntu:22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    pkg-config \
    default-libmysqlclient-dev \
    python3-dev \
    build-essential \
    curl \
    wget \
    git \
    default-jre \
    gpg-agent \
    software-properties-common \
    mysql-client

RUN add-apt-repository -y ppa:apptainer/ppa

RUN apt update && \
    apt install -y apptainer-suid

# Create a directory for Miniconda
RUN mkdir -p /opt/miniconda3

# Download and install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /opt/miniconda3/miniconda.sh && \
    bash /opt/miniconda3/miniconda.sh -b -u -p /opt/miniconda3 && \
    rm /opt/miniconda3/miniconda.sh

# Add Miniconda to PATH
ENV PATH="/opt/miniconda3/bin:${PATH}"

# Set Conda environments path to /opt/conda/envs
ENV CONDA_ENVS_PATH=/opt/conda/envs

COPY nextflow/env.yml /app/

# Initialize Miniconda for bash
RUN conda init bash

# #  Add channels and install the tools
RUN conda env create --file env.yml

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Nextflow
RUN curl -s https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Copy only pyproject.toml and poetry.lock first to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install project dependencies
RUN poetry install

# Copy the project code into the container
COPY . /app

# Expose the port that the app runs on
EXPOSE 8000