import os

import psycopg2
import psycopg2.extras

from dotenv import load_dotenv


# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PROJECT_DIR = os.path.dirname(BASE_DIR)

load_dotenv(
    os.path.join(
        PROJECT_DIR,
        ".env"
    )
)


# --------------------------------------------------
# Database Connection
# --------------------------------------------------

def get_connection():

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "PhishGuardDB"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )


# --------------------------------------------------
# Save Scan Result
# --------------------------------------------------

def save_scan(
    url,
    prediction,
    probability,
    confidence,
    risk_score,
    risk_level,
    threat_intelligence=None
):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO "ScanHistory"
        (
            url,
            prediction,
            probability,
            confidence,
            risk_score,
            risk_level,
            threat_intelligence,
            scan_time
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
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
            risk_level,
            psycopg2.extras.Json(threat_intelligence)
            if threat_intelligence is not None
            else None
        )
    )

    scan_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return scan_id


# --------------------------------------------------
# Get Scan History
# --------------------------------------------------

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
            threat_intelligence,
            scan_time
        FROM "ScanHistory"
        ORDER BY scan_time DESC;
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


# --------------------------------------------------
# Test Database
# --------------------------------------------------

if __name__ == "__main__":

    scan_id = save_scan(
        url="https://example.com",
        prediction="SAFE",
        probability=0.05,
        confidence=95.0,
        risk_score=5,
        risk_level="LOW",
        threat_intelligence={
            "is_malicious": False,
            "sources": [],
            "message": "Test threat intelligence result"
        }
    )

    print("Scan saved successfully!")
    print("Scan ID:", scan_id)

    history = get_history()

    print("\nScan History:")

    for row in history:
        print(row)
