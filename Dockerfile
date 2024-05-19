FROM ubuntu:22.04

USER root

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    unzip \
    libaio1 

RUN mkdir -p /opt/oracle
WORKDIR /opt/oracle

COPY instantclient-basic-linux.x64-21.14.0.0.0dbru.zip /opt/oracle

RUN unzip instantclient-basic-linux.x64-21.14.0.0.0dbru.zip

RUN export LD_LIBRARY_PATH=/opt/oracle/instantclient_21_1:$LD_LIBRARY_PATH

RUN sh -c "echo /opt/oracle/instantclient_21_14 > /etc/ld.so.conf.d/oracle-instantclient.conf"
RUN ldconfig

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY transaction_data.parquet transaction_data.parquet

RUN pip install pyarrow


COPY generator.py generator.py

CMD ["python3", "generator.py"]

# docker built -t generator .
# docker run -it generator


