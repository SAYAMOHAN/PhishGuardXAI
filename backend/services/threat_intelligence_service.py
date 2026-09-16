import os
import base64
import requests
from dotenv import load_dotenv


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)

OPENPHISH_FEED_PATH = os.path.join(
    BASE_DIR,
    "data",
    "openphish_feed.txt"
)


# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv(os.path.join(PROJECT_DIR, ".env"))

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")


# --------------------------------------------------
# PhishTank
# --------------------------------------------------

def check_phishtank(url):

    api_url = "http://checkurl.phishtank.com/checkurl/"

    headers = {
        "User-Agent": "PhishGuardAI/1.0"
    }

    data = {
        "url": url,
        "format": "json"
    }

    try:

        response = requests.post(
            api_url,
            data=data,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:

            return {
                "available": False,
                "is_malicious": False,
                "message": f"PhishTank returned HTTP {response.status_code}"
            }

        result = response.json()

        result_data = result.get("results", {})

        in_database = (
            str(
                result_data.get(
                    "in_database",
                    ""
                )
            ).lower() == "true"
        )

        return {
            "available": True,
            "is_malicious": in_database,
            "phish_id": result_data.get("phish_id"),
            "verified": result_data.get("verified"),
            "valid": result_data.get("valid"),
            "message": (
                "URL found in PhishTank"
                if in_database
                else "URL not found in PhishTank"
            )
        }

    except requests.RequestException as e:

        return {
            "available": False,
            "is_malicious": False,
            "message": f"PhishTank request failed: {str(e)}"
        }


# --------------------------------------------------
# VirusTotal
# --------------------------------------------------

def check_virustotal(url):

    if not VIRUSTOTAL_API_KEY:

        return {
            "available": False,
            "is_malicious": False,
            "message": "VirusTotal API key not configured"
        }

    url_id = base64.urlsafe_b64encode(
        url.encode()
    ).decode().strip("=")

    api_url = (
        f"https://www.virustotal.com/api/v3/urls/{url_id}"
    )

    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }

    try:

        response = requests.get(
            api_url,
            headers=headers,
            timeout=15
        )

        if response.status_code == 404:

            return {
                "available": True,
                "is_malicious": False,
                "message": "URL has not been analyzed by VirusTotal"
            }

        if response.status_code in [401, 403]:

            return {
                "available": False,
                "is_malicious": False,
                "message": (
                    "VirusTotal authorization failed: "
                    f"HTTP {response.status_code}"
                )
            }

        if response.status_code != 200:

            return {
                "available": False,
                "is_malicious": False,
                "message": (
                    f"VirusTotal returned HTTP "
                    f"{response.status_code}"
                )
            }

        result = response.json()

        attributes = result.get(
            "data",
            {}
        ).get(
            "attributes",
            {}
        )

        stats = attributes.get(
            "last_analysis_stats",
            {}
        )

        malicious = stats.get(
            "malicious",
            0
        )

        suspicious = stats.get(
            "suspicious",
            0
        )

        is_malicious = (
            malicious > 0
            or suspicious > 0
        )

        return {
            "available": True,
            "is_malicious": is_malicious,
            "malicious": malicious,
            "suspicious": suspicious,
            "harmless": stats.get("harmless", 0),
            "undetected": stats.get("undetected", 0),
            "message": (
                "VirusTotal detected the URL as malicious"
                if is_malicious
                else "VirusTotal did not detect the URL as malicious"
            )
        }

    except requests.RequestException as e:

        return {
            "available": False,
            "is_malicious": False,
            "message": f"VirusTotal request failed: {str(e)}"
        }


# --------------------------------------------------
# OpenPhish
# --------------------------------------------------

def check_openphish(url):

    if not os.path.exists(OPENPHISH_FEED_PATH):

        return {
            "available": False,
            "is_malicious": False,
            "message": "OpenPhish feed file not found"
        }

    try:

        with open(
            OPENPHISH_FEED_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            feed_urls = {
                line.strip()
                for line in file
                if line.strip()
            }

        is_malicious = url.strip() in feed_urls

        return {
            "available": True,
            "is_malicious": is_malicious,
            "message": (
                "URL found in OpenPhish feed"
                if is_malicious
                else "URL not found in OpenPhish feed"
            )
        }

    except OSError as e:

        return {
            "available": False,
            "is_malicious": False,
            "message": f"OpenPhish feed error: {str(e)}"
        }


# --------------------------------------------------
# Combined Threat Intelligence
# --------------------------------------------------

def check_threat_intelligence(url):

    phishtank_result = check_phishtank(url)

    virustotal_result = check_virustotal(url)

    openphish_result = check_openphish(url)


    # --------------------------------------------------
    # Determine Threat Intelligence Sources
    # --------------------------------------------------

    sources = []

    if phishtank_result["is_malicious"]:
        sources.append("PhishTank")

    if virustotal_result["is_malicious"]:
        sources.append("VirusTotal")

    if openphish_result["is_malicious"]:
        sources.append("OpenPhish")


    is_malicious = len(sources) > 0


    # --------------------------------------------------
    # Final Result
    # --------------------------------------------------

    return {

        "url": url,

        "is_malicious": is_malicious,

        "sources": sources,

        "phishtank": phishtank_result,

        "virustotal": virustotal_result,

        "openphish": openphish_result,

        "message": (
            "URL detected by threat intelligence sources"
            if is_malicious
            else "URL not found in available threat intelligence sources"
        )
    }
