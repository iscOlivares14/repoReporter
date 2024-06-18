# syntax=docker/dockerfile:1

FROM python:3.10.14-alpine3.20

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "app/reporter.py" ]
CMD [ "--period-days=7", "--config_file_path='config/config_pytest.yml'" ]