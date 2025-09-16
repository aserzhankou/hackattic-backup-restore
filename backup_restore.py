import os
import requests
import json
import base64
import subprocess
import gzip
import psycopg2

DEBUG_MODE = False

# Pull problem dataset using GET method from this URL
PROBLEM_URL = "https://hackattic.com/challenges/backup_restore/problem?access_token="

# Put solution using POST method to this URL
SOLVE_URL = "https://hackattic.com/challenges/backup_restore/solve?access_token="

# Dump file name
DUMP_FILE = "dataset_dump.sql"

# Access token to access endpoints
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# PostgreSQL configuration
PG_HOST = "localhost"
PG_DATABASE = "testdb"
PG_USER = "postgres"
PG_PASSWORD = os.environ.get("PG_PASSWORD")


def get_problem_dataset():

    if DEBUG_MODE:
        print("Getting problem dataset")
        print(f"URL: {PROBLEM_URL + ACCESS_TOKEN}")
    else:
        print("Getting problem dataset")

    response = requests.get(PROBLEM_URL + ACCESS_TOKEN)
    
    print(f"Response status: {response.status_code}")
    
    return response.json()


def decode_data(data):
    # Decode base64 data
    return base64.b64decode(data)


def save_data(data, filename):
    # Save decoded data to file
    with open(filename, "wb") as f:
        f.write(data)


def decompress_gzip_file(gzip_file, output_file):
    # Decopress gzip file with dump
    with gzip.open(gzip_file, 'rb') as f_in:
        with open(output_file, 'wb') as f_out:
            f_out.write(f_in.read())


def import_sql_to_postgres(sql_file):
    # Import SQL file into PostgreSQL using psql
    env = os.environ.copy()
    env['PGPASSWORD'] = PG_PASSWORD
    
    cmd = ['psql', '--host', PG_HOST, '--username', PG_USER, 
           '--dbname', PG_DATABASE, '--file', sql_file]

    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if DEBUG_MODE:
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
    return result.returncode == 0


def get_alive_ssns():
    # Query database for SSNs where status is 'alive'
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            user=PG_USER,
            password=PG_PASSWORD,
            database=PG_DATABASE
        )
        cur = conn.cursor()

        cur.execute("SELECT ssn FROM criminal_records WHERE status = 'alive'")
        results = cur.fetchall()

        ssns = [row[0] for row in results]

        cur.close()
        conn.close()

        return ssns
    except Exception as e:
        print(f"Database error: {e}")
        return []


def solve_problem(solution):
    json_payload = json.dumps(solution)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Content-Length': str(len(json_payload.encode('utf-8')))
    }
    
    # Print what we're sending
    print("Sending solution to Hackattic")

    if DEBUG_MODE:
        print("=== REQUEST DETAILS ===")
        print(f"URL: {SOLVE_URL + ACCESS_TOKEN}")
        print(f"Headers: {headers}")
        print(f"JSON payload: {json_payload}")
        print("=======================")

    response = requests.post(SOLVE_URL + ACCESS_TOKEN, data=json_payload, headers=headers)
    
    # Print response details
    if DEBUG_MODE:
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        print(f"Response: {response.text}")
    
    return response.json()


def cleanup():
    """Clean up temporary files created during the process."""
    files_to_remove = [
        DUMP_FILE + ".gz",
        DUMP_FILE,
    ]
    
    print("Cleaning up temporary files...")
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                if DEBUG_MODE:
                    print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Warning: Could not remove {file_path}: {e}")
        else:
            if DEBUG_MODE:
                print(f"File not found (already cleaned): {file_path}")


def main():
    # Get problem dataset
    problem_dataset = get_problem_dataset()

    # Decode data from base64 to bytes
    decoded_data = decode_data(problem_dataset["dump"])

    # Save data to file
    save_data(decoded_data, DUMP_FILE + ".gz")

    # Decompress the gzipped SQL file
    decompress_gzip_file(DUMP_FILE + ".gz", DUMP_FILE)
    
    # Import the SQL file into PostgreSQL
    import_sql_to_postgres(DUMP_FILE)
    
    # Extract SSNs where status is 'alive'
    alive_ssns = get_alive_ssns()

    # Create JSON response with alive_ssns as a list
    solution = {
        "alive_ssns": alive_ssns
    }
    
    if DEBUG_MODE:
        print(f"Solution: {solution}")
    
    # Submit the solution
    result = solve_problem(solution)
    print(f"\nResult: {result}")
    
    # Clean up temporary files
    if DEBUG_MODE:
        print("Skipping cleanup of temporary files in debug mode")
    else:
        cleanup()


if __name__ == "__main__":
    main()