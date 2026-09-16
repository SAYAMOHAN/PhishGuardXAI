from urllib.parse import urlparse
import re


FEATURE_NAMES = [
    "URL_Length",
    "No_of_Dots",
    "No_of_Hyphens",
    "No_of_Digits",
    "Has_HTTPS",
    "No_of_Slashes",
    "No_of_Underscores",
    "No_of_QuestionMarks",
    "No_of_EqualSigns",
    "No_of_At",
    "Has_IP"
]


def extract_features(url):
    """
    Extract the 11 lexical features expected by the
    existing LightGBM model.
    """

    parsed = urlparse(url)

    features = {}

    features["URL_Length"] = len(url)

    features["No_of_Dots"] = url.count(".")

    features["No_of_Hyphens"] = url.count("-")

    features["No_of_Digits"] = sum(char.isdigit() for char in url)

    features["Has_HTTPS"] = 1 if parsed.scheme.lower() == "https" else 0

    features["No_of_Slashes"] = url.count("/")

    features["No_of_Underscores"] = url.count("_")

    features["No_of_QuestionMarks"] = url.count("?")

    features["No_of_EqualSigns"] = url.count("=")

    features["No_of_At"] = url.count("@")

    hostname = parsed.hostname or ""

    # Detect IPv4 address
    ip_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"

    features["Has_IP"] = 1 if re.match(ip_pattern, hostname) else 0

    return features


if __name__ == "__main__":
    test_url = "https://example.com/login?id=123"

    result = extract_features(test_url)

    print("URL:", test_url)
    print("\nExtracted Features:")

    for feature in FEATURE_NAMES:
        print(f"{feature}: {result[feature]}")
