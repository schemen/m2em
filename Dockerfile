FROM python:3.6-slim

MAINTAINER Schemen <me@schemen.me>


WORKDIR /usr/src/app

VOLUME /usr/src/app/data

ENTRYPOINT ["/usr/bin/dumb-init", "--"]

COPY requirements.txt ./
RUN apt-get update && apt-get install dumb-init gcc wget -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge gcc -y && apt-get autoremove -y && apt-get clean

RUN wget http://kindlegen.s3.amazonaws.com/kindlegen_linux_2.6_i386_v2_9.tar.gz -O /tmp/kindlegen.tar.gz && \
    tar xvf /tmp/kindlegen.tar.gz -C /tmp && mv /tmp/kindlegen /usr/bin && \
    rm -r /tmp/*


COPY . .

CMD [ "python","m2em.py", "--daemon", "-s"]
