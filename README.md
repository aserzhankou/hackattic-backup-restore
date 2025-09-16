# hackattiс-backup-restore

This repo contains Python script which can be used as a solution for exercise published at https://hackattic.com/challenges/backup_restore.

## Requirements

- **Python**: 3.7 or higher
- **PostgreSQL**: 11
- **Environment Variables**:
  - `ACCESS_TOKEN`: Hackattic access token
  - `PG_PASSWORD`: Password for Postgres database
- **Database configuration**:
  - `PG_HOST`: Postgres database hostname or ip
  - `PG_DATABASE`: Name of Postgres database
  - `PG_USER`: Username to connect Postgres instance

## Description

Script grabs a dump encoded with base64 from the provided endpoint using GET request, decodes it to the gzip file (suprpise!), then uncompresses it and as a result there is text file with a pure SQL.

Then using psql this data gets imported into the configured PSQL instance. After that, SSN's of entries with status=alive are selected from the DB, to combine a json set which is sent to the provided endpoint using POST request.

## Usage

1. Clone GitHub repo:

```bash
git clone git@github.com:aserzhankou/hackattic-backup-restore.git
```

2. Create venv:

```bash
python3 -m venv venv
```

3. Install requirements:

```bash
pip install -r requirements.txt
```

4. If needed, spin up a local Postgres instance using Docker:

```bash
docker run --rm -d --name temp-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=testdb -p 5432:5432 postgres:11
```

5. Set environment variables:

```bash
export ACCESS_TOKEN=yourvaluehere
export PG_PASSWORD=yourpasswordhere
```

And adjust PSQL configuration (if not using local Docker PSQL instance from the steps above):

```PG_HOST```, ```PG_DATABASE```, ```PG_USER```

6. Start the script:

```bash
python backup_restore.py
```

7. Stop local Postgres instance in Docker (if it was used)

```bash
docker kill temp-postgres
```

### Note: Second run on the existing database will result in the failed execution

## Debug mode

Debug mode can be enabled by settings `DEBUG_MODE` varible to True.

Debug mode provides verbose logging and temporary files are not deleted in the end of execution.

## Things to improve (if there was a reason :)

- Use .env files
- Add enhanced handling of errors and exceptions handling
- Add pre-commit checks
- Spin up Docker container automatically and clean up DB tables before each run
