import json


def insert_cfr_parts(conn, json_data: str) -> None:
    data = json.loads(json_data)
    document_number = data.get("document_number")
    if not document_number:
        return

    refs = data.get("cfr_references") or []
    inserted = 0

    with conn.cursor() as cursor:
        cursor.execute(
            "DELETE FROM federal_register_cfr_parts WHERE document_number = %s",
            (document_number,),
        )
        for ref in refs:
            if not isinstance(ref, dict):
                continue
            title = ref.get("title")
            part = ref.get("part")
            if title is None or part is None:
                continue
            cursor.execute(
                """
                INSERT INTO federal_register_cfr_parts (document_number, cfr_title, cfr_part)
                VALUES (%s, %s, %s)
                ON CONFLICT (document_number, cfr_title, cfr_part) DO NOTHING
                """,
                (document_number, str(title), str(part)),
            )
            inserted += 1
        print(f"CFR parts for {document_number}: {inserted} row(s) inserted.")
