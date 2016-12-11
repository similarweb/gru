FROM python:2.7

RUN apt-get update && apt-get install -y --no-install-recommends \
		libsasl2-dev python-dev libldap2-dev libssl-dev\
	&& rm -rf /var/lib/apt/lists/*

ADD requirements.txt /code/

RUN pip install -r /code/requirements.txt

ADD . /code

EXPOSE 5000

WORKDIR /code

ENV PYTHONPATH=/code:$PYTHONPATH

ENTRYPOINT ["./scripts/start_gru.py", "app:app"]

CMD ["--bind","0.0.0.0:5000"]