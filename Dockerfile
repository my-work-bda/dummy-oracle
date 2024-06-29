FROM python:3.10-alpine

# Install dependencies
RUN apk update && apk add --no-cache \
    unzip \
    libaio \
    g++ \
    make \
    libffi-dev \
    openssl-dev

RUN mkdir -p /opt/oracle
WORKDIR /opt/oracle

COPY instantclient-basic-linux.x64-21.14.0.0.0dbru.zip /opt/oracle

# Unzip the Oracle Instant Client and clean up in a single RUN to reduce layer size
RUN unzip instantclient-basic-linux.x64-21.14.0.0.0dbru.zip && \
    rm instantclient-basic-linux.x64-21.14.0.0.0dbru.zip

# Set environment variable for Oracle Instant Client
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_14:$LD_LIBRARY_PATH

# Configure dynamic linker run-time bindings
RUN echo "/opt/oracle/instantclient_21_14" > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

# Copy and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY transaction_data.parquet transaction_data.parquet
COPY generator.py generator.py

# Set the command to run the application
CMD ["python3", "generator.py"]