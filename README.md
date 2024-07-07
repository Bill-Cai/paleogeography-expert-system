# Paleogeographic Expert System

This project is to support the following work (in submission):

**Mitigating Interpretation Bias in Geological Records Using Large Language Models: Insights from Paleoenvironmental
Analysis**

<a href=''><img src='https://img.shields.io/badge/Paper-PDF-red'></a>

## How to use

### 1. Deploy local database

In **PostgreSQL** that supports **pgvector** plugin, create a new database named `scihub`, and then create tables in
that database according to the `create.sql` instructions in `data2pgvector` folder.

After creating two data tables, download and import two CSV
data (`sedimentology_paper_paragraph.csv`, `sedimentology_paper_sentence.csv`)
from [Local database for paleogeography expert system | Figshare](https://doi.org/10.6084/m9.figshare.26198066.v1) into
the
database.

### 2. Fill in the `.env` file

In the configuration file `.env`, you must fill in the following variables

```
# Your OpenAI API Key
OPENAI_API_KEY=

# Your PostgreSQL database configuration
PGSQL_PASSWORD=
PGSQL_HOST=
PGSQL_USER=
PGSQL_PORT=

# Your Google API Key and Custom Search Engine ID
GOOGLE_API_KEY=
CUSTOM_SEARCH_ENGINE_ID=
```

Here, users need to register and apply for the corresponding service API on their own.

- OpenAI API Key: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Google API
  Key: [https://developers.google.com/custom-search/v1/overview](https://developers.google.com/custom-search/v1/overview)

### 3. Build and run the Docker image

```bash
# build the docker image
docker build -t paleogeographic-expert-system:0.1.0 .
# run the docker container
docker run -p 8000:8000 --name pes-v010 -d paleogeographic-expert-system:0.1.0
```

### 4. Access the API

The API is now available at `http://localhost:8000`.

## Citation

If you use this code in your research, please cite the following content:

```
```