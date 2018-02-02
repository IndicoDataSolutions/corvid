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

COPY ./requirements.txt .

# install python packages
RUN pip3 install -r requirements.txt

# add the code as the final step so that when we modify the code
# we don't bust the cached layers holding the dependencies and
# system packages.
COPY extract_empirical_results/ extract_empirical_results/
COPY scripts/ scripts/
COPY tests/ tests/
#RUN pip3 install --quiet -e .

CMD [ "/bin/bash" ]
