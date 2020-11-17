FROM cybexp-priv-libs

# setup environment & install dependencies
COPY ./requirements.txt /kms-server/requirements.txt
RUN pip3 install -r /kms-server/requirements.txt

# misc
RUN mkdir -p /secrets

# copy kms-server last
COPY ./kms-server /kms-server

WORKDIR /kms-server
