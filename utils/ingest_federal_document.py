import json


def insert_federal_document(conn, json_data):
    data = json.loads(json_data)

    document_number = data.get("document_number")
    if not document_number:
        raise ValueError("Federal Register document JSON missing 'document_number'")

    docket_ids_raw = data.get("docket_ids") or []
    docket_ids = [d.get("id") if isinstance(d, dict) else d for d in docket_ids_raw]

    agency_names_raw = data.get("agencies") or []
    agency_names = [a.get("name") for a in agency_names_raw if isinstance(a, dict) and a.get("name")]
    agency_id = None
    if agency_names_raw:
        first = agency_names_raw[0]
        if isinstance(first, dict):
            agency_id = first.get("id") or first.get("slug")

    cfr_refs = data.get("cfr_references") or []
    title = None
    cfrpart = None
    if cfr_refs:
        first_ref = cfr_refs[0]
        title = str(first_ref.get("title")) if first_ref.get("title") is not None else None
        if first_ref.get("part") is not None:
            cfrpart = str(first_ref["part"])

    values = (
        document_number,
        data.get("document_number"),
        data.get("title"),
        data.get("type"),
        data.get("abstract"),
        data.get("publication_date"),
        data.get("effective_on"),
        docket_ids if docket_ids else None,
        str(agency_id) if agency_id is not None else None,
        agency_names if agency_names else None,
        data.get("topics") or None,
        data.get("significant"),
        data.get("regulation_id_numbers") or None,
        data.get("html_url"),
        data.get("pdf_url"),
        data.get("json_url"),
        data.get("start_page"),
        title,
        cfrpart,
        data.get("end_page"),
    )

    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO federal_register_documents (
            document_number, document_id, document_title, document_type,
            abstract, publication_date, effective_on, docket_ids,
            agency_id, agency_names, topics, significant,
            regulation_id_numbers, html_url, pdf_url, json_url,
            start_page, title, cfrpart, end_page
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (document_number) DO UPDATE
        SET
            document_id = EXCLUDED.document_id,
            document_title = EXCLUDED.document_title,
            document_type = EXCLUDED.document_type,
            abstract = EXCLUDED.abstract,
            publication_date = EXCLUDED.publication_date,
            effective_on = EXCLUDED.effective_on,
            docket_ids = EXCLUDED.docket_ids,
            agency_id = EXCLUDED.agency_id,
            agency_names = EXCLUDED.agency_names,
            topics = EXCLUDED.topics,
            significant = EXCLUDED.significant,
            regulation_id_numbers = EXCLUDED.regulation_id_numbers,
            html_url = EXCLUDED.html_url,
            pdf_url = EXCLUDED.pdf_url,
            json_url = EXCLUDED.json_url,
            start_page = EXCLUDED.start_page,
            title = EXCLUDED.title,
            cfrpart = EXCLUDED.cfrpart,
            end_page = EXCLUDED.end_page;
        """
        cursor.execute(insert_query, values)
        print(f"Federal register document {document_number} inserted successfully.")
