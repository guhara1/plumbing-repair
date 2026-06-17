# 색인(인덱싱) 빠르게 만들기 — 운영 가이드

도메인: `https://plumbing-works.pages.dev`

## 0. 한눈에
| 채널 | 방법 | 즉시성 |
|------|------|--------|
| **Bing · Naver · Yandex** | IndexNow (`tools/indexnow.py`) | 즉시 통보 |
| **Google** | Indexing API (`tools/google_index.py`) + Search Console | 빠름 |
| 공통 | `sitemap.xml` + `rss.xml` 제출 | 표준 |

> ⚠️ **sitemap ping은 중단됨**: Google은 2023년 6월 sitemap ping 엔드포인트를 폐지했고, Bing도 IndexNow 사용을 권장합니다. 그래서 ping 대신 **IndexNow + Indexing API + 콘솔 제출**로 구성했습니다.

---

## 1. IndexNow (Bing·Naver·Yandex 즉시 색인)
- 키: `tools/indexnow_key.json` 에 저장, 키 파일은 사이트 루트 `/<KEY>.txt` 로 배포됨(검증용).
- 글/페이지를 올리거나 수정할 때마다 실행:

```bash
# 전체(sitemap 기준) 통보
python3 tools/indexnow.py

# 특정 URL만 통보(권장 — 변경분만)
python3 tools/indexnow.py /area/seoul/gangnam-gu/ /service/sewer-clog.html
```
- 응답 200/202 = 접수 성공. **키 파일이 배포된 뒤** 실행해야 합니다.

## 2. Google Indexing API (구글 즉시 통보)
최초 1회 세팅:
1. Google Cloud Console → 프로젝트 → **Indexing API** 사용 설정
2. **서비스 계정** 생성 → JSON 키 다운로드 → `tools/google_sa.json` 로 저장
3. **Search Console**에서 사이트 속성에 서비스 계정 이메일을 **소유자**로 추가
4. `pip install google-auth requests`

사용:
```bash
python3 tools/google_index.py /area/seoul/ /service/plumbing.html
python3 tools/google_index.py --from-sitemap     # 전체(일 200건 쿼터 주의)
```

## 3. 검색엔진 콘솔 등록(최초 1회, 가장 중요)
- **네이버 서치어드바이저**: 사이트 등록 → 소유확인(이미 메타 적용됨) → 사이트맵 제출 `https://plumbing-works.pages.dev/sitemap.xml` → RSS 제출 `…/rss.xml`
- **구글 서치콘솔**: 속성 등록 → 소유확인 → 사이트맵 제출(동일)
- **Bing 웹마스터도구**: 사이트 등록 → 사이트맵 제출(+IndexNow 자동 연동)

## 4. 배포 후 1회 권장 절차
```bash
# (배포 완료 확인 후)
python3 tools/indexnow.py            # Bing·Naver 전체 통보
python3 tools/google_index.py --from-sitemap   # 구글(세팅 완료 시)
```

## 파일
- `/<KEY>.txt` — IndexNow 키 검증 파일(루트)
- `/sitemap.xml` — 전체 URL 사이트맵
- `/rss.xml` — 주요 페이지 RSS 피드
- `/robots.txt` — 크롤러 허용 + 사이트맵 위치
