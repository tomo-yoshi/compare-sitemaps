from flask import Flask
from main import compare_sitemaps

app = Flask(__name__)

@app.route('/compare-sitemaps', methods=['POST'])
def handle_compare_sitemaps():
    return compare_sitemaps()

if __name__ == '__main__':
    app.run(debug=True)