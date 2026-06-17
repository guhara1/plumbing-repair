# 스피드 배관공사 (SPEED PLUMBING) — 사이트 구성 개요

도메인: https://plumbing-works.pages.dev
정적 HTML/CSS/소량 JS. 빌드 도구 없이 바로 열리는 구조(`build.py` + `pages.py`로 생성).

---

## 1. 상단 메뉴(GNB) · 하위메뉴 구성
```
홈 ( / )
서비스안내 ▾ ( /service/ )
 ├ 하수구막힘        /service/sewer-clog.html
 ├ 배관공사          /service/plumbing.html
 ├ 누수탐지          /service/leak-detection.html
 ├ 고압세척          /service/high-pressure.html
 ├ CCTV 관로검사      /service/cctv.html
 └ 전체 서비스 보기   /service/
지역별 서비스 ▾ ( /area/ )
 ├ 서울특별시        /area/seoul/
 ├ 경기도            /area/gyeonggi/
 ├ 부산광역시        /area/busan/
 └ 전국 지역 보기     /area/
시공사례             /cases.html
요금안내             /price.html
고객후기             /review.html
자주묻는질문          /faq.html
회사소개 ▾ ( /about.html )
 ├ 회사소개          /about.html
 └ 상담문의          /contact.html
[광고문의] (헤더 골드 버튼)  → https://t.me/googleseolab
```
- 헤더 우측: ☎ 24시간 전화(0000-0000) · 광고문의 버튼
- 모바일 하단 고정바: [전화][카톡][광고문의]
- 광고주 모집 팝업(로드 10초 후, 하루 1회)

---

## 2. 전체 페이지 구조(사이트맵)
```
/                         홈(메인)
/service/                 서비스 인덱스 + 상세 5종
/area/                    지역 인덱스
  /area/{시도}/            17개 시·도
    /area/{시도}/{시군구}/   228개 시·군·구(전국)
      …/{행정동}/           약 2,800개 행정동(전국)
/area/seoul/gangnam-gu/   강남구(고유 콘텐츠) + 14개 동
/area/seoul/seocho-gu/    서초구 + 7개 동
/area/seoul/songpa-gu/    송파구 + 13개 동
/area/seoul/gangdong-gu/  강동구 + 9개 동
/area/seoul/mapo-gu/      마포구 + 13개 동
/area/seoul/yeongdeungpo-gu/ 영등포구 + 8개 동
/cases.html /price.html /review.html /faq.html /about.html /contact.html
/privacy.html /terms.html /404.html
/sitemap.xml /rss.xml /robots.txt /{indexnow키}.txt
```
- 총 3,082개 HTML 페이지

---

## 3. 메인페이지 섹션 순서
1. 헤더(고정) — 로고·GNB·전화·광고문의
2. 히어로 — 좌측 텍스트 + 우측 16:9 이미지(배너), CTA(전화/광고문의)
3. 신뢰 리본 — 24시간·선견적·세금계산서·A/S보증·후기
4. 핵심 신뢰 4분할
5. 서비스 카드 8종
6. 지역 검색 블록(17개 시·도)
7. 작업 진행 5단계
8. 요금 미리보기
9. 시공사례 Before/After
10. 고객 후기
11. 네이버 채널 연동(플레이스·블로그·톡톡)
12. FAQ(아코디언, 구조화 데이터)
13. 하단 CTA 배너
14. 푸터(사업자정보·메뉴·지역·공식채널·광고문의)

---

## 4. 디자인 시스템(브랜드 키트)
컬러 토큰:
- `--navy #0B2545` (주색·헤더/푸터/딥 배경)
- `--ink #08182F` (그라데이션 끝)
- `--steel #2A7DE1` / `--steel-dark #1A5FB4` (보조·링크)
- `--brass #C9A24B` / `--brass-light #E2C277` (강조·CTA 골드)
- `--off #F4F6FA` `--paper #FBFCFE` `--slate #5E708A` `--line #E2E8F1`

타이포:
- 국문: Pretendard
- 영문 디스플레이/숫자: Big Shoulders Display

연출(프리미엄 스킨):
- 딥네이비 메시 글로우 배경, 글래스모피즘 헤더, 골드 그라데이션 버튼(샤인)
- 소프트 미니멀 카드(라운드 18·골드 링 호버), 스크롤 등장 애니메이션
- 골드 그라데이션 텍스트(히어로 강조·전화·별점·요금)

---

## 5. SEO / 색인
- 페이지별 고유 title(≤40~48자)·description(≤80자)·canonical, `lang=ko`
- Open Graph / Twitter 카드
- 구조화 데이터: Plumber(LocalBusiness)·FAQPage·BreadcrumbList
- sitemap.xml(3,082) · rss.xml(주요 31) · robots.txt
- 네이버 서치어드바이저 소유확인 메타 적용
- IndexNow(빙·네이버 즉시 통보): `tools/indexnow.py` + 키 파일
- 구글 Indexing API 스크립트: `tools/google_index.py`

---

## 6. 파일/폴더 구조
```
/index.html, /about.html, /contact.html, /cases.html, /price.html,
 /review.html, /faq.html, /privacy.html, /terms.html, /404.html
/service/*.html              서비스 상세
/area/**/index.html          지역(시도·시군구·행정동)
/assets/css/style.css        전체 스타일(프리미엄 스킨 포함)
/assets/js/main.js           메뉴·FAQ·팝업·스크롤 인터랙션
/assets/logo/*               로고(가로/세로/심볼, 라이트/다크)
/assets/img/*                히어로 배너(webp/jpg), 시공사례 SVG
/assets/data/*.json          행정구역·행정동 데이터(빌드용)
/build.py, /pages.py         사이트 생성기(소스)
/tools/*                     IndexNow·구글 색인·운영 가이드
/sitemap.xml /rss.xml /robots.txt
BRIEF.md                     원본 브리프
```

## 7. 빌드 방법
```bash
python3 pages.py      # 전체 HTML 재생성
```
교체용 자리표시값: 전화 `0000-0000`, 사업자번호 `000-00-00000`, 대표/주소(미정),
네이버/카카오 채널 URL — 확정 시 `build.py` 상단 상수/문자열만 바꾸면 일괄 반영.
