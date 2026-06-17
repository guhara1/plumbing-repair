#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Indexing API — URL 색인 즉시 통보(URL_UPDATED) / 삭제(URL_DELETED).
Google은 IndexNow 미참여이므로 별도로 사용합니다.

사전 준비(최초 1회):
  1) Google Cloud Console에서 프로젝트 생성 → "Indexing API" 사용 설정
  2) 서비스 계정 생성 → JSON 키 다운로드 → tools/google_sa.json 으로 저장
  3) Search Console에서 해당 사이트 속성에 서비스 계정 이메일을
     '소유자(Owner)'로 추가
  4) 의존성 설치:  pip install google-auth requests

사용:
  python3 tools/google_index.py /area/seoul/ /service/sewer-clog.html
  python3 tools/google_index.py --from-sitemap         # sitemap 전체(쿼터 200/일 주의)
  python3 tools/google_index.py --delete /old-page.html

※ 공식적으로는 JobPosting/BroadcastEvent 대상이지만 일반 URL에도 널리 사용됩니다.
   일일 쿼터(기본 200건)에 유의하세요.
"""
import sys, os, re, json

SITE = "https://plumbing-works.pages.dev"
SA_FILE = os.path.join(os.path.dirname(__file__), "google_sa.json")
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

def to_abs(u):
    if u.startswith("http"): return u
    return SITE + (u if u.startswith("/") else "/" + u)

def sitemap_urls():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sm = os.path.join(root, "sitemap.xml")
    return re.findall(r"<loc>(.*?)</loc>", open(sm, encoding="utf-8").read())

def main():
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        print("의존성 필요:  pip install google-auth requests"); return
    if not os.path.exists(SA_FILE):
        print(f"서비스 계정 키가 없습니다: {SA_FILE} (README 참고)"); return

    args = sys.argv[1:]
    op = "URL_DELETED" if "--delete" in args else "URL_UPDATED"
    args = [a for a in args if not a.startswith("--")]
    urls = sitemap_urls() if "--from-sitemap" in sys.argv else [to_abs(a) for a in args]
    if not urls:
        print("통보할 URL을 인자로 주거나 --from-sitemap 을 사용하세요."); return

    creds = service_account.Credentials.from_service_account_file(SA_FILE, scopes=SCOPES)
    session = AuthorizedSession(creds)
    ok = 0
    for u in urls[:200]:   # 일일 쿼터 보호
        r = session.post(ENDPOINT, json={"url": u, "type": op})
        if r.status_code == 200: ok += 1
        else: print(f"  ! {r.status_code} {u}: {r.text[:160]}")
    print(f"Google Indexing API 통보 완료: {ok}/{min(len(urls),200)} ({op})")

if __name__ == "__main__":
    main()
