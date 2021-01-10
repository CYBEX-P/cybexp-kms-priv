FROM cybexp-priv-libs

# setup environment & install dependencies
COPY ./requirements.txt /kms-server/requirements.txt
RUN pip3 install -r /kms-server/requirements.txt

# misc
RUN mkdir -p /secrets

# copy kms-server last
COPY ./kms-server /kms-server
# COPY ./config.yaml /kms-server/config.yaml

WORKDIR /kms-server
EXPOSE 5000

ENTRYPOINT ["/usr/bin/python3", "-u", "/kms-server/server.py"] 

