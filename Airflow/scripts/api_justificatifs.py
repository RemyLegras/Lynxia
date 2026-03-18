import os
import re
import requests
from urllib.parse import urlparse, unquote, urlsplit, urlunsplit, parse_qsl, urlencode

API_URL = "https://intranet.myleasy.com/api/ndf/extract"
BASE_FILE_URL = "https://intranet.myleasy.com/api/ndf/"
API_TOKEN = os.environ.get("API_TOKEN")


def sanitize_filename(filename: str) -> str:
    filename = unquote(filename)
    filename = re.sub(r'[<>:"/\\\\|?*]+', "_", filename)
    filename = filename.strip().strip(".")
    return filename or "document.bin"


def get_filename_from_url(url: str, index: int) -> str:
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)

    if not filename:
        filename = f"justificatif_{index}.bin"

    return sanitize_filename(filename)


def get_unique_path(directory: str, filename: str) -> str:
    base, ext = os.path.splitext(filename)
    path = os.path.join(directory, filename)
    counter = 1

    while os.path.exists(path):
        path = os.path.join(directory, f"{base}_{counter}{ext}")
        counter += 1

    return path


def add_api_token_to_url(url: str, token: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["api_token"] = token
    new_query = urlencode(query)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))


def build_justificatif_url(justificatif_value: str, token: str) -> str:
    justificatif_value = str(justificatif_value).strip()

    if justificatif_value.startswith("http://") or justificatif_value.startswith("https://"):
        return add_api_token_to_url(justificatif_value, token)

    if justificatif_value.startswith("/"):
        return add_api_token_to_url(f"https://intranet.myleasy.com{justificatif_value}", token)

    return add_api_token_to_url(f"{BASE_FILE_URL}{justificatif_value}", token)


def extract_items(payload):
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        if isinstance(payload.get("results"), list):
            return payload["results"]
        if isinstance(payload.get("data"), list):
            return payload["data"]

    raise ValueError("Format JSON non supporté")


def get_next_url(payload):
    if isinstance(payload, dict):
        return payload.get("next")
    return None


def fetch_Api_justificatifs(output_dir="/opt/airflow/output_pdf"):
    if not API_TOKEN:
        raise ValueError("API_TOKEN manquant")

    os.makedirs(output_dir, exist_ok=True)

    session = requests.Session()
    session.headers.update({"Accept": "application/json"})

    next_url = add_api_token_to_url(API_URL, API_TOKEN)

    downloaded_files = []

    while next_url:
        print(f"Appel API : {next_url}")
        response = session.get(next_url, timeout=60)
        response.raise_for_status()

        payload = response.json()
        items = extract_items(payload)

        for i, item in enumerate(items, start=1):
            justificatif_value = item.get("justificatif_url")

            if not justificatif_value:
                continue

            file_url = build_justificatif_url(justificatif_value, API_TOKEN)
            filename = get_filename_from_url(file_url, i)
            output_path = get_unique_path(output_dir, filename)

            print(f"Téléchargement : {file_url}")
            file_response = session.get(file_url, timeout=120, stream=True)
            file_response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in file_response.iter_content(8192):
                    if chunk:
                        f.write(chunk)

            downloaded_files.append(output_path)

        raw_next_url = get_next_url(payload)
        if raw_next_url:
            next_url = add_api_token_to_url(raw_next_url, API_TOKEN)
        else:
            next_url = None

    print(f"Total téléchargés : {len(downloaded_files)}")

    return downloaded_files


if __name__ == "__main__":
    fetch_Api_justificatifs("./output_test")