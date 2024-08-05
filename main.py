import logging
import requests
from requests.exceptions import HTTPError, RequestException
import re
import os
import xml.etree.ElementTree as ET
from typing import Optional, Set
from flask import jsonify

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

ALLOWED_ORIGINS = [
    "https://api.github.com",
]

logging.basicConfig(level=logging.INFO)

def is_allowed_origin(origin: str):
    if not origin:
        return False
    for allowed_origin in ALLOWED_ORIGINS:
        if origin.startswith(allowed_origin):
            return True
    return False

def check_keywords(comment_body: str):
    keywords = ["tommy", "compare", "sitemap"]
    return all(keyword in comment_body.lower() for keyword in keywords)

def extract_first_url(text: str) -> Optional[str]:
    url_pattern = r'https?://(?:www\.)?\w+(?:[\w\-._~:/?#[\]@!$&\'()*+,;%=]*)'
    
    match = re.search(url_pattern, text)
    
    return match.group(0) if match else None

def find_url(text: str):
    if "canadiantrainvacations" in text:
        return "https://canadiantrainvacations.com"
    elif "canadapolarbears" in text:
        return "https://canadapolarbears.com"
    elif "northernlightscanada" in text:
        return "https://northernlightscanada.com"
    elif "freshtrackscanada" in text:
        return "https://freshtrackscanada.com"
    else:
        return None

def fetch_sitemap(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        logging.info(f"Sitemap fetched successfully from {url}")
        return ET.fromstring(response.content)
    except HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        raise
    except RequestException as req_err:
        logging.error(f"Request error occurred: {req_err}")
        raise
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        raise

def get_urls(sitemap: ET.Element) -> Set[str]:
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return {url.findtext('ns:loc', namespaces=namespaces) for url in sitemap.findall('.//ns:url', namespaces)}

def post_github_comment(owner, repo, issue_number, comment):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {"body": comment}
    requests.post(url, headers=headers, json=data)

def compare_sitemaps(request):
    """Main function for comparing sitemaps."""

    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set")

    payload = request.json

    if not is_allowed_origin(payload['issue']['url']):
        return jsonify({"message": "Forbidden"}), 403

    event = request.headers.get('X-GitHub-Event')

    try:
        if event != "issue_comment":
            logging.error("Invalid event")
            return jsonify(error="Invalid event"), 400
                
        comment_body = payload['comment']['body']
        repo_owner = payload['repository']['owner']['login']
        repo_name = payload['repository']['name']
        issue_number = payload['issue']['number']

        if not check_keywords(comment_body):
            logging.error("No Keywords found")
            return jsonify(error="No Keywords found"), 400
                    
        prev_url = extract_first_url(comment_body)

        base_url = find_url(prev_url)

        if not prev_url or not base_url:
            logging.error("Invalid URL")
            return jsonify(error="Invalid URL"), 400
                
        prev_url += "/sitemap.xml"
        base_url += "/sitemap.xml"

        base_sitemap = fetch_sitemap(base_url)
        prev_sitemap = fetch_sitemap(prev_url)

        base_urls = get_urls(base_sitemap)
        prev_urls = get_urls(prev_sitemap)

        added_urls = prev_urls - base_urls
        removed_urls = base_urls - prev_urls

        if added_urls:
            added_urls_list = "\n".join([f"- {url}" for url in added_urls])
        else:
            added_urls_list = "No URLs are added."

        if removed_urls:
            removed_urls_list = "\n".join([f"- {url}" for url in removed_urls])
        else:
            removed_urls_list = "No URLs are removed."

        comment = (
            f"**👉 Number of Pages in Sitemaps:**\n- {base_url} ({len(base_urls)})\n- {prev_url} ({len(base_urls)} + {len(added_urls)} - {len(removed_urls)} = **{len(prev_urls)}**)\n\n"
            f"**📈 Added URLs ({len(added_urls)}):**\n{added_urls_list}\n\n"
            f"**📉 Removed URLs ({len(removed_urls)}):**\n{removed_urls_list}\n\n"
        )
        post_github_comment(repo_owner, repo_name, issue_number, comment)

        return jsonify({"message": "Sitemaps comparison was processed."}), 200

    except Exception as e:
        return jsonify(error=f"Error processing sitemaps: {str(e)}"), 500
