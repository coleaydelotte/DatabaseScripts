import json
import psycopg
from dotenv import load_dotenv
import sys
import os
from datetime import datetime

# Fetch database connection parameters from environment variables


# Function to parse date fields
def _parse_date(date_str):
    if date_str:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return None


# Function to insert document into the database
def insert_document(conn, json_data):
    # Parse the JSON data
    data = json.loads(json_data)

    # Extract relevant fields
    attributes = data["data"]["attributes"]
    document_id = data["data"]["id"]
    document_api_link = data["data"]["links"]["self"]

    # Prepare the values for insertion
    values = (
        document_id,
        document_api_link,
        attributes.get("address1"),
        attributes.get("address2"),
        attributes.get("agencyId"),
        attributes.get("allowLateComments"),
        _parse_date(attributes.get("authorDate")),
        attributes.get("category"),
        attributes.get("city"),
        attributes.get("comment"),
        _parse_date(attributes.get("commentEndDate")),
        _parse_date(attributes.get("commentStartDate")),
        attributes.get("country"),
        attributes.get("docketId"),
        attributes.get("documentType"),
        _parse_date(attributes.get("effectiveDate")),
        attributes.get("email"),
        attributes.get("fax"),
        attributes.get("field1"),
        attributes.get("field2"),
        attributes.get("firstName"),
        attributes.get("govAgency"),
        attributes.get("govAgencyType"),
        _parse_date(attributes.get("implementationDate")),
        attributes.get("lastName"),
        _parse_date(attributes.get("modifyDate")),
        attributes.get("openForComment"),
        attributes.get("organization"),
        attributes.get("phone"),
        _parse_date(attributes.get("postedDate")),
        _parse_date(attributes.get("postmarkDate")),
        attributes.get("reasonWithdrawn"),
        _parse_date(attributes.get("receiveDate")),
        attributes.get("regWriterInstruction"),
        attributes.get("restrictReason"),
        attributes.get("restrictReasonType"),
        attributes.get("stateProvinceRegion"),
        attributes.get("subtype"),
        attributes.get("title"),
        attributes.get("topics"),
        attributes.get("withdrawn"),
        attributes.get("zip"),
        attributes.get("frDocNum"),
    )

    # Insert into the database
    try:
        with conn.cursor() as cursor:
            insert_query = """
            INSERT INTO documents (
                document_id, document_api_link, address1, address2, agency_id,
                is_late_comment, author_date, comment_category, city, comment,
                comment_end_date, comment_start_date, country, docket_id,
                document_type, effective_date, email, fax, flex_field1,
                flex_field2, first_name, submitter_gov_agency, submitter_gov_agency_type,
                implementation_date, last_name, modify_date, is_open_for_comment,
                submitter_org, phone, posted_date, postmark_date, reason_withdrawn,
                receive_date, reg_writer_instruction, restriction_reason,
                restriction_reason_type, state_province_region, subtype,
                document_title, topics, is_withdrawn, postal_code, frdocnum
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, values)
            print(f"Document {document_id} inserted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Main function to read JSON from file and insert into the database
def main():
    if len(sys.argv) != 2:
        print("Usage: python IngestDocument.py <path_to_json_file>")
        sys.exit(1)

    json_file_path = sys.argv[1]

    load_dotenv()
    dbname = os.getenv("POSTGRES_DB")
    username = os.getenv("POSTGRES_USERNAME")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")

    conn_params = {
        "dbname": dbname,
        "user": username,
        "password": password,
        "host": host,
        "port": port,
    }
    try:
        with open(json_file_path, "r") as json_file:
            json_data = json_file.read()
            with psycopg.connect(**conn_params) as conn:
                insert_document(conn, json_data)
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print("Error decoding JSON from the file.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
