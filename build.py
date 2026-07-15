#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스피드 배관공사 정적 사이트 빌더.
공통 헤더/푸터/메타를 한 곳에서 관리하고 순수 HTML을 산출합니다.
빌드 도구 없이 결과물(HTML/CSS/소량 JS)만으로 동작합니다.
사용: python3 build.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://plumbing-repair.pages.dev"

# 대표 고객 검색 키워드 — 전 페이지 공통 meta keywords 및 본문 SEO 반영
KEYWORDS = ("누수탐지, 누수공사, 하수구막힘, 배관막힘, 배관설비, 수전교체, 싱크대수전교체, "
            "화장실수전교체, 변기막힘, 화장실변기교체, 변기부속품수리, 싱크대하수구막힘, "
            "세면대막힘, 세면대교체, 배수구막힘, 배수구뚫음, 욕실배관누수, 수도누수, 수도수리, "
            "주방배관누수, 주방배수구막힘, 이물질제거, 배관내시경, 역류, 물샘, 배관부품, "
            "배관업체, 배관공사, 배관수리비용, 배관수리가격, 고압세척, 24시 긴급출동")

# ---------------------------------------------------------------------------
# 시공 갤러리 이미지 (21장)
#   assets/img/gallery/01.jpg … 21.jpg (선택: 같은 이름 .webp) 를 넣은 뒤
#   아래 GALLERY_READY = True 로 바꾸고 `python3 pages.py` 재빌드하면
#   플레이스홀더 박스가 실제 이미지로 일괄 교체됩니다.
# ---------------------------------------------------------------------------
GALLERY_READY = True                # 실제 이미지 준비되면 True (assets/img/gallery/NN.webp)
GALLERY_DIR = "/assets/img/gallery"
GALLERY_COUNT = 21

def gallery_figure(n, alt, caption=""):
    """n번(1~21) 갤러리 슬롯. 이미지 준비 전에는 플레이스홀더 박스를 렌더."""
    nn = f"{int(n):02d}"
    cap = f'<figcaption class="gphoto-cap">{caption}</figcaption>' if caption else ""
    if GALLERY_READY:
        media = (f'<img class="gphoto-img" src="{GALLERY_DIR}/{nn}.webp" alt="{alt}" '
                 f'loading="lazy" decoding="async" width="1000" height="750">')
        return f'<figure class="gphoto"><a href="{GALLERY_DIR}/{nn}.webp" aria-label="{alt} 크게 보기">{media}</a>{cap}</figure>'
    return (f'<figure class="gphoto is-empty" role="img" aria-label="{alt}" data-slot="{nn}">'
            f'<span class="gphoto-ph"><span class="gphoto-no">{nn}</span>'
            f'<span class="gphoto-tx">시공사진 준비중</span></span>{cap}</figure>')

# 공식 채널 URL (확정 후 실제 주소로 교체) — 자리표시값
NAVER_PLACE = "https://map.naver.com/"      # TODO: 네이버 플레이스(스마트플레이스) 실제 URL
NAVER_BLOG  = "https://blog.naver.com/"      # TODO: 네이버 블로그 실제 URL
NAVER_TALK  = "https://talk.naver.com/"      # TODO: 네이버 톡톡 상담 실제 URL
KAKAO_CH    = "https://pf.kakao.com/"        # TODO: 카카오톡 채널 실제 URL

# ---------------------------------------------------------------------------
# 공통 조각
# ---------------------------------------------------------------------------
def head(title, desc, canonical, jsonld="", og_title=None, og_desc=None, robots="index, follow", keywords=KEYWORDS):
    og_title = og_title or title
    og_desc = og_desc or desc
    blocks = ""
    if jsonld:
        blocks = jsonld
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="{robots}">
<meta name="googlebot" content="{robots}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="스피드 배관공사">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:image" content="{SITE}/assets/logo/symbol.png">
<meta property="og:url" content="{canonical}">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{og_desc}">
<meta name="twitter:image" content="{SITE}/assets/logo/symbol.png">
<!-- 네이버 서치어드바이저 소유확인 -->
<meta name="naver-site-verification" content="bb1b124cbdf6cb7fe7b7cb1c9611aea5224f1da4">
<!-- 구글 서치콘솔 소유확인: 코드 확정 시 삽입 -->
<!-- <meta name="google-site-verification" content="여기에_인증코드"> -->
<link rel="icon" type="image/png" href="/assets/logo/symbol.png">
<link rel="apple-touch-icon" href="/assets/logo/symbol.png">
<link rel="alternate" type="application/rss+xml" title="스피드 배관공사 소식" href="/rss.xml">
<link rel="sitemap" type="application/xml" title="Sitemap" href="/sitemap.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css">
<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
{blocks}</head>
<body>
"""

HEADER = """<header class="site-header" id="top">
  <div class="container header-inner">
    <a class="brand" href="/" aria-label="스피드 배관공사 홈">
      <img class="logo-light" src="/assets/logo/logo-horizontal-white.png" alt="스피드 배관공사 SPEED PLUMBING">
      <img class="logo-dark" src="/assets/logo/logo-horizontal-dark.png" alt="스피드 배관공사 SPEED PLUMBING">
    </a>
    <nav class="gnb" aria-label="주 메뉴" id="gnb">
      <ul class="gnb-list">
        <li><a class="gnb-link" href="/">홈</a></li>
        <li class="has-sub">
          <a class="gnb-link" href="/service/" aria-haspopup="true">서비스안내
            <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg></a>
          <div class="submenu" role="menu">
            <a href="/service/sewer-clog.html">하수구막힘</a>
            <a href="/service/plumbing.html">배관공사</a>
            <a href="/service/leak-detection.html">누수탐지</a>
            <a href="/service/high-pressure.html">고압세척</a>
            <a href="/service/cctv.html">CCTV 관로검사</a>
            <a href="/service/">전체 서비스 보기</a>
          </div>
        </li>
        <li class="has-sub">
          <a class="gnb-link" href="/area/" aria-haspopup="true">지역별 서비스
            <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg></a>
          <div class="submenu" role="menu">
            <a href="/area/seoul/">서울특별시</a>
            <a href="/area/gyeonggi/">경기도</a>
            <a href="/area/busan/">부산광역시</a>
            <a href="/area/">전국 지역 보기</a>
          </div>
        </li>
        <li><a class="gnb-link" href="/cases.html">시공사례</a></li>
        <li><a class="gnb-link" href="/price.html">요금안내</a></li>
        <li><a class="gnb-link" href="/review.html">고객후기</a></li>
        <li><a class="gnb-link" href="/faq.html">자주묻는질문</a></li>
        <li class="has-sub">
          <a class="gnb-link" href="/about.html" aria-haspopup="true">회사소개
            <svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg></a>
          <div class="submenu" role="menu">
            <a href="/about.html">회사소개</a>
            <a href="/contact.html">상담문의</a>
          </div>
        </li>
      </ul>
      <div class="mobile-only-cta">
        <a class="btn btn--primary btn--block" href="tel:010-5183-4300">☎ 010-5183-4300 전화상담</a>
        <!-- 광고문의 상담(모바일 메뉴) 주석처리 — 요청에 따라 미노출
        <a class="btn btn--ghost-light btn--block" href="https://t.me/googleseolab" target="_blank" rel="noopener">광고문의 상담</a>
        -->
      </div>
    </nav>
    <div class="header-actions">
      <a class="header-phone" href="tel:010-5183-4300">
        <small>24시 긴급출동 · 연중무휴</small>
        <strong>010-5183-4300</strong>
      </a>
      <!-- 광고문의(헤더 버튼) 주석처리 — 요청에 따라 미노출:
      <a class="btn btn--primary header-cta" href="https://t.me/googleseolab" target="_blank" rel="noopener">광고문의</a>
      -->
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false" aria-controls="gnb"><span></span></button>
    </div>
  </div>
</header>
"""

FOOTER = """<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <img src="/assets/logo/logo-horizontal-white.png" alt="스피드 배관공사 SPEED PLUMBING">
        <p>호텔·상가·오피스빌딩 등 상업시설 전문 B2B 배관 파트너.<br>하수구막힘·배관공사·누수탐지·고압세척을 24시간 신속하게 해결합니다.</p>
      </div>
      <nav class="footer-col" aria-label="전체 메뉴">
        <h4>전체 메뉴</h4>
        <ul>
          <li><a href="/service/">서비스안내</a></li>
          <li><a href="/area/">지역별 서비스</a></li>
          <li><a href="/cases.html">시공사례</a></li>
          <li><a href="/price.html">요금안내</a></li>
          <li><a href="/review.html">고객후기</a></li>
          <li><a href="/faq.html">자주묻는질문</a></li>
          <li><a href="/about.html">회사소개</a></li>
          <li><a href="/contact.html">상담문의</a></li>
        </ul>
      </nav>
      <nav class="footer-col" aria-label="주요 서비스">
        <h4>주요 서비스</h4>
        <ul>
          <li><a href="/service/sewer-clog.html">하수구막힘</a></li>
          <li><a href="/service/plumbing.html">배관공사</a></li>
          <li><a href="/service/leak-detection.html">누수탐지</a></li>
          <li><a href="/service/high-pressure.html">고압세척</a></li>
          <li><a href="/service/cctv.html">CCTV 관로검사</a></li>
        </ul>
      </nav>
    </div>
    <div class="footer-regions">
      <h4>서비스 지역 (전국)</h4>
      <nav class="reglinks" aria-label="시도별 서비스 지역">
        <a href="/area/seoul/">서울특별시</a>
        <a href="/area/busan/">부산광역시</a>
        <a href="/area/daegu/">대구광역시</a>
        <a href="/area/incheon/">인천광역시</a>
        <a href="/area/gwangju/">광주광역시</a>
        <a href="/area/daejeon/">대전광역시</a>
        <a href="/area/ulsan/">울산광역시</a>
        <a href="/area/sejong/">세종특별자치시</a>
        <a href="/area/gyeonggi/">경기도</a>
        <a href="/area/gangwon/">강원특별자치도</a>
        <a href="/area/chungbuk/">충청북도</a>
        <a href="/area/chungnam/">충청남도</a>
        <a href="/area/jeonbuk/">전북특별자치도</a>
        <a href="/area/jeonnam/">전라남도</a>
        <a href="/area/gyeongbuk/">경상북도</a>
        <a href="/area/gyeongnam/">경상남도</a>
        <a href="/area/jeju/">제주특별자치도</a>
      </nav>
    </div>
    <nav class="footer-channels" aria-label="공식 채널">
      <h4>공식 채널</h4>
      <a href="%(place)s" target="_blank" rel="noopener"><span class="nv">N</span>네이버 플레이스</a>
      <a href="%(blog)s" target="_blank" rel="noopener"><span class="nv">N</span>네이버 블로그</a>
      <a href="%(talk)s" target="_blank" rel="noopener"><span class="nv">N</span>네이버 톡톡</a>
      <a class="kakao" href="%(kakao)s" target="_blank" rel="noopener"><span class="nv">K</span>카카오톡 채널</a>
    </nav>

    <!-- 광고주 모집 배너(footer-adbar) 주석처리 — 요청에 따라 미노출:
    <div class="footer-adbar">
      <span class="footer-adbar-txt">📣 이 자리에 귀사 광고를 노출하세요 — 지역별 상위 노출 <strong>광고주 모집 중</strong></span>
      <a class="footer-ad-btn" href="https://t.me/googleseolab" target="_blank" rel="noopener">광고문의 (텔레그램)</a>
    </div>
    -->

    <section class="footer-keywords" aria-label="취급 서비스 키워드">
      <h4>취급 서비스</h4>
      <p class="fk-tags">누수탐지 · 누수공사 · 하수구막힘 · 배관막힘 · 배관설비 · 수전교체 · 싱크대수전교체 · 화장실수전교체 · 변기막힘 · 화장실변기교체 · 변기부속품수리 · 싱크대하수구막힘 · 세면대막힘 · 세면대교체 · 배수구막힘 · 배수구뚫음 · 욕실배관누수 · 수도누수 · 수도수리 · 주방배관누수 · 주방배수구막힘 · 고압세척</p>
      <p class="fk-desc">이물질 제거·배관내시경 검사부터 역류·물샘·누수까지, 부품 교체와 배관 수리 공사 비용·가격을 전화로 먼저 안내하는 24시 긴급출동 배관 업체입니다.</p>
    </section>

    <address class="footer-biz">
      <div class="biz-name"><strong>스피드 배관공사</strong> (SPEED PLUMBING)</div>
      <div>대표자: (미정) · 사업자등록번호: 000-00-00000</div>
      <div>주소: (미정)</div>
      <div>대표전화: <a href="tel:010-5183-4300">010-5183-4300</a> · 카카오톡 상담: @스피드배관</div>
      <div>영업시간: 연중무휴 24시간 긴급출동</div>
    </address>
    <div class="footer-bottom">
      <div>© 2026 스피드 배관공사 (SPEED PLUMBING). All rights reserved.</div>
      <nav class="footer-legal" aria-label="약관 및 정책">
        <a href="/privacy.html">개인정보처리방침</a>
        <a href="/terms.html">이용약관</a>
        <a href="/sitemap.xml">사이트맵</a>
      </nav>
    </div>
  </div>
</footer>
"""
FOOTER = FOOTER % {"place": NAVER_PLACE, "blog": NAVER_BLOG, "talk": NAVER_TALK, "kakao": KAKAO_CH}

MOBILE_BAR = """<nav class="mobile-bar" aria-label="빠른 연락">
  <a href="tel:010-5183-4300"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.68 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.32 1.85.55 2.81.68A2 2 0 0 1 22 16.92z"/></svg>전화</a>
  <a href="https://pf.kakao.com/" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>카톡</a>
  <!-- 광고문의(모바일 하단바) 주석처리 — 요청에 따라 미노출
  <a class="is-primary" href="https://t.me/googleseolab" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="15" x2="15" y2="15"/></svg>광고문의</a>
  -->
</nav>
"""

SCRIPTS = '<script src="/assets/js/main.js" defer></script>\n</body>\n</html>\n'

# 광고주 모집 팝업 (SEO 안전: 기본 hidden, JS가 지연 노출·빈도제한·쉬운 닫기)
AD_POPUP = """<div class="ad-popup" id="adPopup" role="dialog" aria-modal="true" aria-labelledby="adPopTitle" hidden>
  <div class="ad-popup-card">
    <button class="ad-popup-close" type="button" aria-label="팝업 닫기">&times;</button>
    <span class="ad-popup-badge">📣 광고주 모집</span>
    <h3 id="adPopTitle">지역별 상위 노출,<br>이 자리에 귀사 광고를</h3>
    <p>전국 시·군·구·동 단위로 노출되는 배관 전문 플랫폼입니다. 텔레그램으로 문의하시면 광고 단가와 노출 위치를 바로 안내해 드립니다.</p>
    <a class="ad-popup-btn" href="https://t.me/googleseolab" target="_blank" rel="noopener">✈ 광고문의 (텔레그램)</a>
    <button class="ad-popup-dismiss" type="button" data-dismiss-day>오늘 하루 보지 않기</button>
  </div>
</div>
"""


def clip_desc(s, n=80):
    """메타 설명을 n자 이내로 — 단어/구분자 경계에서 깔끔하게 컷."""
    s = " ".join(s.split())
    if len(s) <= n:
        return s
    cut = s[:n]
    for i in range(len(cut) - 1, n - 22, -1):
        if cut[i] in " .,·":
            return cut[:i].rstrip(" .,·")
    return cut.rstrip(" .,·")


def page(path, title, desc, canonical, body, jsonld="", og_title=None, og_desc=None, noindex=False):
    robots = "noindex, follow" if noindex else "index, follow"
    desc = clip_desc(desc)          # 네이버 권장: 설명 80자 이내 보장
    # 광고주 모집 팝업(AD_POPUP) 비활성화 — 요청에 따라 주석처리(미노출).
    html = head(title, desc, canonical, jsonld, og_title, og_desc, robots) + HEADER + body + FOOTER + MOBILE_BAR + SCRIPTS  # + AD_POPUP
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)


def page_hero(eyebrow, h1, sub, crumbs):
    """공통 페이지 상단 + breadcrumb. crumbs = [(label,url|None), ...]"""
    items = ""
    bl = []
    for i, (label, url) in enumerate(crumbs):
        if url and i < len(crumbs) - 1:
            items += f'<li><a href="{url}">{label}</a></li>'
        else:
            items += f'<li><span aria-current="page">{label}</span></li>'
    # JSON-LD breadcrumb
    el = []
    for i, (label, url) in enumerate(crumbs):
        item = {"pos": i + 1, "name": label}
        item["url"] = (SITE + url) if url else canonical_placeholder
        el.append(item)
    return f"""<section class="page-hero">
  <div class="container">
    <nav class="breadcrumb" aria-label="현재 위치"><ol>{items}</ol></nav>
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p>{sub}</p>
  </div>
</section>
"""

canonical_placeholder = SITE + "/"


def breadcrumb_jsonld(crumbs):
    items = []
    for i, (label, url) in enumerate(crumbs):
        items.append(
            '{"@type":"ListItem","position":%d,"name":"%s"%s}'
            % (i + 1, label, (',"item":"%s%s"' % (SITE, url)) if url else "")
        )
    return (
        '<script type="application/ld+json">\n'
        '{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":['
        + ",".join(items)
        + "]}\n</script>\n"
    )


# 공통 사이드바 CTA 카드
SIDEBAR = """<aside class="sidebar-card">
  <h3>지금 바로 상담하세요</h3>
  <p>현장 진단 후 선견적을 드립니다. 야간·새벽·공휴일도 쉬지 않는 <strong>연중무휴 24시 긴급출동</strong> 업체입니다.</p>
  <a class="phone-big" href="tel:010-5183-4300">010-5183-4300</a>
  <p style="margin-bottom:18px;">카카오톡 상담 @스피드배관</p>
  <a class="btn btn--primary btn--block" href="tel:010-5183-4300">☎ 전화 상담</a>
  <!-- 광고문의 상담(사이드바) 주석처리 — 요청에 따라 미노출:
  <a class="btn btn--ghost-light btn--block" href="https://t.me/googleseolab" target="_blank" rel="noopener" style="margin-top:10px;">광고문의 상담</a>
  -->
</aside>
"""

# 서비스 상세 하단 공통 CTA
def bottom_cta(h2="배관 문제, 24시 긴급출동으로 바로 해결합니다",
               p="전화 한 통이면 가장 가까운 전문 작업팀이 즉시 움직입니다. 야간·새벽·공휴일도 쉬지 않는 연중무휴 24시간, 언제든 연락 주세요."):
    return f"""<section class="section">
  <div class="container">
    <div class="cta-banner"><div class="cta-banner-inner">
      <div><h2>{h2}</h2><p>{p}</p></div>
      <div class="hero-cta">
        <a class="btn btn--primary btn--lg" href="tel:010-5183-4300">☎ 010-5183-4300</a>
        <!-- 광고문의 상담(하단 CTA) 주석처리 — 요청에 따라 미노출:
        <a class="btn btn--ghost-light btn--lg" href="https://t.me/googleseolab" target="_blank" rel="noopener">광고문의 상담</a>
        -->
      </div>
    </div></div>
  </div>
</section>
"""
