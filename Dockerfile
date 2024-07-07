FROM ubuntu:22.04
LABEL authors="qingmu"
LABEL email=qingmu_0722@163.com

RUN apt-get update
RUN apt-get install curl -y

RUN curl -LO https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda
RUN rm Miniconda3-latest-Linux-x86_64.sh

ENV PATH="/opt/conda/bin:${PATH}"

ADD . /workspace
WORKDIR /workspace

RUN chmod a+x ./sh/run_v012.sh

EXPOSE 8000

RUN apt-get install libpangocairo-1.0-0 -y
RUN conda install psycopg2 -y
RUN pip install -r requirements.txt

CMD ["./sh/run_v012.sh"]
