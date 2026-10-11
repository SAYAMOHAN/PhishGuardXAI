
import re
from urllib.parse import urlparse

urls = [
    "https://www.wikipedia.org/",
    "http://paypal.com.security-check.example/login",
    "http://192.168.1.10/login",
    "http://example.com/path/https-check",
]

for url in urls:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    training_https = int(str(url).lower().startswith("https://"))
    backend_https = int(parsed.scheme.lower() == "https")

    training_ip = int(
        bool(re.search(r"(\d{1,3}\.){3}\d{1,3}", url))
    )
    backend_ip = int(
        bool(re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", hostname))
    )

    print("\nURL:", url)
    print("HTTPS — training:", training_https, "| backend:", backend_https)
    print("Has_IP — training:", training_ip, "| backend:", backend_ip)
