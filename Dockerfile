FROM python:3.12

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.8.3 python -

# Include the directories where the Poetry executable might reside in the PATH env var
ENV PATH="/root/.local/bin:/opt/poetry/bin:$PATH"

# Install sqlite3
RUN apt-get update && apt-get install --yes sqlite3

# Copy the dependencies file
COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock

# Set the working directory
WORKDIR /app

# Install the dependencies
RUN poetry config virtualenvs.create false && poetry install

# Copy the repo
COPY . /app

# ETL and enrich the data
RUN make etl-enrich

# Run the app
RUN make run-app
