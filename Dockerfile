FROM python:3.6.4-jessie

# set env variables

# install base packages
RUN apt-get clean \
 && apt-get update --fix-missing \
 && apt-get install -y \
    git \
    curl \
    gcc \
    g++ \
    build-essential \
    wget \
    awscli

WORKDIR /work

# install python packages
COPY requirements.in .
RUN pip3 install -r requirements.in

# add the code as the final step so that when we modify the code
# we don't bust the cached layers holding the dependencies and
# system packages.
COPY corvid/ corvid/
COPY tests/ tests/
COPY .pylintrc .
# not obvious to me whether we need this, so currently commented out
#RUN pip3 install --quiet -e .

CMD [ "/bin/bash" ]
