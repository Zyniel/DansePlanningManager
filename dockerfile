# syntax=docker/dockerfile:1.2

# ==============================================================================
# Contents of Dockerfile
# <Description>
# ==============================================================================
# Pull a Base Image
FROM ubuntu:20.04
LABEL "version"="0.1"
LABEL "service.name"="Danse Planning Parser"
LABEL "service.author"="CABANNES François"

# Versions
ARG EDGE_VERSION="google-chrome-stable"
ARG PYTHON_VERSION=3.9
ARG PIP_VERSION=3

# ==============================================================================
# Install Misc.
# ==============================================================================
# Install unzip
RUN apt-get update && apt-get install -yqq unzip wget curl

# ==============================================================================
# Install Python
# ==============================================================================
# Install keys
RUN apt-get update && \
    apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa

# Install Python 3.9
RUN apt-get update && \
    apt-get install --no-install-recommends -y python${PYTHON_VERSION} python${PYTHON_VERSION}-dev python${PYTHON_VERSION}-venv python${PIP_VERSION}-pip python3-wheel build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Make some useful symlinks that are expected to exist
RUN cd /usr/local/bin \
	&& ln -s idle3 idle \
	&& ln -s pydoc3 pydoc \
	&& ln -s python3 python \
	&& ln -s python3-config python-config

# ==============================================================================
# Install Xvfb virtual/headless display
# ==============================================================================
RUN apt-get update -y && \
    apt-get -y install xvfb  && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

USER root

# ==============================================================================
# Install Chrome
# ==============================================================================
# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# Adding Google Chrome to the repositories
RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
# Updating apt to see and install Google Chrome
RUN apt-get update -qqy
# Install Chrome
RUN apt-get -qqy install ${CHROME_VERSION:-google-chrome-stable}
# Cleanup package / temp
RUN rm /etc/apt/sources.list.d/google-chrome.list
RUN rm -rf /var/lib/apt/lists/* /var/cache/apt/*


# ==============================================================================
# Install Chrome WebDrivers
# ==============================================================================
# Get latest version number for chromedriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    # Create destination folder for chromedriver
    mkdir -p /opt/chromedriver-${CHROMEDRIVER_VERSION} && \
    # Download chromedriver
    wget -O /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    # Extract files to installation folder
    unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-${CHROMEDRIVER_VERSION} && \
    # Cleanup temporary download material
    rm /tmp/chromedriver_linux64.zip && \
    # Tweak execution permissions
    chmod +x /opt/chromedriver-${CHROMEDRIVER_VERSION}/chromedriver && \
    # Create symlink
    ln -fs /opt/chromedriver-${CHROMEDRIVER_VERSION}/chromedriver /usr/bin/chromedriver

# Set display port as an environment variable
ENV DISPLAY=:99

# ==============================================================================
# Download Pytesseract
# ==============================================================================
RUN apt-get update -qqy && \
    apt install -qqy tesseract-ocr tesseract-ocr-fra imagemagick libtesseract-dev

# ==============================================================================
# Download Fonts
# ==============================================================================
# http://askubuntu.com/a/25614
RUN echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections
RUN apt-get update -qqy && apt-get install -y --no-install-recommends fontconfig ttf-mscorefonts-installer
RUN fc-cache -f -v

RUN useradd --create-home ocanada
USER ocanada
CMD ["bash"]

# ==============================================================================
# Checks
# ==============================================================================
RUN echo "Python : `python -v`"
RUN echo "Tesseract : `tesseract -v`"
