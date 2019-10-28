FROM python:3.7 AS builder

COPY requirements.txt /

WORKDIR /build

RUN pip3 install -r /requirements.txt

FROM python:alpine3.7 AS app

WORKDIR /app

COPY --from=builder /build /app/

COPY scrape.py /app/

EXPOSE 80

CMD [ "python", "./scrape.py" ]
