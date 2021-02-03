########
# This image will compile the dependencies
# It will install compilers and other packages, that won't be carried
# over to the runtime image
########
FROM alpine:3.9 AS compile-image

# Add requirements for python and pip
RUN apk add --update python3

RUN mkdir -p /opt/code
WORKDIR /opt/code

# Install dependencies
RUN apk add python3-dev build-base gcc linux-headers postgresql-dev libffi-dev

# Create a virtual environment for all the Python dependencies
RUN python3 -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
RUN pip3 install --upgrade pip


# Install other dependencies
COPY TaxipassengersBackend/requirements.txt /opt/
RUN pip3 install -r /opt/requirements.txt

########
# This image is the runtime, will copy the dependencies from the other
########
FROM alpine:3.9 AS runtime-image

# Install python
RUN apk add --update python3 curl libffi postgresql-libs
# Copy celery worker
RUN mkdir -p /opt/celery
COPY docker/celery/ /opt/celery/
COPY TaxipassengersBackend/ /opt/code/

# Copy the venv with compile dependencies from the compile-image
COPY --from=compile-image /opt/venv /opt/venv
# Be sure to activate the venv
ENV PATH="/opt/venv/bin:$PATH"

RUN chmod +x opt/celery/worker_start.sh

CMD ["/bin/sh", "opt/celery/worker_start.sh"]