FROM ubuntu:bionic

RUN apt-get -qq update

ARG OPTDIR=/opt/
ARG XQA=xqa-db-amqp

RUN mkdir ${OPTDIR}/${XQA}
COPY src ${OPTDIR}/${XQA}
COPY requirements.txt ${OPTDIR}/${XQA}

RUN apt-get -qq install -y python3-pip python3-dev

RUN useradd -r -M -d ${OPTDIR}${XQA} xqa
RUN chown -R xqa:xqa ${OPTDIR}${XQA}

USER xqa

WORKDIR ${OPTDIR}${XQA}

RUN pip3 install -r requirements.txt

ENV PYTHONPATH=${OPTDIR}${XQA}

ENTRYPOINT ["python3", "xqa/db_amqp.py"]
