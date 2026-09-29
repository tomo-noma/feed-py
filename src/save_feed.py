import csv
import json
import urllib.request
import xml.etree.ElementTree as ET
from urllib.error import URLError


def fetch_and_parse_feed(url: str, limit: int = 10) -> list[dict[str, str]]:
    """フィードを取得し、辞書のリストとして返す"""
    headers = {"User-Agent": "Python-Feed-Fetcher/1.0"}
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            xml_data = res.read()
    except URLError as e:
        print(f"取得エラー: {e}")
        return []

    root = ET.fromstring(xml_data)
    items_data = []

    # RSS 2.0 の場合
    if root.tag == "rss":
        channel = root.find("channel")
        if channel is not None:
            for item in channel.findall("item")[:limit]:
                items_data.append(
                    {
                        "title": item.findtext("title", "").strip(),
                        "link": item.findtext("link", "").strip(),
                        "pub_date": item.findtext("pubDate", "").strip(),
                    }
                )

    # Atom の場合
    elif "feed" in root.tag:
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", namespaces=ns)[:limit]:
            # 公開日（published がなければ updated を参照）
            pub_date = entry.findtext(
                "atom:published",
                entry.findtext("atom:updated", "", namespaces=ns),
                namespaces=ns,
            ).strip()

            link_elem = entry.find("atom:link", namespaces=ns)
            link = (
                link_elem.attrib.get("href", "").strip()
                if link_elem is not None
                else ""
            )

            items_data.append(
                {
                    "title": entry.findtext(
                        "atom:title", "", namespaces=ns
                    ).strip(),
                    "link": link,
                    "pub_date": pub_date,
                }
            )

    return items_data

def save_to_json(data: list[dict[str, str]], filepath: str):
    """JSONファイルとして保存"""
    # ensure_ascii=False で日本語がエスケープ（\uXXXX）されるのを防ぐ
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSONファイルを保存しました: {filepath}")

def save_to_csv(data: list[dict[str, str]], filepath: str):
    """CSVファイルとして保存"""
    if not data:
        print("保存するデータがありません。")
        return

    # フィールド（列名）の定義
    fieldnames = ["title", "link", "pub_date"]

    # WindowsのExcel等で文字化けを防ぐ場合は 'utf-8-sig' を指定
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"CSVファイルを保存しました: {filepath}")

if __name__ == "__main__":
    # 動作確認用URL
    sample_url = "https://www.nhk.or.jp/rss/news/cat0.xml"

    # 1. フィード取得（上位5件）
    feed_items = fetch_and_parse_feed(sample_url, limit=5)

    if feed_items:
        # 2. JSON形式で保存
        save_to_json(feed_items, "feed_items.json")

        # 3. CSV形式で保存
        save_to_csv(feed_items, "feed_items.csv")
