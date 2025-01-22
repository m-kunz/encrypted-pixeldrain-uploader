FROM python:latest
COPY pyproject.toml /uploader/pyproject.toml
WORKDIR /uploader
RUN pip install poetry
RUN poetry install
COPY . /uploader
ENTRYPOINT [ "poetry","run","python","uploader.py" ]