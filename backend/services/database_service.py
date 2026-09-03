from database.database import (
    save_scan,
    get_history,
    get_connection
)


# --------------------------------------------------
# Save Scan Result
# --------------------------------------------------

def save_scan_result(
    url,
    prediction,
    probability,
    confidence,
    risk_score,
    risk_level,
    threat_intelligence=None
):

    return save_scan(
        url=url,
        prediction=prediction,
        probability=probability,
        confidence=confidence,
        risk_score=risk_score,
        risk_level=risk_level,
        threat_intelligence=threat_intelligence
    )


# --------------------------------------------------
# Get Scan History
# --------------------------------------------------

def get_scan_history():

    return get_history()


# --------------------------------------------------
# Get Dashboard Statistics
# --------------------------------------------------

def get_scan_statistics():

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            COUNT(*) AS total_scans,

            COUNT(*) FILTER (
                WHERE prediction = 'PHISHING'
            ) AS phishing_count,

            COUNT(*) FILTER (
                WHERE prediction = 'SAFE'
            ) AS safe_count,

            COUNT(*) FILTER (
                WHERE risk_level = 'CRITICAL'
            ) AS critical_count,

            COUNT(*) FILTER (
                WHERE risk_level = 'HIGH'
            ) AS high_count,

            COUNT(*) FILTER (
                WHERE risk_level = 'MEDIUM'
            ) AS medium_count,

            COUNT(*) FILTER (
                WHERE risk_level = 'LOW'
            ) AS low_count

        FROM "ScanHistory";
    """

    cursor.execute(query)

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "total_scans": row[0],
        "phishing_count": row[1],
        "safe_count": row[2],
        "critical_count": row[3],
        "high_count": row[4],
        "medium_count": row[5],
        "low_count": row[6]
    }


# --------------------------------------------------
# Get Recent Phishing Scans
# --------------------------------------------------

def get_recent_phishing_scans(limit=10):

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
        WHERE prediction = 'PHISHING'
        ORDER BY scan_time DESC
        LIMIT %s;
    """

    cursor.execute(query, (limit,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


# --------------------------------------------------
# Save User Report
# --------------------------------------------------

def save_user_report(url, reason=None):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO "UserReports"
        (
            url,
            reason
        )
        VALUES (%s, %s)
        RETURNING id;
    """

    cursor.execute(
        query,
        (
            url,
            reason
        )
    )

    report_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return report_id


# --------------------------------------------------
# Get User Reports
# --------------------------------------------------

def get_user_reports():

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            id,
            url,
            reason,
            report_status,
            reported_at
        FROM "UserReports"
        ORDER BY reported_at DESC;
    """

    cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows
