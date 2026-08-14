FROM python:3.11-slim

WORKDIR /app

# ---------------------------------------------------------
# System dependencies + Microsoft ODBC Driver 18
# ---------------------------------------------------------

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg \
        unixodbc \
        unixodbc-dev \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor \
        > /usr/share/keyrings/microsoft-prod.gpg \
    && curl -sSL \
        https://packages.microsoft.com/config/debian/12/prod.list \
        > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------
# Python dependencies
# ---------------------------------------------------------

COPY requirements.txt .

RUN pip install --no-cache-dir \
    -r requirements.txt

# ---------------------------------------------------------
# Application
# ---------------------------------------------------------

COPY app ./app

# Copy RAG/knowledge data if it lives in these directories.
# We will adjust this if your project uses another location.
COPY data ./data

EXPOSE 8000

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]