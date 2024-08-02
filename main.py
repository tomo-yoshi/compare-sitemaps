import requests
import xml.etree.ElementTree as ET
# from flask import request, jsonify
from flask import jsonify

def fetch_sitemap(url):
    response = requests.get(url)
    response.raise_for_status()
    return ET.fromstring(response.content)

def get_urls(sitemap):
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return {url.findtext('ns:loc', namespaces=namespaces) for url in sitemap.findall('.//ns:url', namespaces)}

def compare_sitemaps(request):
    try:
        request_json = request.get_json(silent=True)
        prod_url = request_json.get('prodUrl') + "/sitemap.xml"
        prev_url = request_json.get('prevUrl') + "/sitemap.xml"

        if not prod_url or not prev_url:
            return jsonify(error="Missing 'prodUrl' or 'prevUrl' parameter"), 400

        prod_sitemap = fetch_sitemap(prod_url)
        prev_sitemap = fetch_sitemap(prev_url)

        prod_urls = get_urls(prod_sitemap)
        prev_urls = get_urls(prev_sitemap)

        added_urls = prev_urls - prod_urls
        removed_urls = prod_urls - prev_urls

        return jsonify(added_urls=list(added_urls), removed_urls=list(removed_urls))

    except Exception as e:
        return jsonify(error=f"Error processing sitemaps: {str(e)}"), 500
