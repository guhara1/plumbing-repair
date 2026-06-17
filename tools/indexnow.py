#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexNow 즉시 색인 통보 — Bing · Naver · Yandex 동시 전송.
(Google은 IndexNow 미참여 → tools/google_index.py 사용)

사용:
  python3 tools/indexnow.py                     # sitemap.xml 전체 URL 통보
  python3 tools/indexnow.py /area/seoul/        # 특정 URL만 통보 (여러 개 가능)

전제: 키 파일(<KEY>.txt)이 사이트 루트에 배포된 후 실행해야 합니다.
"""
import sys, json, os, re, urllib.request, urllib.error

HOST = "plumbing-repair.pages.dev"
SITE = f"https://{HOST}"

_key_file = os.path.join(os.path.dirname(__file__), "indexnow_key.json")
KEY = json.load(open(_key_file, encoding="utf-8"))["key"]
KEY_LOCATION = f"{SITE}/{KEY}.txt"

# IndexNow 참여 엔진별 엔드포인트 (api.indexnow.org는 참여 엔진 전체 분배)
ENDPOINTS = [
    ("Bing/IndexNow", "https://api.indexnow.org/IndexNow"),
    ("Naver",         "https://searchadvisor.naver.com/indexnow"),
    ("Yandex",        "https://yandex.com/indexnow"),
]

def sitemap_urls():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sm = os.path.join(root, "sitemap.xml")
    return re.findall(r"<loc>(.*?)</loc>", open(sm, encoding="utf-8").read())

def to_abs(u):
    if u.startswith("http"): return u
    return SITE + (u if u.startswith("/") else "/" + u)

def send(endpoint_name, endpoint_url, urls):
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint_url, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"  ✓ {endpoint_name}: {len(urls)} URL 전송 완료 (HTTP {r.status})")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:200]
        print(f"  ✗ {endpoint_name}: HTTP {e.code} — {body}")
        if e.code == 403:
            print("    → 키 파일이 아직 배포 안 됐거나 HOST가 다릅니다. 배포 후 재시도.")
    except Exception as e:
        print(f"  ✗ {endpoint_name}: {e}")

def main():
    raw_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    urls = [to_abs(a) for a in raw_args] if raw_args else sitemap_urls()
    urls = urls[:10000]  # IndexNow 1회 최대 10,000 URL

    print(f"IndexNow 통보 시작: {len(urls)} URL")
    print(f"키: {KEY}  |  키 파일: {KEY_LOCATION}\n")
    for name, ep in ENDPOINTS:
        send(name, ep, urls)

    print("\n완료. 200/202 = 접수 성공 · 422 = URL 형식 오류 · 403 = 키 미확인")

if __name__ == "__main__":
    main()
