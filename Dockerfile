FROM dsgantivac/gantivaflask

RUN apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev

RUN pip3 install mysql-connector
RUN pip3 install python-ldap

COPY . /app

WORKDIR /app

EXPOSE 5005
