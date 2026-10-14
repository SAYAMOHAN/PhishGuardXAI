
from database.database import get_connection

conn = None
cursor = None

try:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            prediction,
            probability,
            confidence,
            risk_score,
            risk_level,
            threat_intelligence IS NOT NULL,
            shap_evidence IS NOT NULL,
            model_disagreement IS NOT NULL,
            scan_time
        FROM "ScanHistory"
        ORDER BY scan_time DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    if row:
        print("Latest scan record:")
        print("ID:", row[0])
        print("Prediction:", row[1])
        print("Probability:", row[2])
        print("Confidence:", row[3])
        print("Risk score:", row[4])
        print("Risk level:", row[5])
        print("Threat intelligence saved:", row[6])
        print("SHAP evidence saved:", row[7])
        print("Model disagreement saved:", row[8])
        print("Scan time:", row[9])
    else:
        print("No scan records found.")

except Exception as error:
    print("Database check failed:", error)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
