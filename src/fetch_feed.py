import urllib.request
import xml.etree.ElementTree as ET
from urllib.error import URLError


def fetch_feed(url: str, limit: int = 5):
    headers = {
        'User-Agent': 'Python-Feed-Fetcher/1.0'
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            xml_data = res.read()

    except URLError as e:
        print(f"取得エラー: {e}")
        return

    # XMLパース
    root = ET.fromstring(xml_data)

    # RSS/Atomの判別と抽出
    if root.tag == 'rss':
        parse_rss(root, limit)
    elif root.tag == 'feed':
        pass
    else:
        print(f"不明なフィード形式です: {root.tag}")

def parse_rss(root: ET.Element, limit: int):
    """RSS 2.0を解析する"""
    channel = root.find("channel")
    if channel is None:
        return

    site_title = channel.findtext("title", "No Title")
    print(f"=== {site_title} (RSS 2.0) ===\n")

    items = channel.findall("item")[:limit]
    for item in items:
        title = item.findtext("title", "No Title").strip()
        link = item.findtext("link", "").strip()
        pub_date = item.findtext("pubDate", "").strip()

        print(f"タイトル: {title}")
        print(f"リンク: {link}")
        if pub_date:
            print(f"公開日: {pub_date}")
        print("-" * 40)

def parse_atom(root: ET.Element, limit: int):
    """Atomを解析する"""
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    site_title = root.findtext("atom:title", "No Title", namespaces=ns)
    print(f"=== {site_title} (Atom) ===\n")

    entries = root.findall("atom:entry", namespaces=ns)[:limit]
    for entry in entries:
        title = entry.findtext("atom:title", "No Title", namespaces=ns).strip()
        link_elem = entry.find("atom:link", namespaces=ns)
        link = (
            link_elem.attrib.get("href", "") if link_elem is not None else ""
        )
        pub_date = entry.findtext(
            "atom:published",
            entry.findtext("atom:updated", "", namespaces=ns),
            namespaces=ns
        ).strip()

        print(f"タイトル: {title}")
        print(f"リンク: {link}")
        if pub_date:
            print(f"公開日: {pub_date}")
        print("-" * 40)

if __name__ == "__main__":
    # 動作確認用URL
    sample_url = "https://www.nhk.or.jp/rss/news/cat0.xml"
    fetch_feed(sample_url, limit=3)
