import psycopg2


def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="PhishGuardDB",
        user="postgres",
        password="Post123"
    )


def save_scan(
    url,
    prediction,
    probability,
    confidence,
    risk_score,
    risk_level
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO "ScanHistory"
        (url, prediction, probability, confidence, risk_score, risk_level, scan_time)
        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING id;
    """

    cursor.execute(
        query,
        (
            url,
            prediction,
            probability,
            confidence,
            risk_score,
            risk_level
        )
    )

    scan_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return scan_id


def get_history():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            id,
            url,
            prediction,
            probability,
            confidence,
            risk_score,
            risk_level,
            scan_time
        FROM "ScanHistory"
        ORDER BY scan_time DESC;
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
if __name__ == "__main__":
    scan_id = save_scan(
        url="https://example.com",
        prediction="SAFE",
        probability=0.05,
        confidence=95.0,
        risk_score=5,
        risk_level="LOW"
    )

    print("Scan saved successfully!")
    print("Scan ID:", scan_id)

    history = get_history()

    print("\nScan History:")
    for row in history:
        print(row)