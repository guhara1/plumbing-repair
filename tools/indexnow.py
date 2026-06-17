#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexNow 즉시 색인 통보 — Bing · Naver · Yandex · Seznam 동시 전송.
(IndexNow 참여 검색엔진에 한 번에 통보됩니다. Google은 IndexNow 미참여 → google_index.py 사용)

사용:
  python3 tools/indexnow.py                 # sitemap.xml의 전체 URL 통보
  python3 tools/indexnow.py /area/seoul/    # 특정 URL만 통보(여러 개 가능)
  python3 tools/indexnow.py --new           # 최근 변경분만(직접 인자 전달 권장)

전제: 키 파일( <KEY>.txt )이 사이트 루트에 배포되어 접근 가능해야 합니다.
"""
import sys, json, os, glob, re, urllib.request

HOST = "plumbing-works.pages.dev"
SITE = f"https://{HOST}"
KEY = json.load(open(os.path.join(os.path.dirname(__file__), "indexnow_key.json")))["key"]
KEY_LOCATION = f"{SITE}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/IndexNow"   # 모든 참여 엔진으로 분배

def sitemap_urls():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sm = os.path.join(root, "sitemap.xml")
    return re.findall(r"<loc>(.*?)</loc>", open(sm, encoding="utf-8").read())

def to_abs(u):
    if u.startswith("http"): return u
    return SITE + (u if u.startswith("/") else "/" + u)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    urls = [to_abs(a) for a in args] if args else sitemap_urls()
    # IndexNow 1회 최대 10,000 URL
    urls = urls[:10000]
    payload = {"host": HOST, "key": KEY, "keyLocation": KEY_LOCATION, "urlList": urls}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=data,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow 전송 완료: {len(urls)} URL · HTTP {r.status}")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
        print("→ 200/202가 아니면 키 파일이 아직 배포 안 됐을 수 있습니다(배포 후 재시도).")

if __name__ == "__main__":
    main()
