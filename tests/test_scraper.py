from modules.scraper import _jsonld
from bs4 import BeautifulSoup


def test_reads_jobposting_jsonld():
    soup = BeautifulSoup('''<script type="application/ld+json">{"@type":"JobPosting","title":"Design Intern","hiringOrganization":{"name":"Acme"},"description":"A detailed design internship description."}</script>''', "html.parser")
    extracted = _jsonld(soup)
    assert extracted["title"] == "Design Intern"
    assert extracted["company"] == "Acme"
