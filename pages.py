#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""모든 페이지 콘텐츠 정의 후 빌드. 사용: python3 pages.py"""
from build import (page, SITE, breadcrumb_jsonld, SIDEBAR, bottom_cta,
                   NAVER_PLACE, NAVER_BLOG, NAVER_TALK, KAKAO_CH)
import json as _json, os as _os

S = SITE

# ===========================================================================
# 전국 행정구역(시도 > 시군구) 공식 데이터 + 로마자 슬러그
# 출처: cosmosfarm/korea-administrative-district (행정안전부 기준)
# ===========================================================================
_KAD = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                  "assets/data/korea-administrative-district.json"), encoding="utf-8"))
OFFICIAL = {}          # {시도ko: [시군구ko ...]}
for _it in _KAD["data"]:
    for _sd, _gus in _it.items():
        OFFICIAL[_sd] = _gus

def sido_slug_of(ko):
    m = {"서울":"seoul","부산":"busan","대구":"daegu","인천":"incheon","광주":"gwangju",
         "대전":"daejeon","울산":"ulsan","세종":"sejong","경기":"gyeonggi","강원":"gangwon",
         "충청북도":"chungbuk","충청남도":"chungnam","전북":"jeonbuk","전라북도":"jeonbuk",
         "전라남도":"jeonnam","경상북도":"gyeongbuk","경상남도":"gyeongnam","제주":"jeju"}
    for k, v in m.items():
        if ko.startswith(k):
            return v
    return "etc"

# 한글 → 로마자(국어의 로마자 표기, 슬러그용 간이 변환)
_CHO=["g","kk","n","d","tt","r","m","b","pp","s","ss","","j","jj","ch","k","t","p","h"]
_JUNG=["a","ae","ya","yae","eo","e","yeo","ye","o","wa","wae","oe","yo","u","wo","we","wi","yu","eu","ui","i"]
_JONG=["","k","k","k","n","n","n","t","l","k","m","l","l","l","p","l","m","p","p","t","t","ng","t","t","k","t","p","t"]
def _rr(s):
    out=[]
    for ch in s:
        o=ord(ch)
        if 0xAC00<=o<=0xD7A3:
            i=o-0xAC00; out.append(_CHO[i//588]+_JUNG[(i%588)//28]+_JONG[i%28])
        else:
            out.append(ch)
    return "".join(out)
def gungu_slug(name):
    if name.endswith("구"):   return _rr(name[:-1])+"-gu"
    if name.endswith("군"):   return _rr(name[:-1])+"-gun"
    if name.endswith("시"):   return _rr(name[:-1])+"-si"
    return _rr(name)

# 이미 고유 콘텐츠로 제작된 시군구는 해당 URL을 그대로 사용(자동 생성에서 제외)
CUSTOM_GUNGU_URL = {
    ("seoul","강남구"):"/area/seoul/gangnam-gu/",
    ("seoul","서초구"):"/area/seoul/seocho-gu/",
    ("seoul","송파구"):"/area/seoul/songpa-gu/",
    ("seoul","강동구"):"/area/seoul/gangdong-gu/",
    ("seoul","마포구"):"/area/seoul/mapo-gu/",
    ("seoul","영등포구"):"/area/seoul/yeongdeungpo-gu/",
}
def gungu_url(sido_slug, gu_ko):
    c = CUSTOM_GUNGU_URL.get((sido_slug, gu_ko))
    return c if c else f"/area/{sido_slug}/{gungu_slug(gu_ko)}/"

# ---------------------------------------------------------------------------
# 전국 행정동(대표 동명 통합) 데이터 + 동 슬러그
# ---------------------------------------------------------------------------
DONG_DATA = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                  "assets/data/hjd_consolidated.json"), encoding="utf-8"))
# 2023년 행정구역 개편: 군위군은 경북 → 대구로 이관
if "군위군" in DONG_DATA.get("gyeongbuk", {}):
    DONG_DATA.setdefault("daegu", {})["군위군"] = DONG_DATA["gyeongbuk"].pop("군위군")

def dong_slug(name):
    if name.endswith("동"):  return _rr(name[:-1])+"-dong"
    if name.endswith("읍"):  return _rr(name[:-1])+"-eup"
    if name.endswith("면"):  return _rr(name[:-1])+"-myeon"
    return _rr(name)

# 이미 행정동 상세가 있는 시군구(자동 동 생성에서 제외)
SKIP_DONG = {("seoul","강남구"),("seoul","서초구"),("seoul","송파구"),
             ("seoul","강동구"),("seoul","마포구"),("seoul","영등포구")}

def dongs_of(sido_slug, gu_ko):
    return DONG_DATA.get(sido_slug, {}).get(gu_ko, [])


# ===========================================================================
# 홈 (index.html)
# ===========================================================================
HOME_JSONLD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Plumber",
  "name": "스피드 배관공사",
  "alternateName": "SPEED PLUMBING",
  "description": "가정집·음식점·빌딩 배관 전문. 하수구막힘·배관공사·누수탐지·고압세척 — 원인 진단 후 근본 처리, 24시간 출동.",
  "image": "%(s)s/assets/logo/symbol.png",
  "logo": "%(s)s/assets/logo/logo-horizontal-dark.png",
  "url": "%(s)s/",
  "telephone": "+82-0000-0000",
  "priceRange": "\\u20a9\\u20a9",
  "openingHoursSpecification": {"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],"opens":"00:00","closes":"23:59"},
  "areaServed": {"@type":"Country","name":"대한민국"},
  "address": {"@type":"PostalAddress","addressCountry":"KR","addressRegion":"서울특별시"},
  "aggregateRating": {"@type":"AggregateRating","ratingValue":"4.9","reviewCount":"327"},
  "sameAs": ["%(place)s","%(blog)s","%(talk)s","%(kakao)s"]
}
</script>
""" % {"s": S, "place": NAVER_PLACE, "blog": NAVER_BLOG, "talk": NAVER_TALK, "kakao": KAKAO_CH}

FAQ_ITEMS = [
    ("배관 문제가 발생하면 얼마나 빨리 출동하나요?",
     "접수 후 가까운 작업팀이 즉시 배정됩니다. 도심 주요 지역은 평균 30~40분, 외곽 지역도 당일 출동을 원칙으로 합니다. 야간·새벽·공휴일도 동일하게 운영됩니다."),
    ("현장 방문 전에 대략적인 비용을 알 수 있나요?",
     "증상과 위치, 건물 형태를 알려주시면 전화 상담으로 예상 범위를 안내드립니다. 정확한 금액은 현장 진단 후 선견적으로 확정하며, 동의하신 범위 외 추가 청구는 없습니다."),
    ("하수구가 자꾸 막히는데 왜 그런건가요?",
     "일시적으로 뚫은 뒤 배관 내벽에 기름때·스케일이 남아 있으면 단기간 내 다시 막힙니다. CCTV로 내부를 확인하고 고압세척으로 관 벽까지 세척해야 재발 주기를 크게 늘릴 수 있습니다."),
    ("수도요금이 갑자기 올랐는데 누수 때문일 수 있나요?",
     "계량기 근처의 밸브를 잠그고 계량기 숫자가 오르면 내부 누수일 가능성이 높습니다. 청음·열화상·가스 탐지 등 비파괴 방식으로 벽이나 바닥을 뜯지 않고 위치를 특정할 수 있습니다."),
    ("가정집도 작업이 가능한가요, 상업시설 전문인가요?",
     "가정집(아파트·빌라·단독주택)과 상업시설(식당·상가·호텔·빌딩) 모두 작업합니다. 현장 유형에 맞는 장비와 작업 방식을 달리 적용하므로 어느 쪽이든 먼저 증상을 말씀해 주세요."),
    ("작업 후 다시 문제가 생기면 어떻게 되나요?",
     "작업 항목별로 사후 보증을 적용합니다. 동일 원인으로 재발한 경우 보증 기간 내에는 재작업을 진행하며, 보증 범위는 작업 전 안내드립니다."),
]

def faq_jsonld(items):
    q = []
    for name, ans in items:
        q.append('{"@type":"Question","name":"%s","acceptedAnswer":{"@type":"Answer","text":"%s"}}'
                  % (name.replace('"', '\\"'), ans.replace('"', '\\"')))
    return ('<script type="application/ld+json">\n{"@context":"https://schema.org","@type":"FAQPage","mainEntity":['
            + ",".join(q) + "]}\n</script>\n")

def faq_html(items, intro=True):
    rows = ""
    for name, ans in items:
        rows += f"""      <div class="faq-item">
        <button class="faq-q" aria-expanded="false"><span>{name}</span><span class="plus" aria-hidden="true"></span></button>
        <div class="faq-a"><div class="faq-a-inner">{ans}</div></div>
      </div>
"""
    return rows

HERO = """<section class="hero hero--media">
  <div class="container hero-inner">
    <div class="hero-text">
    <span class="badge badge--light"><span class="dot"></span>가정집 · 음식점 · 빌딩 배관 전문</span>
    <h1>막힘부터 누수까지 <span class="accent">배관 문제</span>,<br>정확하게 뿌리뽑습니다.</h1>
    <p class="hero-sub">하수구막힘·배관공사·누수탐지·고압세척 — 가정집과 상업시설 모두, 증상을 확인하고 원인부터 해결하는 스피드 배관공사. 현장 방문 전 전화 상담으로 예상 비용을 먼저 안내드립니다.</p>
    <div class="hero-cta">
      <a class="btn btn--primary btn--lg" href="tel:0000-0000">
        <svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.68 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.32 1.85.55 2.81.68A2 2 0 0 1 22 16.92z"/></svg>
        지금 전화 0000-0000</a>
      <a class="btn btn--ghost-light btn--lg" href="https://t.me/googleseolab" target="_blank" rel="noopener">광고문의 상담</a>
    </div>
    <div class="hero-trust">
      <span class="badge badge--light">⏱ 당일·야간 출동 가능</span>
      <span class="badge badge--light">✓ 전화 상담 후 예상 비용 안내</span>
      <span class="badge badge--light">★ 작업 후 보증 제공</span>
    </div>
    <div class="hero-keywords" aria-hidden="true">
      <span>#하수구막힘</span><span>#배관공사</span><span>#누수탐지</span><span>#고압세척</span><span>#싱크대막힘</span><span>#CCTV관로검사</span>
    </div>
    </div>
    <div class="hero-media">
      <figure class="hero-photo-frame">
        <picture>
          <source srcset="/assets/img/hero.webp" type="image/webp">
          <img class="hero-photo" src="/assets/img/hero.jpg" alt="배관 전문가가 하수구막힘을 진단하고 고압세척으로 처리하는 현장 — 스피드 배관공사"
               width="1672" height="941" loading="eager" fetchpriority="high">
        </picture>
      </figure>
    </div>
  </div>
</section>
"""

TRUST = """<section class="section section--off" aria-labelledby="trust-h">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">Why Speed Plumbing</span>
      <h2 id="trust-h">배관 문제, 왜 스피드에 맡기나요</h2>
      <p class="lead">막힘 하나가 영업을 멈추고, 누수 하나가 아랫집 분쟁으로 번집니다. 원인을 정확히 찾고, 재발까지 관리합니다.</p>
    </div>
    <div class="trust-grid">
      <div class="trust-card"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/></svg></div><h3>당일·야간 출동</h3><p>낮이든 새벽이든 접수 즉시 현장과 가장 가까운 작업팀을 연결합니다.</p></div>
      <div class="trust-card"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg></div><h3>전화 상담 후 비용 안내</h3><p>증상을 먼저 들은 뒤 예상 범위를 안내합니다. 현장에서 확정된 견적 외 추가 청구는 없습니다.</p></div>
      <div class="trust-card"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-6h6v6"/></svg></div><h3>근본 원인 처리</h3><p>일시 뚫음에 그치지 않고 반복 원인을 파악해 재발을 최소화합니다.</p></div>
      <div class="trust-card"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15 15 0 0 1 0 20 15 15 0 0 1 0-20z"/></svg></div><h3>전국 출동 가능</h3><p>전국 시·도 작업 네트워크로 주요 도심은 물론 인근 시·군·구까지 연결됩니다.</p></div>
    </div>
  </div>
</section>
"""

SERVICE_GRID = """<section class="section" aria-labelledby="svc-h">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">Services</span>
      <h2 id="svc-h">어떤 배관 문제든 해결합니다</h2>
      <p class="lead">가정집부터 식당·빌딩까지, 현장 조건에 맞는 장비와 방법으로 접근합니다.</p>
    </div>
    <div class="service-grid">
      <a class="service-card" href="/service/sewer-clog.html"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7h18"/><path d="M6 7v9a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3V7"/><path d="M9 11v3M15 11v3"/></svg></div><h3>하수구막힘</h3><p>역류·악취·배수 지연 — 막힘 위치와 원인을 먼저 파악합니다.</p><span class="more">자세히 →</span></a>
      <a class="service-card" href="/service/plumbing.html"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h7v4H4z"/><path d="M11 9h5a3 3 0 0 1 3 3v8"/><path d="M16 20h6"/></svg></div><h3>배관공사</h3><p>노후관 교체·신설·증설 — 영업 중단 최소화 시공.</p><span class="more">자세히 →</span></a>
      <a class="service-card" href="/service/leak-detection.html"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/></svg></div><h3>누수탐지</h3><p>벽·바닥 철거 없이 청음·열화상으로 위치 특정.</p><span class="more">자세히 →</span></a>
      <a class="service-card" href="/service/high-pressure.html"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h6"/><path d="M9 9l4 3-4 3z"/><path d="M14 7v10M18 5v14"/></svg></div><h3>고압세척</h3><p>기름때·스케일을 고압수로 제거해 배수 흐름 회복.</p><span class="more">자세히 →</span></a>
      <a class="service-card" href="/service/cctv.html"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/></svg></div><h3>CCTV 관로검사</h3><p>카메라로 배관 내부를 직접 확인해 원인 특정.</p><span class="more">자세히 →</span></a>
      <a class="service-card" href="/service/sewer-clog.html"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="2" width="12" height="9" rx="2"/><path d="M9 11v9a3 3 0 0 0 6 0v-9"/></svg></div><h3>변기·싱크대막힘</h3><p>이물질 제거·압력 관통으로 즉시 배수 복구.</p><span class="more">자세히 →</span></a>
      <a class="service-card" href="/service/plumbing.html"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v6"/><path d="M5 8h14l-1 12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z"/></svg></div><h3>정화조·동파</h3><p>정화조 준설·청소 및 동파된 배관 복구.</p><span class="more">자세히 →</span></a>
      <a class="service-card" href="/service/plumbing.html"><div class="ico-wrap"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 7l3 3"/><path d="M3 21l3-1 11-11-2-2L4 18z"/><path d="M17 4l3 3"/></svg></div><h3>배관 리모델링</h3><p>상가·사무실 인테리어 배관 재배치·경로 변경.</p><span class="more">자세히 →</span></a>
    </div>
  </div>
</section>
"""

AREA_BLOCK = """<section class="section section--off" aria-labelledby="area-h">
  <div class="container area-block">
    <div>
      <span class="eyebrow">Nationwide</span>
      <h2 id="area-h">내 지역 배관 서비스 확인하기</h2>
      <p class="lead">전국 17개 시·도에 작업 네트워크를 운영합니다. 지역을 선택하면 해당 지역 출동 가능 여부와 서비스 안내를 확인할 수 있습니다.</p>
      <p><a class="btn btn--secondary" href="/area/">전국 지역 전체 보기</a></p>
    </div>
    <nav class="region-grid" aria-label="시도 바로가기">
      <a href="/area/seoul/">서울</a><a href="/area/busan/">부산</a><a href="/area/daegu/">대구</a><a href="/area/incheon/">인천</a>
      <a href="/area/gwangju/">광주</a><a href="/area/daejeon/">대전</a><a href="/area/ulsan/">울산</a><a href="/area/sejong/">세종</a>
      <a href="/area/gyeonggi/">경기</a><a href="/area/gangwon/">강원</a><a href="/area/chungbuk/">충북</a><a href="/area/chungnam/">충남</a>
      <a href="/area/jeonbuk/">전북</a><a href="/area/jeonnam/">전남</a><a href="/area/gyeongbuk/">경북</a><a href="/area/gyeongnam/">경남</a><a href="/area/jeju/">제주</a>
    </nav>
  </div>
</section>
"""

STEPS = """<section class="section" aria-labelledby="step-h">
  <div class="container">
    <div class="section-head center"><span class="eyebrow">Process</span><h2 id="step-h">문의부터 사후 보증까지, 5단계 진행 방식</h2><p class="lead">비용과 작업 범위를 단계마다 공유하고, 동의 없이는 진행하지 않습니다.</p></div>
    <ol class="steps">
      <li class="step"><div class="num">01</div><h3>증상 상담</h3><p>전화로 증상·위치·건물 형태를 먼저 파악하고 예상 비용을 안내합니다.</p></li>
      <li class="step"><div class="num">02</div><h3>현장 출동</h3><p>증상에 맞는 장비를 갖춘 작업팀이 빠르게 현장으로 이동합니다.</p></li>
      <li class="step"><div class="num">03</div><h3>원인 진단 · 확정 견적</h3><p>배관 상태를 확인하고 정확한 비용을 안내한 뒤 동의가 확인되면 작업을 시작합니다.</p></li>
      <li class="step"><div class="num">04</div><h3>작업 · 현장 정리</h3><p>장비로 막힘·누수를 처리하고 작업 후 현장을 깔끔하게 정리합니다.</p></li>
      <li class="step"><div class="num">05</div><h3>재발 방지 안내 · 보증</h3><p>반복을 줄이는 관리 방법을 안내하고 작업 범위에 맞는 보증을 적용합니다.</p></li>
    </ol>
  </div>
</section>
"""

PRICE_PREVIEW = """<section class="section section--off" aria-labelledby="price-h">
  <div class="container">
    <div class="section-head"><span class="eyebrow">Pricing</span><h2 id="price-h">서비스별 예상 요금 안내</h2><p class="lead">아래 금액은 일반적인 참고 범위입니다. 현장 상황(막힘 위치·관 길이·접근성)에 따라 달라지며, 정확한 견적은 상담 후 안내드립니다.</p></div>
    <div class="price-table-wrap"><table class="price-table">
      <caption>※ 부가세 별도 · 현장 진단 후 선견적 제공 · 추가금 없음</caption>
      <thead><tr><th scope="col">서비스 항목</th><th scope="col">작업 범위</th><th scope="col">참고 요금</th></tr></thead>
      <tbody>
        <tr><td>하수구막힘</td><td>스프링·관통기 1개소</td><td class="unit">5만원~</td></tr>
        <tr><td>변기·싱크대막힘</td><td>이물질 제거·압력 관통</td><td class="unit">4만원~</td></tr>
        <tr><td>고압세척</td><td>기름때·스케일 관로 세척</td><td class="unit">별도 산정</td></tr>
        <tr><td>누수탐지</td><td>비파괴 정밀 탐지</td><td class="unit">10만원~</td></tr>
        <tr><td>CCTV 관로검사</td><td>배관 내부 영상 진단</td><td class="unit">8만원~</td></tr>
        <tr><td>배관공사</td><td>교체·신설·증설</td><td class="unit">현장 견적</td></tr>
      </tbody>
    </table></div>
    <p class="price-note">식당·빌딩 등 정기 관리 계약 시 우선 출동 및 요금 할인이 적용됩니다. · <a href="/price.html">전체 요금표 보기</a></p>
  </div>
</section>
"""

def case_grid(more=True):
    btn = '<p style="text-align:center;margin-top:32px;"><a class="btn btn--secondary" href="/cases.html">시공사례 전체보기</a></p>' if more else ""
    return f"""<section class="section" aria-labelledby="case-h">
  <div class="container">
    <div class="section-head center"><span class="eyebrow">Before / After</span><h2 id="case-h">실제 시공 사례</h2><p class="lead">직접 찍은 현장 사진으로 작업 전후를 확인하세요.</p></div>
    <div class="case-grid">
      <article class="case-card"><div class="ba"><figure class="before"><img src="/assets/img/case1.svg" alt="서울 강남 호텔 주방 하수구 기름때 막힘 작업 전 상태" loading="lazy" width="400" height="300"><figcaption>BEFORE</figcaption></figure><figure class="after"><img src="/assets/img/case1-after.svg" alt="서울 강남 호텔 주방 고압세척으로 배관 내부 기름때 완전 제거 후" loading="lazy" width="400" height="300"><figcaption>AFTER</figcaption></figure></div><div class="case-body"><span class="case-tag">호텔 · 고압세척</span><h3>서울 강남 호텔 주방 배관 고압세척</h3><p>6개월 주기로 반복되던 역류를 고압세척과 CCTV 진단으로 근본 해결. 이후 정기 관리 계약 전환.</p></div></article>
      <article class="case-card"><div class="ba"><figure class="before"><img src="/assets/img/case2.svg" alt="경기 성남 상가 천장에 물 얼룩이 생긴 누수 탐지 전 상태" loading="lazy" width="400" height="300"><figcaption>BEFORE</figcaption></figure><figure class="after"><img src="/assets/img/case2-after.svg" alt="경기 성남 상가 누수 지점 비파괴 탐지 및 최소 보수 후 복구된 천장" loading="lazy" width="400" height="300"><figcaption>AFTER</figcaption></figure></div><div class="case-body"><span class="case-tag">상가 · 누수탐지</span><h3>경기 성남 상가 천장 누수 비파괴 탐지</h3><p>벽 전체 철거 대신 청음·열화상으로 지점을 특정, 최소 범위만 보수해 공사비 60% 절감.</p></div></article>
      <article class="case-card"><div class="ba"><figure class="before"><img src="/assets/img/case3.svg" alt="부산 해운대 오피스빌딩 지하 30년 노후 주철관 부식 상태" loading="lazy" width="400" height="300"><figcaption>BEFORE</figcaption></figure><figure class="after"><img src="/assets/img/case3-after.svg" alt="부산 해운대 오피스빌딩 지하 노후 배관 스테인리스 교체 완료 후" loading="lazy" width="400" height="300"><figcaption>AFTER</figcaption></figure></div><div class="case-body"><span class="case-tag">빌딩 · 배관공사</span><h3>부산 해운대 오피스빌딩 지하 노후관 교체</h3><p>30년 된 주철관을 야간 무중단으로 스테인리스 교체 완료. 입주사 민원 없이 3일 공정 마무리.</p></div></article>
    </div>
    {btn}
  </div>
</section>
"""

REVIEWS = """<section class="section section--off" aria-labelledby="review-h">
  <div class="container">
    <div class="section-head center"><span class="eyebrow">Reviews</span><h2 id="review-h">고객 후기</h2><p class="lead">실제 작업을 경험한 분들이 남긴 이야기입니다.</p></div>
    <div class="review-grid">
      <article class="review-card"><div class="stars" aria-label="별점 5점">★★★★★</div><blockquote>"주방 하수구가 새벽에 막혀 급하게 연락했는데, 한 시간도 안 돼 오셔서 고압세척까지 다 마쳤어요. 요금도 전화에서 말씀하신 그대로라 신뢰가 갔습니다."</blockquote><div class="review-meta"><span class="review-avatar">조</span><div><div class="who">조OO 대표</div><div class="where">서울 마포 · 식당</div></div></div></article>
      <article class="review-card"><div class="stars" aria-label="별점 5점">★★★★★</div><blockquote>"아랫집에서 물이 샌다고 연락이 와서 당황했는데, 벽을 뜯지 않고 누수 위치를 잡아주셔서 공사 범위가 훨씬 작아졌어요. 세금계산서 처리도 깔끔했습니다."</blockquote><div class="review-meta"><span class="review-avatar">강</span><div><div class="who">강OO 점주</div><div class="where">경기 수원 · 상가</div></div></div></article>
      <article class="review-card"><div class="stars" aria-label="별점 5점">★★★★★</div><blockquote>"입주 전 배관 점검을 맡겼는데 CCTV로 구배 불량을 발견해주셨어요. 덕분에 입주 후 문제 없이 지내고 있습니다. 설명도 친절하고 보고서도 제공해주셔서 좋았어요."</blockquote><div class="review-meta"><span class="review-avatar">윤</span><div><div class="who">윤OO 원장</div><div class="where">인천 · 의원</div></div></div></article>
    </div>
    <p style="text-align:center;margin-top:32px;"><a class="btn btn--secondary" href="/review.html">고객후기 전체보기</a> &nbsp; <a class="btn btn--primary" href="https://map.naver.com/" rel="noopener" target="_blank">네이버 플레이스에서 보기</a></p>
  </div>
</section>
"""

HOME_FAQ = f"""<section class="section" aria-labelledby="faq-h">
  <div class="container">
    <div class="section-head center"><span class="eyebrow">FAQ</span><h2 id="faq-h">자주 묻는 질문</h2></div>
    <div class="faq-list">
{faq_html(FAQ_ITEMS)}    </div>
    <p style="text-align:center;margin-top:28px;"><a href="/faq.html">자주 묻는 질문 더 보기 →</a></p>
  </div>
</section>
"""

_CHK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
TRUST_RIBBON = f"""<section class="trust-ribbon" aria-label="신뢰 요소">
  <div class="container">
    <span class="item">{_CHK}24시간 연중무휴 출동</span>
    <span class="item">{_CHK}선견적 후작업 · 추가금 없음</span>
    <span class="item">{_CHK}세금계산서·현금영수증 발행</span>
    <span class="item">{_CHK}작업 후 A/S 보증</span>
    <span class="item">{_CHK}누적 4.9★ · 327건 후기</span>
  </div>
</section>
"""

NAVER_SECTION = f"""<section class="section" aria-labelledby="naver-h">
  <div class="container">
    <div class="section-head center">
      <span class="eyebrow">Naver Channel</span>
      <h2 id="naver-h">네이버에서 스피드 배관공사 만나기</h2>
      <p class="lead">실시간 방문자 후기와 시공 사례, 빠른 상담을 네이버에서 확인하세요. 검색으로도 '스피드 배관공사'를 찾을 수 있습니다.</p>
    </div>
    <div class="naver-grid">
      <a class="channel-card" href="{NAVER_PLACE}" target="_blank" rel="noopener">
        <div class="ch-ico naver">N</div><h3>네이버 플레이스</h3>
        <p>방문자 리뷰·별점과 찾아오는 길, 영업정보를 확인하세요.</p>
        <span class="more">플레이스 보기 →</span>
      </a>
      <a class="channel-card" href="{NAVER_BLOG}" target="_blank" rel="noopener">
        <div class="ch-ico blog">B</div><h3>네이버 블로그</h3>
        <p>실제 시공 과정과 Before/After 사진을 블로그에서 확인하세요.</p>
        <span class="more">블로그 보기 →</span>
      </a>
      <a class="channel-card" href="{NAVER_TALK}" target="_blank" rel="noopener">
        <div class="ch-ico talk">T</div><h3>네이버 톡톡</h3>
        <p>네이버에서 바로 사진 상담과 예약 문의를 남기세요.</p>
        <span class="more">톡톡 상담 →</span>
      </a>
    </div>
  </div>
</section>
"""

HOME_BODY = ("<main>\n" + HERO + TRUST_RIBBON + TRUST + SERVICE_GRID + AREA_BLOCK + STEPS +
             PRICE_PREVIEW + case_grid() + REVIEWS + NAVER_SECTION + HOME_FAQ + bottom_cta() + "</main>\n")

page("index.html",
     "스피드 배관공사 | 하수구막힘·누수탐지·배관공사 전문",
     "하수구막힘·배관공사·누수탐지·고압세척 전문. 원인 진단 후 근본 해결 — 가정집·식당·빌딩 모두 출동 가능, 전화 상담 후 비용 안내.",
     S + "/",
     HOME_BODY,
     jsonld=HOME_JSONLD + faq_jsonld(FAQ_ITEMS),
     og_title="스피드 배관공사 | 하수구막힘·누수탐지·배관공사 전문",
     og_desc="하수구막힘·누수탐지·배관공사·고압세척 — 가정집·식당·빌딩 모두 대응, 원인부터 찾는 스피드 배관공사.")


# ===========================================================================
# 공통: 페이지 히어로 + 빵부스러기
# ===========================================================================
def phero(eyebrow, h1, sub, crumbs):
    items = ""
    for i, (label, url) in enumerate(crumbs):
        if url and i < len(crumbs) - 1:
            items += f'<li><a href="{url}">{label}</a></li>'
        else:
            items += f'<li><span aria-current="page">{label}</span></li>'
    return f"""<section class="page-hero page-hero--media">
  <div class="container page-hero-inner">
    <div class="page-hero-text">
      <nav class="breadcrumb" aria-label="현재 위치"><ol>{items}</ol></nav>
      <span class="eyebrow">{eyebrow}</span>
      <h1>{h1}</h1>
      <p>{sub}</p>
    </div>
    <div class="page-hero-media">
      <figure class="hero-photo-frame">
        <picture>
          <source srcset="/assets/img/hero.webp" type="image/webp">
          <img class="hero-photo" src="/assets/img/hero.jpg" alt="스피드 배관공사 — 전국 누수탐지·배관·하수구막힘 24시간 긴급출동"
               width="1672" height="941" loading="lazy">
        </picture>
      </figure>
    </div>
  </div>
</section>
"""

# ===========================================================================
# 서비스 상세 (증상/원인 → 작업방법 → 사용장비 → 예상요금 → 시공사례 → CTA)
# ===========================================================================
def service_page(slug, name, eyebrow, h1, hero_sub, title, desc,
                 symptoms, causes, methods, equipment, price_rows,
                 service_faq, related):
    crumbs = [("홈", "/"), ("서비스안내", "/service/"), (name, None)]
    sym = "".join(f"<li>{x}</li>" for x in symptoms)
    cau = "".join(f"<li>{x}</li>" for x in causes)
    met = "".join(f"<li><strong>{t}.</strong> {d}</li>" for t, d in methods)
    eq = "".join(f"<span>{x}</span>" for x in equipment)
    pr = "".join(f"<tr><td>{a}</td><td>{b}</td><td class='unit'>{c}</td></tr>" for a, b, c in price_rows)
    rel = "".join(f'<a class="link-card" href="{u}"><h3>{n}</h3><p>{p}</p></a>' for n, p, u in related)
    faq_block = ""
    faq_ld = ""
    if service_faq:
        faq_block = f"""<section class="section section--off" aria-labelledby="sfaq-h">
  <div class="container">
    <div class="section-head center"><span class="eyebrow">FAQ</span><h2 id="sfaq-h">{name} 자주 묻는 질문</h2></div>
    <div class="faq-list">
{faq_html(service_faq)}    </div>
  </div>
</section>
"""
        faq_ld = faq_jsonld(service_faq)
    body = f"""{phero(eyebrow, h1, hero_sub, crumbs)}
<main>
<section class="section">
  <div class="container layout-sidebar">
    <div class="prose">
      <p class="lead">{hero_sub}</p>

      <div class="scope-note">
        <span class="scope-badge">🏠 가정집</span>
        <span class="scope-badge">🏢 상업시설</span>
        <p><strong>가정집부터 상업시설까지 모두 작업합니다.</strong> 아파트·빌라·주택 등 가정집 {name}은 물론, 호텔·상가·오피스빌딩·음식점 등 상업시설까지 현장 규모에 맞춰 신속하게 출동합니다.</p>
      </div>

      <h2>가정집·상업시설 {name} 모두 가능합니다</h2>
      <p>스피드 배관공사는 가정집(아파트·빌라·단독주택)의 생활 {name}과 상업시설(호텔·상가·빌딩·음식점)의 대형 배관 작업을 함께 진행합니다. 가정집은 머리카락·음식물·비누 찌꺼기가, 영업장은 기름때·퇴적물이 주요 원인이 되는 등 현장마다 원인과 장비가 다르므로, 증상과 건물 형태를 먼저 확인한 뒤 작업 방향을 안내드립니다.</p>

      <h2>이런 증상이라면 {name} 점검이 필요합니다</h2>
      <ul class="ticks">{sym}</ul>

      <h2>주요 원인</h2>
      <ul class="ticks">{cau}</ul>

      <h2>작업 방법</h2>
      <ol style="padding-left:20px;display:flex;flex-direction:column;gap:10px;">{met}</ol>

      <h2>사용 장비</h2>
      <div class="chips">{eq}</div>

      <h2>예상 요금</h2>
      <div class="price-table-wrap"><table class="price-table">
        <caption>※ 부가세 별도 · 현장 진단 후 선견적 제공</caption>
        <thead><tr><th scope="col">항목</th><th scope="col">작업 범위</th><th scope="col">예상 요금</th></tr></thead>
        <tbody>{pr}</tbody>
      </table></div>
      <p class="price-note">현장 상황(관 길이·접근성·상태)에 따라 비용이 달라질 수 있어 정확한 금액은 무료 상담으로 안내드립니다.</p>

      <h2>관련 서비스</h2>
      <div class="card-grid">{rel}</div>
    </div>
    {SIDEBAR}
  </div>
</section>
{case_grid()}
{faq_block}
{bottom_cta()}
</main>
"""
    page(f"service/{slug}.html", title, desc, f"{S}/service/{slug}.html", body,
         jsonld=breadcrumb_jsonld(crumbs) + faq_ld)


service_page(
    "sewer-clog", "하수구막힘", "Service · 하수구막힘",
    "하수구막힘, 역류 전에 근본부터 뚫습니다",
    "주방·화장실·바닥 배수구의 하수구막힘을 스프링·관통기·고압세척으로 신속 해결하고, CCTV로 원인을 진단해 재발을 막습니다.",
    "하수구막힘 | 상업시설 배관 막힘 24시간 출동 - 스피드 배관공사",
    "하수구막힘·역류·악취 24시간 출동. 가정집·상가 반복 막힘을 CCTV 진단·고압세척으로 근본 해결.",
    ["물이 천천히 빠지거나 역류한다", "배수구에서 악취가 올라온다", "여러 배수구가 동시에 막힌다", "변기 물이 잘 내려가지 않는다"],
    ["기름때·음식물 찌꺼기 누적 (주방)", "머리카락·이물질 엉킴 (화장실)", "배관 구배 불량·이물질 투입", "노후관 내부 스케일 침착"],
    [("증상 확인 및 진단", "막힘 위치와 정도를 파악하고 필요 시 CCTV로 관 내부를 확인합니다."),
     ("관통 작업", "전동 스프링·관통기로 막힘을 1차 제거합니다."),
     ("고압세척", "기름때·스케일이 원인이면 고압수로 관 벽을 세척해 흐름을 회복합니다."),
     ("점검 및 재발 방지 안내", "배수 상태를 확인하고 정기 관리·구배 개선 등을 제안합니다.")],
    ["전동 스프링", "관통기(오거)", "고압세척기", "CCTV 관로카메라", "악취 차단 트랩"],
    [("일반 하수구", "스프링/관통 1개소", "5만원~"),
     ("주방 배관", "기름때 고압세척 병행", "별도 산정"),
     ("바닥 배수구", "이물질 제거", "4만원~"),
     ("반복 막힘", "CCTV 진단 + 근본 처리", "현장 견적")],
    [("하수구막힘은 왜 자꾸 반복되나요?", "관 내부에 기름때나 스케일이 얇게 남으면 다시 빠르게 쌓입니다. 일시적 뚫음이 아니라 고압세척으로 관 벽까지 세척하고 CCTV로 구배·파손 여부를 확인하면 재발을 크게 줄일 수 있습니다."),
     ("영업 중에도 작업이 가능한가요?", "네. 소음·냄새를 최소화하는 장비로 영업에 지장이 적게 작업하며, 필요 시 야간·새벽 시간대 작업도 조율합니다.")],
    [("고압세척", "관 내부 기름때·스케일 완전 제거", "/service/high-pressure.html"),
     ("CCTV 관로검사", "막힘 원인을 영상으로 진단", "/service/cctv.html"),
     ("누수탐지", "막힘과 함께 의심되는 누수 점검", "/service/leak-detection.html")],
)

service_page(
    "plumbing", "배관공사", "Service · 배관공사",
    "노후관 교체부터 신설까지, 상업시설 배관공사",
    "호텔·상가·빌딩의 급수·배수·오수 배관을 교체·신설·증설합니다. 영업 중단을 최소화하는 야간·단계 시공으로 진행합니다.",
    "배관공사 | 상업시설 급수·배수 배관 교체·신설 - 스피드 배관공사",
    "배관공사 전문 — 노후관 교체·급수·배수·오수관 신설·증설·누수 보수. 가정집·상업시설 선견적 시공.",
    ["배관이 노후되어 부식·누수가 잦다", "수압이 약하거나 배수가 원활하지 않다", "리모델링으로 배관 재배치가 필요하다", "증축·용도 변경으로 배관 증설이 필요하다"],
    ["설치 후 15년 이상 경과한 금속관 부식", "잦은 막힘으로 인한 관 손상", "동결·외부 충격에 의한 파손", "설계 용량 초과·구배 불량"],
    [("현장 실측 및 설계", "배관 경로·용량·자재를 진단하고 시공안과 견적을 제시합니다."),
     ("자재 준비 및 일정 협의", "PB·스테인리스·주철 등 용도에 맞는 자재를 선정하고 무중단 일정을 조율합니다."),
     ("배관 교체·신설 시공", "구간별 차단·우회로 영업 영향을 최소화하며 시공합니다."),
     ("수압·누수 테스트 및 마감", "통수·가압 테스트로 누수를 확인하고 현장을 복구·정리합니다.")],
    ["배관 절단·나사 가공기", "동관·PB 압착공구", "전기 융착기", "가압 테스트 펌프", "관 검사 카메라"],
    [("노후관 교체", "구간·자재별", "현장 견적"),
     ("급수 배관 신설", "용량·경로별", "현장 견적"),
     ("배수·오수 배관", "구배 재시공 포함", "현장 견적"),
     ("부분 보수", "누수·파손 구간", "10만원~")],
    [("영업을 멈추지 않고 배관을 교체할 수 있나요?", "구간별 차단과 우회 배관, 야간·새벽 시공을 활용해 영업 중단을 최소화합니다. 호텔·상가의 운영 일정에 맞춰 단계 시공을 계획합니다."),
     ("어떤 자재를 사용하나요?", "용도와 수질·압력 조건에 맞춰 스테인리스, PB, 동관, 주철 등을 선정합니다. 견적 시 자재 등급과 보증 내용을 함께 안내합니다.")],
    [("누수탐지", "교체 전 누수 위치 정밀 확인", "/service/leak-detection.html"),
     ("CCTV 관로검사", "배관 상태를 영상으로 진단", "/service/cctv.html"),
     ("하수구막힘", "배수 불량 동반 시 함께 처리", "/service/sewer-clog.html")],
)

service_page(
    "leak-detection", "누수탐지", "Service · 누수탐지",
    "벽을 뜯지 않고 누수 지점을 찾습니다",
    "청음·열화상·가스 탐지 등 비파괴 장비로 누수 위치를 정확히 특정합니다. 불필요한 철거를 줄여 복구 비용과 시간을 아낍니다.",
    "누수탐지 | 비파괴 정밀 누수 탐지 - 스피드 배관공사",
    "누수탐지 전문 — 벽·바닥 철거 없이 청음·열화상·가스 탐지로 숨은 누수를 정확히 진단. 24시간 상담.",
    ["수도 사용이 없는데 계량기가 돈다", "벽·천장·바닥에 물 얼룩·곰팡이가 있다", "원인 모를 수도 요금 급증", "아래층으로 물이 새 분쟁이 우려된다"],
    ["배관 이음부 노화·균열", "콘크리트 매립 배관 부식", "외부 충격·동결에 의한 미세 파손", "방수층 손상으로 인한 침투"],
    [("현장 청취 및 1차 점검", "누수 정황과 사용 패턴을 확인하고 의심 구간을 좁힙니다."),
     ("비파괴 정밀 탐지", "청음·열화상·가스 추적으로 누수 지점을 특정합니다."),
     ("위치 표시 및 복구안 제시", "최소 철거 범위를 표시하고 보수 방법·비용을 안내합니다."),
     ("보수 및 재점검", "보수 후 가압 테스트로 누수 해소를 확인합니다.")],
    ["청음식 누수탐지기", "열화상 카메라", "추적가스 탐지기", "관로 내시경", "수압 측정기"],
    [("누수 정밀 탐지", "지점당", "10만원~"),
     ("열화상 진단", "구역별", "별도 산정"),
     ("탐지+보수", "패키지", "현장 견적"),
     ("누수 보수", "이음부·구간", "현장 견적")],
    [("정말 벽을 안 뜯고 찾을 수 있나요?", "대부분의 누수는 청음·열화상·가스 탐지로 위치를 특정할 수 있어 철거를 최소화합니다. 다만 매립 깊이나 구조에 따라 일부 확인 작업이 필요할 수 있으며, 사전에 안내드립니다."),
     ("탐지만 받고 보수는 따로 맡겨도 되나요?", "가능합니다. 탐지 결과 리포트와 위치 표시를 제공하므로 자체 보수나 타 업체 보수에도 활용할 수 있습니다.")],
    [("배관공사", "탐지 후 누수 구간 보수·교체", "/service/plumbing.html"),
     ("CCTV 관로검사", "배수관 내부 파손 확인", "/service/cctv.html"),
     ("고압세척", "보수 전 관 내부 세척", "/service/high-pressure.html")],
)

service_page(
    "high-pressure", "고압세척", "Service · 고압세척",
    "관 벽까지 새것처럼, 고압세척",
    "고압수로 관 내부의 기름때·슬러지·스케일을 제거해 배수 흐름을 회복합니다. 주방·정화조·오수관 등 누적 오염에 효과적입니다.",
    "고압세척 | 배관 내부 기름때·스케일 제거 - 스피드 배관공사",
    "고압세척 전문 — 주방 배관·오수관 기름때·스케일 완전 제거. 반복 하수구막힘 근본 해결·정기 관리.",
    ["주기적으로 배수가 느려진다", "주방 배관에서 기름 냄새가 난다", "막힘이 짧은 주기로 반복된다", "오수·정화조 관로에 슬러지가 쌓였다"],
    ["식용유·유지방의 관 벽 침착", "세제·미네랄 스케일 누적", "장기 미세척으로 인한 협착", "구배 불량으로 침전물 정체"],
    [("관로 상태 진단", "필요 시 CCTV로 오염 정도와 구간을 확인합니다."),
     ("고압세척 시공", "회전·직진 노즐을 사용해 관 벽의 오염을 박리·배출합니다."),
     ("배출물 처리", "세척으로 떨어진 슬러지를 안전하게 수거·처리합니다."),
     ("정기 관리 제안", "오염 주기를 고려한 정기 세척 주기를 제안합니다.")],
    ["고압세척기(워터젯)", "회전·직진 노즐", "릴 호스 시스템", "CCTV 관로카메라", "슬러지 수거 장비"],
    [("주방 배관 세척", "구간·길이별(m당)", "별도 산정"),
     ("오수·정화조 관로", "현장 상태별", "현장 견적"),
     ("정기 관리 계약", "월/분기 단위", "할인 적용"),
     ("CCTV 진단 병행", "세척 전후 비교", "8만원~")],
    [("얼마나 자주 세척하면 좋나요?", "주방 사용량이 많은 호텔·식당은 분기 1회, 일반 상가는 반기~연 1회를 권장합니다. 사용 패턴을 보고 적정 주기를 함께 정해 드립니다."),
     ("세척하면 막힘이 정말 줄어드나요?", "관 벽의 기름때·스케일이 제거되면 유효 단면이 회복되어 막힘 빈도가 크게 줄어듭니다. 정기 관리와 병행하면 효과가 오래 유지됩니다.")],
    [("하수구막힘", "막힘 발생 시 즉시 관통", "/service/sewer-clog.html"),
     ("CCTV 관로검사", "세척 효과를 영상으로 확인", "/service/cctv.html"),
     ("배관공사", "세척으로 회복 어려운 노후관 교체", "/service/plumbing.html")],
)

service_page(
    "cctv", "CCTV 관로검사", "Service · CCTV 관로검사",
    "배관 속을 눈으로 확인하는 CCTV 진단",
    "관로 전용 카메라로 배관 내부를 촬영해 막힘·파손·역구배·이물질을 정확히 진단합니다. 추측이 아닌 근거로 작업을 결정합니다.",
    "CCTV 관로검사 | 배관 내부 영상 진단 - 스피드 배관공사",
    "CCTV 관로검사 — 배관 내부 막힘·균열·역구배를 영상 진단. 반복 하수구막힘·누수 원인 정확 파악.",
    ["막힘·누수가 반복되는데 원인을 모른다", "배관 매입 위치·경로를 확인하고 싶다", "인수인계·하자 점검 근거가 필요하다", "공사 전 배관 상태를 진단하고 싶다"],
    ["관 내부 균열·이음부 이탈", "역구배·처짐으로 인한 정체", "이물질·뿌리 침입", "노후로 인한 협착"],
    [("카메라 투입", "관경에 맞는 관로 카메라를 배관에 투입합니다."),
     ("내부 촬영·진단", "막힘·파손·구배 상태를 실시간 영상으로 확인합니다."),
     ("위치 측정", "문제 지점의 거리·깊이를 측정해 위치를 특정합니다."),
     ("리포트 제공", "영상과 진단 결과를 바탕으로 보수안을 제안합니다.")],
    ["관로 CCTV 카메라", "거리 측정 시스템", "자주식 카메라(대형관)", "위치 추적 송신기", "영상 기록 장비"],
    [("관로 영상 진단", "구간별", "8만원~"),
     ("위치 측정 포함", "거리·깊이 측정", "별도 산정"),
     ("진단 리포트", "영상·소견 제공", "포함"),
     ("공사 전 진단", "시공 견적 연계", "현장 견적")],
    [("검사 영상이나 결과를 받을 수 있나요?", "네. 촬영 영상과 문제 지점, 소견을 정리해 제공합니다. 하자 점검·인수인계·보험 청구 근거로도 활용할 수 있습니다."),
     ("어떤 배관까지 검사가 가능한가요?", "소형 생활배관부터 대형 오수·우수관까지 관경에 맞는 카메라로 검사합니다. 자주식 카메라로 긴 구간도 진단 가능합니다.")],
    [("하수구막힘", "진단 후 막힘 즉시 처리", "/service/sewer-clog.html"),
     ("고압세척", "오염 구간 고압 세척", "/service/high-pressure.html"),
     ("배관공사", "파손 구간 교체·보수", "/service/plumbing.html")],
)


# ===========================================================================
# 서비스 인덱스
# ===========================================================================
SVC_LIST = [
    ("하수구막힘", "역류·악취·배수 지연을 근본 원인부터 해결합니다.", "/service/sewer-clog.html"),
    ("배관공사", "노후관 교체·신설·증설 등 종합 배관 시공.", "/service/plumbing.html"),
    ("누수탐지", "벽·바닥 철거 없이 비파괴 정밀 탐지.", "/service/leak-detection.html"),
    ("고압세척", "관 내부 기름때·스케일을 고압수로 완전 제거.", "/service/high-pressure.html"),
    ("CCTV 관로검사", "배관 내부를 영상으로 진단해 원인 특정.", "/service/cctv.html"),
    ("변기·싱크대막힘", "변기·싱크대·바닥배수구 막힘 즉시 처리.", "/service/sewer-clog.html"),
    ("정화조·동파", "정화조 관리·청소 및 겨울철 동파 복구.", "/service/plumbing.html"),
    ("배관 리모델링", "상가·사무실 인테리어 배관 재배치·정비.", "/service/plumbing.html"),
]
svc_cards = "".join(f'<a class="link-card" href="{u}"><h3>{n}</h3><p>{p}</p></a>' for n, p, u in SVC_LIST)
svc_body = f"""{phero("Services", "서비스안내", "상업시설에서 발생하는 모든 배관 문제를 한 곳에서 해결합니다. 각 서비스를 선택해 자세한 작업 방법과 예상 요금을 확인하세요.", [("홈","/"),("서비스안내",None)])}
<main>
<section class="section">
  <div class="container">
    <div class="card-grid">{svc_cards}</div>
  </div>
</section>
{bottom_cta()}
</main>
"""
page("service/index.html", "서비스안내 | 하수구막힘·배관공사·누수탐지·고압세척 - 스피드 배관공사",
     "하수구막힘·배관공사·누수탐지·고압세척·CCTV 관로검사 — 스피드 배관공사 전체 서비스 한눈에.",
     S + "/service/", svc_body,
     jsonld=breadcrumb_jsonld([("홈","/"),("서비스안내","/service/")]))

# ===========================================================================
# 지역 허브
# ===========================================================================
def area_index():
    SIDO = ["서울특별시","부산광역시","대구광역시","인천광역시","광주광역시","대전광역시","울산광역시",
            "세종특별자치시","경기도","강원특별자치도","충청북도","충청남도","전북특별자치도","전라남도",
            "경상북도","경상남도","제주특별자치도"]
    links = {"서울특별시":"/area/seoul/","부산광역시":"/area/busan/","대구광역시":"/area/daegu/",
             "인천광역시":"/area/incheon/","광주광역시":"/area/gwangju/","대전광역시":"/area/daejeon/",
             "울산광역시":"/area/ulsan/","세종특별자치시":"/area/sejong/","경기도":"/area/gyeonggi/",
             "강원특별자치도":"/area/gangwon/","충청북도":"/area/chungbuk/","충청남도":"/area/chungnam/",
             "전북특별자치도":"/area/jeonbuk/","전라남도":"/area/jeonnam/","경상북도":"/area/gyeongbuk/",
             "경상남도":"/area/gyeongnam/","제주특별자치도":"/area/jeju/"}
    cards = ""
    for s in SIDO:
        u = links.get(s, "/area/")
        cards += f'<a class="link-card" href="{u}"><h3>{s}</h3></a>'
    body = f"""{phero("Nationwide", "지역별 서비스", "스피드 배관공사는 전국 17개 시·도에서 호텔·상가·빌딩 배관 서비스를 제공합니다. 지역을 선택하면 해당 지역의 출동 안내와 시공사례를 확인할 수 있습니다.", [("홈","/"),("지역별 서비스",None)])}
<main>
<section class="section">
  <div class="container">
    <div class="card-grid">{cards}</div>
    <p class="price-note" style="margin-top:24px;">※ 읍·면·동 단위 페이지는 별도로 생성하지 않으며, 각 시·군·구 페이지 내 '서비스 가능 지역' 목록으로 안내합니다.</p>
  </div>
</section>
{bottom_cta()}
</main>
"""
    page("area/index.html", "지역별 서비스 | 전국 17개 시·도 상업시설 배관 - 스피드 배관공사",
         "전국 17개 시·도 하수구막힘·배관공사·누수탐지·고압세척 24시간 출동. 지역별 서비스 안내.",
         S + "/area/", body,
         jsonld=breadcrumb_jsonld([("홈","/"),("지역별 서비스","/area/")]))
area_index()


def sido_page(slug, name, short, intro, districts, district_links, cases_html, phone_note):
    crumbs = [("홈","/"),("지역별 서비스","/area/"),(name, None)]
    # 공식 데이터의 전체 시군구를 링크 카드로 렌더링
    full = OFFICIAL.get(name)
    dcards = ""
    if full:
        for d in full:
            u = gungu_url(slug, d)
            dcards += f'<a class="link-card" href="{u}"><h3>{d}</h3></a>'
    else:
        # 세종 등 시군구가 없는 경우: 전달된 동 목록을 비링크 카드로 안내
        for d in districts:
            dcards += f'<div class="link-card" style="opacity:.9"><h3>{d}</h3></div>'
    body = f"""{phero(f"{name} 서비스", f"{name} 배관·하수구막힘 24시간 출동", intro, crumbs)}
<main>
<section class="section">
  <div class="container layout-sidebar">
    <div class="prose">
      <h2>{name} 상업시설 배관, 스피드가 함께합니다</h2>
      <p>{short}</p>
      <p>{intro}</p>

      <h2>{name} 시·군·구 서비스</h2>
      <p>아래 지역을 선택하면 해당 시·군·구의 출동 안내를 확인할 수 있습니다.</p>
      <div class="card-grid">{dcards}</div>

      <h2>{name} 시공 사례</h2>
      {cases_html}

      <h2>이런 현장에서 자주 불러주십니다</h2>
      <ul class="ticks">
        <li>호텔·모텔·숙박시설 주방 및 객실 층 배관</li>
        <li>상가·식당 밀집 지역의 기름때 하수구막힘</li>
        <li>오피스빌딩 지하 메인 배관 누수·교체</li>
      </ul>
    </div>
    <aside class="sidebar-card">
      <h3>{name} 상담</h3>
      <p>{phone_note}</p>
      <a class="phone-big" href="tel:0000-0000">0000-0000</a>
      <p style="margin-bottom:18px;">카카오톡 상담 @스피드배관</p>
      <a class="btn btn--primary btn--block" href="tel:0000-0000">☎ 전화 상담</a>
      <a class="btn btn--ghost-light btn--block" href="https://t.me/googleseolab" target="_blank" rel="noopener" style="margin-top:10px;">광고문의 상담</a>
    </aside>
  </div>
</section>
{bottom_cta(h2=f"{name} 어디든, 지금 출동합니다")}
</main>
"""
    title = f"{name} 배관·하수구막힘·누수탐지 24시간 출동 - 스피드 배관공사"
    desc = f"{name} 하수구막힘·배관공사·누수탐지·고압세척 24시간 출동. 가정집·상업시설 전 지역 신속 상담."
    page(f"area/{slug}/index.html", title, desc, f"{S}/area/{slug}/", body,
         jsonld=breadcrumb_jsonld(crumbs))


# 시·군·구 상세 페이지 링크 레지스트리 (시도 페이지의 구 카드 → 상세 페이지 연결)
GUNGU_LINKS = {
    "seoul":    {"강남구":"/area/seoul/gangnam-gu/", "서초구":"/area/seoul/seocho-gu/", "송파구":"/area/seoul/songpa-gu/"},
    "gyeonggi": {"성남시":"/area/gyeonggi/seongnam-si/", "수원시":"/area/gyeonggi/suwon-si/"},
    "busan":    {"해운대구":"/area/busan/haeundae-gu/"},
    "incheon":  {"연수구":"/area/incheon/yeonsu-gu/"},
}

# --- 서울 ---
sido_page(
    "seoul", "서울특별시",
    "강남·중구·영등포 등 업무·상업 밀집 지역이 많은 서울은 야간에도 영업하는 시설이 많아 즉시 대응이 중요합니다. 스피드 배관공사는 서울 전역에 작업팀을 배치해 평균 30분 내 출동을 목표로 운영합니다.",
    "호텔·백화점·대형 상가가 밀집한 서울 도심 특성상 주방 기름때로 인한 하수구막힘과 노후 빌딩의 배관 누수 의뢰가 많습니다. 고압세척과 CCTV 진단을 기본으로 재발까지 관리합니다.",
    ["강남구","서초구","송파구","중구","종로구","영등포구","마포구","용산구","강서구","구로구","성동구","광진구"],
    GUNGU_LINKS["seoul"],
    """<article class="case-card" style="max-width:520px;"><div class="ba"><figure class="before"><img src="/assets/img/case1.svg" alt="서울 강남 호텔 주방 하수구 막힘 전" loading="lazy" width="400" height="300"><figcaption>BEFORE</figcaption></figure><figure class="after"><img src="/assets/img/case1-after.svg" alt="서울 강남 호텔 주방 고압세척 후" loading="lazy" width="400" height="300"><figcaption>AFTER</figcaption></figure></div><div class="case-body"><span class="case-tag">강남구 · 호텔</span><h3>강남 호텔 주방 배관 고압세척</h3><p>반복되던 역류를 고압세척으로 근본 해결.</p></div></article>""",
    "서울 전역 24시간 출동. 야간·새벽 긴급 작업 가능.")

# --- 경기 ---
sido_page(
    "gyeonggi", "경기도",
    "성남·수원·고양·용인 등 인구와 상권이 빠르게 성장하는 경기도는 대형 쇼핑몰과 신축 상가, 물류시설의 배관 수요가 많습니다. 권역별 작업팀으로 넓은 지역을 빠르게 커버합니다.",
    "신도시 상가의 주방 배관 막힘부터 노후 공장·물류센터의 대형 오수관 고압세척까지 폭넓게 대응합니다. 경기 남부·북부 권역에 작업팀을 분산 배치합니다.",
    ["성남시","수원시","용인시","고양시","부천시","안양시","화성시","남양주시","평택시","의정부시","파주시","김포시"],
    GUNGU_LINKS["gyeonggi"],
    """<article class="case-card" style="max-width:520px;"><div class="ba"><figure class="before"><img src="/assets/img/case2.svg" alt="경기 성남 상가 천장 누수 전" loading="lazy" width="400" height="300"><figcaption>BEFORE</figcaption></figure><figure class="after"><img src="/assets/img/case2-after.svg" alt="경기 성남 상가 누수 보수 후" loading="lazy" width="400" height="300"><figcaption>AFTER</figcaption></figure></div><div class="case-body"><span class="case-tag">성남시 · 상가</span><h3>성남 상가 천장 누수 비파괴 탐지</h3><p>철거 없이 누수 지점을 특정해 복구비 최소화.</p></div></article>""",
    "경기 남부·북부 권역 24시간 출동.")

# --- 부산 ---
sido_page(
    "busan", "부산광역시",
    "해운대·서면·남포동 등 관광·상업 중심지가 많은 부산은 호텔과 식당가의 배관 관리 수요가 꾸준합니다. 해안가 특성상 노후 배관의 부식·누수 의뢰도 많습니다.",
    "관광 성수기 호텔의 객실 층 배수 긴급 대응과, 오래된 상가 건물의 노후관 교체를 함께 진행합니다. 해운대·중구·부산진구 권역에 작업팀을 배치합니다.",
    ["해운대구","부산진구","중구","동래구","남구","수영구","사하구","북구","금정구","연제구","사상구","기장군"],
    GUNGU_LINKS["busan"],
    """<article class="case-card" style="max-width:520px;"><div class="ba"><figure class="before"><img src="/assets/img/case3.svg" alt="부산 해운대 오피스빌딩 지하 배관 노후 전" loading="lazy" width="400" height="300"><figcaption>BEFORE</figcaption></figure><figure class="after"><img src="/assets/img/case3-after.svg" alt="부산 해운대 오피스빌딩 배관 교체 후" loading="lazy" width="400" height="300"><figcaption>AFTER</figcaption></figure></div><div class="case-body"><span class="case-tag">해운대구 · 빌딩</span><h3>해운대 오피스빌딩 지하 노후관 교체</h3><p>부식 메인 배관을 야간 무중단 교체.</p></div></article>""",
    "부산 전역 24시간 출동. 해안가 노후 배관 전문.")


# --- 서울 강남구 종합 페이지 + 행정동 하위 페이지는 파일 하단 별도 블록에서 생성 ---


# ===========================================================================
# 시공사례
# ===========================================================================
CASES = [
    ("호텔 · 하수구막힘","강남 호텔 주방 배관 고압세척","기름때 누적으로 반복되던 역류를 고압세척으로 근본 해결. 정기 관리 계약으로 전환.","case1.svg","case1-after.svg"),
    ("상가 · 누수탐지","성남 상가 천장 누수 비파괴 탐지","철거 없이 누수 지점을 특정해 복구 범위와 비용을 최소화.","case2.svg","case2-after.svg"),
    ("빌딩 · 배관공사","해운대 오피스빌딩 지하 노후관 교체","부식이 진행된 메인 배관을 야간 무중단으로 교체.","case3.svg","case3-after.svg"),
    ("식당 · 고압세척","서면 식당가 주방 오수관 고압세척","장기 미세척 오수관의 슬러지를 제거해 배수 정상화.","case1.svg","case1-after.svg"),
    ("오피스 · CCTV","여의도 오피스 배관 CCTV 진단","반복 막힘의 원인을 영상으로 특정해 정확히 보수.","case2.svg","case2-after.svg"),
    ("모텔 · 변기막힘","수원 숙박시설 객실 변기 긴급 처리","주말 야간 긴급 출동으로 영업 차질 없이 해결.","case3.svg","case3-after.svg"),
]
cards = ""
for tag, t, d, b, a in CASES:
    cards += f"""<article class="case-card"><div class="ba"><figure class="before"><img src="/assets/img/{b}" alt="{t} 작업 전" loading="lazy" width="400" height="300"><figcaption>BEFORE</figcaption></figure><figure class="after"><img src="/assets/img/{a}" alt="{t} 작업 후" loading="lazy" width="400" height="300"><figcaption>AFTER</figcaption></figure></div><div class="case-body"><span class="case-tag">{tag}</span><h3>{t}</h3><p>{d}</p></div></article>"""
cases_body = f"""{phero("Before / After","시공사례","막힘과 누수, 결과로 증명합니다. 호텔·상가·빌딩 등 상업시설에서 진행한 실제 시공 사례를 소개합니다.",[("홈","/"),("시공사례",None)])}
<main>
<section class="section">
  <div class="container"><div class="case-grid">{cards}</div></div>
</section>
{bottom_cta()}
</main>
"""
page("cases.html","시공사례 | 상업시설 배관 Before/After - 스피드 배관공사",
     "시공사례 — 주방 고압세척, 상가 누수탐지, 빌딩 노후관 교체 등 배관 작업 Before/After.",
     S + "/cases.html", cases_body, jsonld=breadcrumb_jsonld([("홈","/"),("시공사례","/cases.html")]))

# ===========================================================================
# 요금안내
# ===========================================================================
price_body = f"""{phero("Pricing","요금안내","현장 진단 후 선견적을 드리는 것이 원칙입니다. 아래 표는 참고용 단가이며, 관 길이·접근성·상태에 따라 달라집니다. 사전 협의 없는 추가금은 청구하지 않습니다.",[("홈","/"),("요금안내",None)])}
<main>
<section class="section">
  <div class="container prose" style="max-width:920px;">
    <h2>대표 서비스 요금</h2>
    <div class="price-table-wrap"><table class="price-table">
      <caption>※ 부가세 별도 · 현장 진단 후 선견적 제공</caption>
      <thead><tr><th scope="col">서비스 항목</th><th scope="col">작업 범위</th><th scope="col">예상 요금</th></tr></thead>
      <tbody>
        <tr><td>하수구막힘</td><td>일반 관로 뚫음 (스프링/관통)</td><td class="unit">5만원~</td></tr>
        <tr><td>변기·싱크대막힘</td><td>이물질 제거·압력 관통</td><td class="unit">4만원~</td></tr>
        <tr><td>바닥 배수구</td><td>이물질 제거</td><td class="unit">4만원~</td></tr>
        <tr><td>고압세척</td><td>관 내부 기름때·스케일 세척 (m당)</td><td class="unit">별도 산정</td></tr>
        <tr><td>누수탐지</td><td>비파괴 정밀 탐지 (지점당)</td><td class="unit">10만원~</td></tr>
        <tr><td>CCTV 관로검사</td><td>관 내부 영상 진단</td><td class="unit">8만원~</td></tr>
        <tr><td>배관공사</td><td>노후관 교체·신설</td><td class="unit">현장 견적</td></tr>
        <tr><td>정화조 관리</td><td>청소·준설</td><td class="unit">현장 견적</td></tr>
        <tr><td>동파 복구</td><td>해빙·보수</td><td class="unit">현장 견적</td></tr>
      </tbody>
    </table></div>

    <h2>요금이 달라지는 요인</h2>
    <ul class="ticks">
      <li>막힘·누수의 위치와 정도, 관의 길이·관경</li>
      <li>현장 접근성(층수·매립 여부·작업 공간)</li>
      <li>야간·휴일 긴급 출동 여부</li>
      <li>사용 자재의 등급과 보증 범위</li>
    </ul>

    <h2>상업시설 정기 관리 계약</h2>
    <p>호텔·식당·빌딩 등 주기적 관리가 필요한 시설은 월/분기 단위 정기 관리 계약으로 <strong>우선 출동과 요금 할인</strong>을 받을 수 있습니다. 세금계산서·거래명세서 발행을 지원합니다.</p>
    <p style="margin-top:24px;"><a class="btn btn--primary" href="/contact.html">정확한 견적 무료 상담</a></p>
  </div>
</section>
{bottom_cta()}
</main>
"""
page("price.html","요금안내 | 하수구막힘·누수탐지·고압세척 예상 요금 - 스피드 배관공사",
     "요금안내 — 하수구막힘·누수탐지·고압세척·배관공사 참고 단가. 선견적 후작업, 추가금 없음.",
     S + "/price.html", price_body, jsonld=breadcrumb_jsonld([("홈","/"),("요금안내","/price.html")]))

# ===========================================================================
# 고객후기
# ===========================================================================
REV = [
    (5,"야간에 호텔 객실 층 배수가 막혔는데 30분 만에 오셔서 영업에 지장 없이 해결해주셨어요. 견적도 먼저 정확히 알려주셔서 믿음이 갔습니다.","김","김OO 지배인","서울 강남 · 호텔"),
    (5,"상가 화장실 누수 원인을 다른 곳에선 못 찾았는데, 벽 안 뜯고 정확히 짚어주셔서 복구비를 크게 아꼈습니다. 세금계산서도 깔끔하게 처리됐어요.","이","이OO 점주","경기 성남 · 상가"),
    (5,"빌딩 지하 배관 교체를 야간 무중단으로 진행해 주셔서 입주사 불만 없이 끝냈습니다. 정기 관리까지 맡기기로 했어요.","박","박OO 관리소장","부산 해운대 · 오피스빌딩"),
    (5,"주방 배관이 자주 막혀 골치였는데 고압세척 후로 확실히 좋아졌습니다. 정기 세척 주기도 잡아주셔서 편해요.","최","최OO 대표","서울 마포 · 식당"),
    (5,"CCTV로 막힘 원인을 직접 보여주시니 신뢰가 갔습니다. 불필요한 공사 없이 필요한 부분만 정확히.","정","정OO 실장","인천 · 상가"),
    (4,"주말 새벽에 변기 막힘으로 급하게 연락드렸는데 빠르게 와주셨어요. 응대도 친절했습니다.","한","한OO 사장","수원 · 숙박"),
]
rcards = ""
for star, txt, av, who, where in REV:
    stars = "★"*star + "☆"*(5-star)
    rcards += f"""<article class="review-card"><div class="stars" aria-label="별점 {star}점">{stars}</div><blockquote>"{txt}"</blockquote><div class="review-meta"><span class="review-avatar">{av}</span><div><div class="who">{who}</div><div class="where">{where}</div></div></div></article>"""
review_body = f"""{phero("Reviews","고객후기","실제 고객이 남긴 후기입니다. 더 많은 후기는 네이버 플레이스에서 확인하실 수 있습니다.",[("홈","/"),("고객후기",None)])}
<main>
<section class="section">
  <div class="container">
    <div class="review-grid">{rcards}</div>
    <p style="text-align:center;margin-top:36px;"><a class="btn btn--primary" href="https://map.naver.com/" rel="noopener" target="_blank">네이버 플레이스에서 더 보기</a></p>
  </div>
</section>
{bottom_cta()}
</main>
"""
page("review.html","고객후기 | 상업시설 배관 서비스 후기 - 스피드 배관공사",
     "고객후기 — 하수구막힘·누수탐지·고압세척 서비스 실제 후기. 누적 평점 4.9 / 327건.",
     S + "/review.html", review_body, jsonld=breadcrumb_jsonld([("홈","/"),("고객후기","/review.html")]))

# ===========================================================================
# FAQ
# ===========================================================================
FAQ_FULL = FAQ_ITEMS + [
    ("출장비나 점검비가 따로 있나요?","현장 진단 후 작업을 진행하는 경우 별도 출장비를 청구하지 않는 것이 원칙입니다. 단순 점검·진단만 진행되는 경우의 비용은 사전에 안내드립니다."),
    ("정기 관리 계약은 어떻게 진행되나요?","시설 규모와 사용량을 진단해 월/분기 단위 관리 주기와 요금을 제안합니다. 계약 시 우선 출동과 요금 할인이 적용됩니다."),
    ("작업 후 문제가 재발하면 어떻게 하나요?","작업 항목별 사후 보증을 적용합니다. 동일 원인으로 재발 시 보증 범위 내에서 재작업해 드리며, 보증 조건은 작업 전 안내합니다."),
]
faq_page_body = f"""{phero("FAQ","자주묻는질문","상담 전 자주 궁금해하시는 내용을 모았습니다. 더 궁금한 점은 언제든 전화로 문의해 주세요.",[("홈","/"),("자주묻는질문",None)])}
<main>
<section class="section">
  <div class="container">
    <div class="faq-list">
{faq_html(FAQ_FULL)}    </div>
  </div>
</section>
{bottom_cta()}
</main>
"""
page("faq.html","자주묻는질문 | 상업시설 배관 서비스 FAQ - 스피드 배관공사",
     "자주 묻는 질문 — 24시간 출동, 선견적 후작업, 누수탐지 방식, 세금계산서 발행 등 안내.",
     S + "/faq.html", faq_page_body, jsonld=breadcrumb_jsonld([("홈","/"),("자주묻는질문","/faq.html")]) + faq_jsonld(FAQ_FULL))

# ===========================================================================
# 회사소개
# ===========================================================================
about_body = f"""{phero("About","회사소개","상업시설 배관, 멈추지 않는 신속함. 스피드 배관공사는 호텔·상가·오피스빌딩의 배관을 책임지는 B2B 전문 파트너입니다.",[("홈","/"),("회사소개",None)])}
<main>
<section class="section">
  <div class="container prose" style="max-width:880px;">
    <h2>우리가 일하는 방식</h2>
    <p>스피드 배관공사는 '영업을 멈추지 않게 한다'는 한 가지 원칙에서 출발합니다. 호텔의 객실, 식당의 주방, 빌딩의 지하 배관은 한 번 멈추면 곧 매출 손실로 이어집니다. 그래서 우리는 <strong>빠른 출동</strong>과 <strong>정직한 견적</strong>, 그리고 <strong>재발을 막는 근본 처리</strong>를 기준으로 일합니다.</p>

    <h2>우리의 약속</h2>
    <ul class="ticks">
      <li><strong>24시간 출동</strong> — 야간·휴일에도 가까운 작업팀이 즉시 움직입니다.</li>
      <li><strong>선견적 후작업</strong> — 비용을 먼저 안내하고, 동의 후에만 작업합니다.</li>
      <li><strong>상업시설 전문</strong> — 대형 배관·설비에 맞는 인력과 장비를 갖췄습니다.</li>
      <li><strong>투명한 거래</strong> — 세금계산서·현금영수증 발행, 정기 관리 계약 지원.</li>
    </ul>

    <h2>전문 장비</h2>
    <div class="chips"><span>고압세척기(워터젯)</span><span>CCTV 관로카메라</span><span>청음식 누수탐지기</span><span>열화상 카메라</span><span>전동 스프링·관통기</span><span>전기 융착기</span><span>가압 테스트 펌프</span></div>

    <h2>회사 정보</h2>
    <div class="price-table-wrap"><table class="price-table">
      <tbody>
        <tr><td>상호</td><td colspan="2">스피드 배관공사 (SPEED PLUMBING)</td></tr>
        <tr><td>대표자</td><td colspan="2">(미정)</td></tr>
        <tr><td>사업자등록번호</td><td colspan="2">000-00-00000</td></tr>
        <tr><td>주소</td><td colspan="2">(미정)</td></tr>
        <tr><td>대표전화</td><td colspan="2">0000-0000</td></tr>
        <tr><td>카카오톡</td><td colspan="2">@스피드배관</td></tr>
        <tr><td>영업시간</td><td colspan="2">연중무휴 24시간</td></tr>
      </tbody>
    </table></div>
  </div>
</section>
{bottom_cta()}
</main>
"""
page("about.html","회사소개 | 상업시설 전문 B2B 배관 파트너 - 스피드 배관공사",
     "회사소개 — 가정집·상업시설 배관 전문 스피드 배관공사. 24시간 출동·선견적 후작업·전문 장비.",
     S + "/about.html", about_body, jsonld=breadcrumb_jsonld([("홈","/"),("회사소개","/about.html")]))

# ===========================================================================
# 상담문의
# ===========================================================================
contact_body = f"""{phero("Contact","상담문의","전화 한 통이면 가장 가까운 전문 작업팀이 움직입니다. 24시간 언제든 연락 주시고, 견적 폼으로도 신청하실 수 있습니다.",[("홈","/"),("상담문의",None)])}
<main>
<section class="section">
  <div class="container layout-sidebar">
    <div>
      <h2>광고문의 상담</h2>
      <p class="lead" style="margin-bottom:24px;">아래 정보를 남겨주시면 빠르게 연락드려 현장 진단·견적을 안내해 드립니다.</p>
      <form data-quote-form novalidate>
        <div class="form-grid">
          <div class="field"><label for="name">이름/담당자 <span class="req">*</span></label><input id="name" name="name" type="text" required autocomplete="name"></div>
          <div class="field"><label for="phone">연락처 <span class="req">*</span></label><input id="phone" name="phone" type="tel" required autocomplete="tel" placeholder="010-0000-0000"></div>
          <div class="field"><label for="facility">시설 유형</label>
            <select id="facility" name="facility">
              <option value="">선택</option><option>호텔·숙박</option><option>상가·식당</option><option>오피스빌딩</option><option>공장·물류</option><option>기타</option>
            </select>
          </div>
          <div class="field"><label for="service">필요 서비스</label>
            <select id="service" name="service">
              <option value="">선택</option><option>하수구막힘</option><option>배관공사</option><option>누수탐지</option><option>고압세척</option><option>CCTV 관로검사</option><option>기타</option>
            </select>
          </div>
          <div class="field full"><label for="region">지역</label><input id="region" name="region" type="text" placeholder="예) 서울 강남구"></div>
          <div class="field full"><label for="msg">증상/요청 내용</label><textarea id="msg" name="msg" placeholder="증상과 현장 상황을 적어주시면 더 정확히 안내해 드립니다."></textarea></div>
          <div class="field full">
            <label class="form-consent"><input type="checkbox" name="consent" required style="margin-top:4px;"> <span>개인정보 수집·이용에 동의합니다. (상담 목적, 보관 후 파기)</span></label>
          </div>
          <div class="field full">
            <button class="btn btn--primary btn--lg" type="submit">상담 신청하기</button>
            <p class="form-status price-note" role="status" hidden></p>
          </div>
        </div>
      </form>
    </div>
    <aside class="sidebar-card">
      <h3>바로 연락하기</h3>
      <p>24시간 상업시설 전문 출동. 급하실 땐 전화가 가장 빠릅니다.</p>
      <a class="phone-big" href="tel:0000-0000">0000-0000</a>
      <ul class="info-list" style="margin-top:18px;color:#BFD0E8;list-style:none;">
        <li style="display:block;color:#BFD0E8;">카카오톡 상담: <strong style="color:#fff;">@스피드배관</strong></li>
        <li style="display:block;color:#BFD0E8;">영업시간: <strong style="color:#fff;">연중무휴 24시간</strong></li>
      </ul>
      <a class="btn btn--primary btn--block" href="tel:0000-0000" style="margin-top:16px;">☎ 전화 상담</a>
      <a class="btn btn--ghost-light btn--block" href="https://pf.kakao.com/" target="_blank" rel="noopener" style="margin-top:10px;">카카오톡 상담</a>
    </aside>
  </div>
</section>
</main>
"""
page("contact.html","상담문의 | 무료 견적·24시간 출동 - 스피드 배관공사",
     "상담문의 — 하수구막힘·배관공사·누수탐지·고압세척 24시간 출동. 전화·사진 상담, 선견적 후작업.",
     S + "/contact.html", contact_body, jsonld=breadcrumb_jsonld([("홈","/"),("상담문의","/contact.html")]))

# ===========================================================================
# 404
# ===========================================================================
notfound_body = """<main>
<section class="section" style="text-align:center;min-height:50vh;display:grid;place-items:center;">
  <div class="container" style="max-width:560px;">
    <span class="eyebrow">404</span>
    <h1>페이지를 찾을 수 없습니다</h1>
    <p class="lead">요청하신 페이지가 이동되었거나 존재하지 않습니다. 아래에서 원하시는 정보를 찾아보세요.</p>
    <p style="margin-top:24px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
      <a class="btn btn--primary" href="/">홈으로</a>
      <a class="btn btn--secondary" href="/service/">서비스안내</a>
      <a class="btn btn--secondary" href="/contact.html">상담문의</a>
    </p>
  </div>
</section>
</main>
"""
page("404.html","페이지를 찾을 수 없습니다 (404) - 스피드 배관공사",
     "요청하신 페이지를 찾을 수 없습니다. 스피드 배관공사 홈으로 이동하거나 서비스안내·상담문의를 이용해 주세요.",
     S + "/404.html", notfound_body)

# ===========================================================================
# 개인정보처리방침 / 이용약관 (신뢰 페이지 — 실제 확정 시 내용 보강)
# ===========================================================================
def legal_page(slug, title_h1, eyebrow, intro, sections, seo_title, seo_desc):
    crumbs = [("홈","/"),(title_h1, None)]
    secs = ""
    for h, paras in sections:
        body_ps = "".join(f"<p>{p}</p>" for p in paras)
        secs += f"<h2>{h}</h2>{body_ps}"
    body = f"""{phero(eyebrow, title_h1, intro, crumbs)}
<main>
<section class="section">
  <div class="container prose" style="max-width:840px;">
    <p class="price-note">※ 본 문서는 표준 양식 기반의 예시이며, 사업자 정보 확정 후 실제 내용으로 교체됩니다.</p>
    {secs}
    <h2>문의처</h2>
    <p>개인정보 및 약관 관련 문의는 대표전화(0000-0000) 또는 카카오톡 상담(@스피드배관)으로 연락 주시기 바랍니다.</p>
  </div>
</section>
</main>
"""
    page(f"{slug}.html", seo_title, seo_desc, f"{S}/{slug}.html", body,
         jsonld=breadcrumb_jsonld(crumbs))

legal_page("privacy", "개인정보처리방침", "Privacy Policy",
    "스피드 배관공사는 이용자의 개인정보를 중요하게 생각하며 관련 법령을 준수합니다.",
    [("1. 수집하는 개인정보 항목",
      ["상담·견적 신청 시 이름, 연락처, 지역, 상담 내용을 수집합니다. 통화·문자 상담 과정에서 제공하신 정보가 포함될 수 있습니다."]),
     ("2. 개인정보의 수집·이용 목적",
      ["수집한 개인정보는 상담 응대, 견적 안내, 작업 일정 조율, 사후 관리(A/S) 목적으로만 이용합니다."]),
     ("3. 개인정보의 보유 및 이용 기간",
      ["수집 목적 달성 후 지체 없이 파기합니다. 관련 법령에 따라 보존이 필요한 경우 해당 기간 동안 보관합니다."]),
     ("4. 개인정보의 제3자 제공",
      ["원칙적으로 이용자의 개인정보를 외부에 제공하지 않습니다. 법령에 근거하거나 이용자가 동의한 경우에 한합니다."]),
     ("5. 이용자의 권리",
      ["이용자는 언제든지 자신의 개인정보 열람·정정·삭제·처리정지를 요청할 수 있으며, 요청 시 지체 없이 조치합니다."])],
    "개인정보처리방침 - 스피드 배관공사",
    "스피드 배관공사 개인정보처리방침. 상담·견적 과정에서 수집하는 개인정보의 항목, 이용 목적, 보유 기간, 이용자의 권리를 안내합니다.")

legal_page("terms", "이용약관", "Terms of Service",
    "본 약관은 스피드 배관공사 웹사이트 이용에 관한 기본 사항을 규정합니다.",
    [("제1조 (목적)",
      ["본 약관은 스피드 배관공사가 제공하는 배관 상담·시공 관련 정보 및 서비스 이용 조건을 정함을 목적으로 합니다."]),
     ("제2조 (서비스의 제공)",
      ["회사는 하수구막힘, 배관공사, 누수탐지, 고압세척 등 배관 관련 상담 및 시공 서비스를 제공합니다. 정확한 비용·작업 범위는 현장 진단 후 안내됩니다."]),
     ("제3조 (선견적 후작업)",
      ["회사는 현장 진단 후 비용을 먼저 안내하고, 이용자의 동의를 받은 뒤 작업을 진행하는 것을 원칙으로 합니다. 사전 협의 없는 추가금은 청구하지 않습니다."]),
     ("제4조 (책임의 한계)",
      ["천재지변, 노후·구조적 결함 등 회사의 통제를 벗어난 사유로 인한 손해에 대해서는 책임이 제한될 수 있습니다."]),
     ("제5조 (광고 게재)",
      ["본 사이트에는 제휴 광고가 게재될 수 있으며, 광고 문의는 별도 채널을 통해 접수합니다."])],
    "이용약관 - 스피드 배관공사",
    "스피드 배관공사 이용약관. 서비스 제공 범위, 선견적 후작업 원칙, 책임의 한계 등 웹사이트 및 서비스 이용 조건을 안내합니다.")

print("\\nALL PAGES BUILT.")


# ===========================================================================
# 시도 추가 확장 (각 시도 고유 콘텐츠 — 도어웨이 방지)
# ===========================================================================
def _case(tag, title, desc, b, a, alt_b, alt_a):
    return (f"""<article class="case-card" style="max-width:520px;"><div class="ba">"""
            f"""<figure class="before"><img src="/assets/img/{b}" alt="{alt_b}" loading="lazy" width="400" height="300"><figcaption>BEFORE</figcaption></figure>"""
            f"""<figure class="after"><img src="/assets/img/{a}" alt="{alt_a}" loading="lazy" width="400" height="300"><figcaption>AFTER</figcaption></figure></div>"""
            f"""<div class="case-body"><span class="case-tag">{tag}</span><h3>{title}</h3><p>{desc}</p></div></article>""")

# (slug, name, short, intro, districts, case, phone_note)
SIDO_MORE = [
 ("daegu","대구광역시",
  "동성로·서문시장 등 도심 상권과 산업단지가 함께 있는 대구는 식당가 주방 배관과 공장 오수관 관리 수요가 꾸준합니다. 도심·외곽 권역에 작업팀을 배치해 빠르게 대응합니다.",
  "여름철 무더위로 음식물 부패가 빠른 대구 식당가 특성상 기름때 하수구막힘 의뢰가 많고, 노후 상가 건물의 배관 교체도 자주 진행합니다. 고압세척과 CCTV 진단으로 재발까지 관리합니다.",
  ["중구","동구","서구","남구","북구","수성구","달서구","달성군"],
  _case("중구 · 식당가","동성로 식당 주방 배관 고압세척","여름철 반복되던 기름때 막힘을 고압세척으로 해소.","case1.svg","case1-after.svg","대구 중구 식당 주방 배관 막힘 전","대구 중구 식당 주방 고압세척 후"),
  "대구 도심·외곽 24시간 출동."),
 ("incheon","인천광역시",
  "공항·항만·물류단지와 신도시 상가가 공존하는 인천은 대형 시설의 배관 규모가 크고, 송도·청라 신도시 상가의 신축 배관 수요도 많습니다. 권역별 작업팀으로 폭넓게 대응합니다.",
  "물류·공장 시설의 대형 오수관 고압세척과, 송도·청라 상가의 주방 배관 막힘을 함께 처리합니다. 해안 매립지 특성상 배관 침하·역구배 점검도 CCTV로 진단합니다.",
  ["중구","미추홀구","연수구","남동구","부평구","계양구","서구","강화군"],
  _case("연수구 · 상가","송도 상가 배관 CCTV 진단","반복 막힘 원인을 영상으로 특정해 정확히 보수.","case2.svg","case2-after.svg","인천 연수구 상가 배관 진단 전","인천 연수구 상가 배관 보수 후"),
  "인천 전역·도서 권역 24시간 출동."),
 ("gwangju","광주광역시",
  "충장로·상무지구 등 상업 중심지와 첨단산단을 갖춘 광주는 식당·카페 상권의 배관 관리와 사무빌딩 배관 수요가 많습니다. 시 전역에 작업팀을 운영합니다.",
  "상무지구 오피스빌딩의 누수탐지·배관 교체와, 충장로 상권 식당의 하수구막힘을 함께 대응합니다. 선견적 후작업으로 비용을 먼저 확인하고 진행합니다.",
  ["동구","서구","남구","북구","광산구"],
  _case("서구 · 빌딩","상무지구 빌딩 지하 누수탐지","벽 철거 없이 누수 지점을 특정해 복구비 절감.","case2.svg","case2-after.svg","광주 서구 빌딩 누수 전","광주 서구 빌딩 누수 보수 후"),
  "광주 전역 24시간 출동."),
 ("daejeon","대전광역시",
  "둔산·유성 등 업무·연구단지와 원도심 상권이 어우러진 대전은 연구시설·사무빌딩의 배관과 식당가 배관 관리 수요가 함께 있습니다. 도심·유성 권역에 작업팀을 배치합니다.",
  "둔산 오피스빌딩의 노후관 교체와 유성 상권 주방 배관 고압세척을 주로 진행합니다. 정기 관리 계약으로 우선 출동·요금 할인을 제공합니다.",
  ["동구","중구","서구","유성구","대덕구"],
  _case("서구 · 오피스","둔산 오피스 노후관 교체","부식 메인 배관을 야간 무중단으로 교체.","case3.svg","case3-after.svg","대전 서구 오피스 배관 노후 전","대전 서구 오피스 배관 교체 후"),
  "대전 도심·유성 권역 24시간 출동."),
 ("ulsan","울산광역시",
  "산업수도 울산은 대규모 공장·플랜트 설비 배관과 상권 식당 배관이 공존합니다. 산업단지 대형 배관에 맞는 장비와 인력으로 대응합니다.",
  "공장·플랜트 오수관 고압세척과 CCTV 진단, 상가 식당의 하수구막힘을 함께 처리합니다. 대형 관로 작업 경험을 갖춘 팀이 출동합니다.",
  ["중구","남구","동구","북구","울주군"],
  _case("남구 · 산업시설","산업단지 오수관 고압세척","대형 관로 슬러지를 제거해 배수 정상화.","case1.svg","case1-after.svg","울산 남구 산업시설 오수관 전","울산 남구 산업시설 오수관 세척 후"),
  "울산 산업단지·도심 24시간 출동."),
 ("sejong","세종특별자치시",
  "행정중심복합도시로 빠르게 성장한 세종은 신축 상가·오피스가 밀집해 신규 배관과 초기 하자 점검 수요가 많습니다. 신도심 전역으로 신속 출동합니다.",
  "신축 상가의 배관 마감·하자 점검과 식당 주방 배관 막힘을 주로 대응합니다. CCTV 진단으로 시공 상태를 영상으로 확인해 드립니다.",
  ["한솔동","도담동","아름동","종촌동","새롬동","보람동","조치원읍"],
  _case("신도심 · 상가","세종 상가 배관 CCTV 점검","신축 배관 상태를 영상으로 확인 후 보수.","case2.svg","case2-after.svg","세종 상가 배관 점검 전","세종 상가 배관 보수 후"),
  "세종 신도심 전역 24시간 출동."),
 ("gangwon","강원특별자치도",
  "관광·숙박 시설이 많은 강원은 성수기 호텔·콘도·펜션의 배관 긴급 대응과 겨울철 동파 복구 수요가 특히 높습니다. 영동·영서 권역에 작업팀을 운영합니다.",
  "성수기 숙박시설 객실 배수 긴급 대응과 겨울철 동파 해빙·복구를 집중적으로 진행합니다. 한랭지 배관 보온·보수 경험을 갖춘 팀이 출동합니다.",
  ["춘천시","원주시","강릉시","속초시","동해시","삼척시","평창군","홍천군"],
  _case("강릉 · 숙박","강릉 펜션 객실 동파 복구","겨울철 동파관을 해빙·보수해 영업 재개.","case3.svg","case3-after.svg","강원 강릉 펜션 동파 전","강원 강릉 펜션 동파 복구 후"),
  "강원 영동·영서 권역 24시간 출동, 동파 전문."),
 ("chungbuk","충청북도",
  "청주를 중심으로 산업단지와 물류시설이 발달한 충북은 공장 오수관 관리와 상권 식당 배관 수요가 함께 있습니다. 청주·충주 권역에 작업팀을 배치합니다.",
  "청주 산업단지의 대형 오수관 고압세척과 상가 식당의 하수구막힘을 주로 처리합니다. 정기 관리로 막힘 빈도를 크게 줄입니다.",
  ["청주시","충주시","제천시","음성군","진천군","옥천군","영동군"],
  _case("청주 · 식당","청주 식당가 주방 배관 세척","기름때 누적 배관을 고압세척으로 회복.","case1.svg","case1-after.svg","충북 청주 식당 배관 전","충북 청주 식당 배관 세척 후"),
  "충북 청주·충주 권역 24시간 출동."),
 ("chungnam","충청남도",
  "천안·아산 산업벨트와 서해안 관광지를 아우르는 충남은 공장·물류 배관과 숙박시설 배관 수요가 함께 있습니다. 내륙·서해안 권역에 작업팀을 운영합니다.",
  "천안·아산 물류시설의 대형 배관 고압세척과 서해안 숙박시설의 객실 배수 긴급 대응을 함께 진행합니다. CCTV 진단으로 근본 원인을 찾습니다.",
  ["천안시","아산시","서산시","당진시","공주시","논산시","보령시","예산군"],
  _case("천안 · 물류","천안 물류센터 오수관 세척","대형 관로 슬러지 제거로 배수 정상화.","case1.svg","case1-after.svg","충남 천안 물류센터 오수관 전","충남 천안 물류센터 오수관 세척 후"),
  "충남 내륙·서해안 권역 24시간 출동."),
 ("jeonbuk","전북특별자치도",
  "전주 한옥마을 상권과 군산·익산 산업지역을 갖춘 전북은 관광 식당가 배관과 공장 배관 수요가 함께 있습니다. 전주·군산 권역에 작업팀을 배치합니다.",
  "전주 상권 식당의 기름때 하수구막힘과 군산·익산 공장의 오수관 관리를 주로 대응합니다. 선견적 후작업으로 신뢰를 드립니다.",
  ["전주시","군산시","익산시","정읍시","남원시","김제시","완주군"],
  _case("전주 · 식당가","전주 식당가 배관 고압세척","관광 성수기 전 배관을 미리 세척해 막힘 예방.","case1.svg","case1-after.svg","전북 전주 식당가 배관 전","전북 전주 식당가 배관 세척 후"),
  "전북 전주·군산 권역 24시간 출동."),
 ("jeonnam","전라남도",
  "여수·순천·목포 등 관광·항만 도시가 많은 전남은 숙박·식당 시설의 배관과 항만 시설 배관 수요가 함께 있습니다. 동부·서부 권역에 작업팀을 운영합니다.",
  "여수·순천 숙박시설의 객실 배수 긴급 대응과 목포 상권 식당의 배관 막힘을 함께 처리합니다. 해안 노후 배관의 부식·누수도 점검합니다.",
  ["목포시","여수시","순천시","나주시","광양시","무안군","해남군","고흥군"],
  _case("여수 · 숙박","여수 호텔 객실 배수 긴급 대응","성수기 야간 막힘을 신속 출동으로 해결.","case3.svg","case3-after.svg","전남 여수 호텔 배수 전","전남 여수 호텔 배수 복구 후"),
  "전남 동부·서부 권역 24시간 출동."),
 ("gyeongbuk","경상북도",
  "포항·구미 산업도시와 경주 관광지를 아우르는 경북은 공장 대형 배관과 숙박시설 배관 수요가 함께 있습니다. 포항·구미·경주 권역에 작업팀을 배치합니다.",
  "포항·구미 산업단지의 오수관 고압세척·CCTV 진단과 경주 숙박시설의 배관 관리를 함께 진행합니다. 대형 관로 작업 경험을 갖춘 팀이 출동합니다.",
  ["포항시","구미시","경주시","경산시","안동시","김천시","영주시","칠곡군"],
  _case("구미 · 산업시설","구미 산단 오수관 CCTV 진단","관 내부 파손을 영상으로 확인 후 보수.","case2.svg","case2-after.svg","경북 구미 산단 오수관 진단 전","경북 구미 산단 오수관 보수 후"),
  "경북 포항·구미·경주 권역 24시간 출동."),
 ("gyeongnam","경상남도",
  "창원·김해 산업벨트와 통영·거제 해안 관광지를 갖춘 경남은 공장 배관과 숙박·식당 배관 수요가 함께 있습니다. 동부·서부 권역에 작업팀을 운영합니다.",
  "창원·김해 공장의 대형 오수관 관리와 통영·거제 숙박시설의 객실 배수 대응을 함께 진행합니다. 해안 노후 배관의 부식·누수도 정밀 탐지합니다.",
  ["창원시","김해시","진주시","양산시","거제시","통영시","사천시","밀양시"],
  _case("창원 · 공장","창원 공장 오수관 고압세척","대형 관로 슬러지 제거로 배수 회복.","case1.svg","case1-after.svg","경남 창원 공장 오수관 전","경남 창원 공장 오수관 세척 후"),
  "경남 동부·서부 권역 24시간 출동."),
 ("jeju","제주특별자치도",
  "관광·숙박 산업이 중심인 제주는 호텔·리조트·게스트하우스의 배관 긴급 대응 수요가 특히 높습니다. 제주시·서귀포 권역에 작업팀을 운영합니다.",
  "성수기 숙박시설의 객실 배수 긴급 대응과 식당가 주방 배관 고압세척을 집중적으로 진행합니다. 화산암 지반 특성을 고려한 배관 점검도 함께합니다.",
  ["제주시","서귀포시","애월읍","조천읍","한림읍","성산읍","대정읍","남원읍"],
  _case("제주시 · 숙박","제주 리조트 객실 배수 대응","성수기 야간 막힘을 신속 출동으로 해결.","case3.svg","case3-after.svg","제주시 리조트 배수 전","제주시 리조트 배수 복구 후"),
  "제주시·서귀포 권역 24시간 출동."),
]
for slug, name, short, intro, districts, case, note in SIDO_MORE:
    sido_page(slug, name, short, intro, districts, GUNGU_LINKS.get(slug, {}), case, note)

print("\\nEXTRA SIDO PAGES BUILT.")


# ===========================================================================
# 시·군·구 상세 페이지 생성기 (각 구/시 고유 콘텐츠)
# ===========================================================================
def gungu_page(sido_slug, sido_name, sido_url, slug, gu_name, lead, paras, jobs, dong, case_html, note):
    crumbs = [("홈","/"),("지역별 서비스","/area/"),(sido_name, sido_url),(gu_name, None)]
    para_html = "".join(f"<p>{p}</p>" for p in paras)
    jobs_html = "".join(f"<li>{j}</li>" for j in jobs)
    tags = "".join(f"<span>{d}</span>" for d in dong)
    body = f"""{phero(f"{gu_name} 서비스", f"{gu_name} 배관·하수구막힘 24시간 출동", lead, crumbs)}
<main>
<section class="section">
  <div class="container layout-sidebar">
    <div class="prose">
      <h2>{gu_name} 상업시설 배관 전문</h2>
      {para_html}

      <h2>{gu_name}에서 자주 의뢰되는 작업</h2>
      <ul class="ticks">{jobs_html}</ul>

      <h2>{gu_name} 시공 사례</h2>
      {case_html}

      <h2>{gu_name} 서비스 가능 지역</h2>
      <p>아래 동네를 포함한 {gu_name} 전역으로 출동합니다. (동 단위 별도 페이지는 운영하지 않습니다.)</p>
      <div class="tag-list">{tags}</div>
    </div>
    <aside class="sidebar-card">
      <h3>{gu_name} 상담</h3>
      <p>{note}</p>
      <a class="phone-big" href="tel:0000-0000">0000-0000</a>
      <p style="margin-bottom:18px;">카카오톡 상담 @스피드배관</p>
      <a class="btn btn--primary btn--block" href="tel:0000-0000">☎ 전화 상담</a>
      <a class="btn btn--ghost-light btn--block" href="https://t.me/googleseolab" target="_blank" rel="noopener" style="margin-top:10px;">광고문의 상담</a>
    </aside>
  </div>
</section>
{bottom_cta(h2=f"{gu_name} 어디든, 지금 출동합니다")}
</main>
"""
    title = f"{gu_name} 배관·하수구막힘·누수탐지 24시간 출동 - 스피드 배관공사"
    desc = f"{gu_name} 하수구막힘·배관공사·누수탐지·고압세척 24시간 출동. 선견적 후작업, 추가금 없음."
    page(f"area/{sido_slug}/{slug}.html", title, desc, f"{S}/area/{sido_slug}/{slug}.html",
         body, jsonld=breadcrumb_jsonld(crumbs))


# (서초구·송파구는 파일 하단에서 강남과 동일한 구+행정동 종합 체계로 생성)
# (성남·수원·해운대·연수는 전국 자동 시군구+행정동 체계로 통합 생성)

print("\\nGUNGU DETAIL PAGES BUILT.")


# ===========================================================================
# 서울 강남구 종합 페이지 (/area/seoul/gangnam-gu/) + 14개 행정동 하위 페이지
# ===========================================================================
import re as _re
def _chars(html):
    """본문 시각 텍스트 글자 수(공백 제외) 근사 — 분량 확인용"""
    t = _re.sub(r"<[^>]+>", "", html)
    t = _re.sub(r"\s+", "", t)
    return len(t)

GN_DONG = [
    ("역삼동","yeoksam",
     "역삼동은 테헤란로와 강남대로가 교차하는 강남의 대표 업무지구로, 대형 오피스빌딩과 오피스텔, 그리고 직장인을 상대하는 식당·카페가 빼곡하게 들어선 지역입니다. 주거용 오피스텔과 다세대가 함께 섞여 있어 가정용 배관과 상업용 배관 상담이 동시에 들어옵니다.",
     "역삼역·강남역 주변은 점심·저녁 시간대 유동 인구가 많아 식당 주방 배관에 기름때가 빠르게 쌓이고, 오피스텔은 세대가 밀집된 만큼 공용 배수관에 부담이 큰 편입니다. 영업장은 무중단 작업이, 오피스텔은 공용관 영향 확인이 중요합니다.",
     "역삼동에서는 싱크대 배수 불량과 오피스텔 화장실 배수 지연, 식당 주방 바닥 배수구 역류 상담이 특히 잦습니다. 반복 막힘이라면 단순 스프링 작업보다 배관내시경으로 내부 상태를 먼저 확인하는 구성이 안전합니다.",
     [("논현동","nonhyeon"),("삼성동","samseong"),("대치동","daechi")]),
    ("논현동","nonhyeon",
     "논현동은 가구거리와 먹자골목, 그리고 영동시장 인근 상권이 어우러진 지역으로, 음식점과 술집, 카페가 밀집해 있습니다. 주거지로는 단독·다세대 주택과 빌라가 많아 노후 배관 상담도 함께 들어오는 편입니다.",
     "음식점이 많은 만큼 주방에서 흘러나오는 기름 슬러지가 배관 내부에 퇴적되어 막힘을 일으키는 경우가 자주 있습니다. 가정집은 머리카락·음식물 찌꺼기가, 영업장은 기름때가 주요 원인이 되는 식으로 현장마다 원인이 다릅니다.",
     "논현동에서는 음식점 주방 하수구막힘과 빌라 화장실 악취, 싱크대 역류 상담이 많습니다. 영업장의 반복 막힘은 고압세척으로 배관 내부를 세척해야 재발을 줄일 수 있어, 배관내시경 확인 후 작업 방향을 정하는 것이 좋습니다.",
     [("신사동","sinsa"),("역삼동","yeoksam"),("반포(서초)","seocho")]),
    ("신사동","sinsa",
     "신사동은 가로수길을 중심으로 한 패션·뷰티 상권과 카페·디저트 매장이 밀집한 지역입니다. 1층 상가와 지하 매장이 많아 배수 구조가 복잡한 편이며, 주거지로는 다세대와 빌라가 함께 자리합니다.",
     "지하 매장이 많은 가로수길 특성상 바닥 배수구 역류와 배수 지연 상담이 잦고, 카페·음료 매장은 우유·시럽·커피 찌꺼기가 배관에 엉겨 막힘을 만드는 경우가 있습니다. 매장 영업 시간을 고려한 작업 일정 조율이 중요합니다.",
     "신사동에서는 카페·음식점 싱크대막힘과 지하 상가 바닥 배수구 역류, 화장실 배수 불량 상담이 많습니다. 매장 배관은 가정집보다 원인이 복잡할 수 있어 작업 전 사진·영상 상담으로 상태를 먼저 확인하는 것을 권합니다.",
     [("논현동","nonhyeon"),("압구정동","apgujeong"),("청담동","cheongdam")]),
    ("압구정동","apgujeong",
     "압구정동은 로데오거리 상권과 고급 아파트 단지, 그리고 미용·성형·병의원이 밀집한 지역입니다. 준공 연차가 오래된 아파트가 많아 노후 배관에서 비롯된 상담이 꾸준히 들어옵니다.",
     "오래된 아파트는 배관 구배가 좋지 않거나 내부에 스케일이 쌓여 배수가 느려지는 경우가 많고, 병의원·미용실은 사용량이 많아 배수구 막힘이 반복되기도 합니다. 단지 공용관과 세대 전용관을 구분해 원인을 판단하는 것이 중요합니다.",
     "압구정동에서는 노후 아파트 욕실 배수 지연과 세면대·싱크대막힘, 상가 화장실 역류 상담이 많습니다. 반복 막힘이나 여러 세대 동시 증상은 공용관 문제일 수 있어 배관내시경 확인 후 대응 범위를 정하는 것이 안전합니다.",
     [("신사동","sinsa"),("청담동","cheongdam"),("삼성동","samseong")]),
    ("청담동","cheongdam",
     "청담동은 명품거리와 갤러리, 고급 레스토랑·바가 모여 있는 지역으로, 저층 상가 건물과 고급 주거가 혼재합니다. 인테리어가 까다로운 매장이 많아 작업 시 현장 보양과 마감 정리가 특히 중요합니다.",
     "고급 레스토랑·바가 많아 주방 기름때와 음식물 슬러지로 인한 배관 막힘이 잦고, 저층 상가 건물은 지하 배수와 오수관에서 악취가 올라오는 상담이 자주 발생합니다. 영업장 이미지가 중요한 만큼 무중단·저소음 작업이 요구됩니다.",
     "청담동에서는 건물 지하 배수 악취와 레스토랑 주방 하수구막힘, 상가 화장실 배수구 역류 상담이 많습니다. 악취·역류가 반복된다면 배관내시경으로 원인 위치를 확인하고 고압세척으로 내부를 세척하는 구성이 효과적입니다.",
     [("압구정동","apgujeong"),("삼성동","samseong"),("신사동","sinsa")]),
    ("삼성동","samseong",
     "삼성동은 코엑스와 무역센터, 대형 오피스빌딩과 호텔이 밀집한 강남 최대의 업무·전시 지역입니다. 대형 시설이 많아 배관 규모가 크고 대량 배수가 발생하는 현장이 많습니다.",
     "대형 상가·전시시설은 화장실과 식당가의 사용량이 많아 바닥 배수구 역류와 오수관 막힘 상담이 잦고, 오피스빌딩은 지하 메인 배관의 누적 퇴적물이 문제가 되곤 합니다. 시설 운영에 지장이 없도록 시간대 조율이 필요합니다.",
     "삼성동에서는 상가 화장실 배수구 역류와 대형 오수관 막힘, 오피스빌딩 지하 배관 상담이 많습니다. 사용량이 많은 시설은 정기적인 배관내시경 점검과 고압세척으로 막힘을 예방하는 것이 운영에 유리합니다.",
     [("대치동","daechi"),("역삼동","yeoksam"),("청담동","cheongdam")]),
    ("대치동","daechi",
     "대치동은 학원가와 대단지 아파트가 공존하는 지역으로, 학원 건물과 주거 시설의 배관 상담이 함께 들어옵니다. 학원가 상가는 화장실 사용 빈도가 높아 배수 부담이 큰 편입니다.",
     "대단지 아파트는 준공 연차에 따라 배관 노후도가 달라 욕실 배수가 느려지거나 악취가 올라오는 상담이 잦고, 학원·상가 건물은 화장실 배수구 막힘이 반복되는 경우가 있습니다. 세대 전용관과 공용관을 구분한 진단이 중요합니다.",
     "대치동에서는 아파트 욕실 배수 느림과 세면대·싱크대막힘, 학원 상가 화장실 배수구 막힘 상담이 많습니다. 반복 증상은 내부 퇴적물이 원인일 수 있어 배관내시경 확인 후 고압세척 여부를 판단하는 것이 좋습니다.",
     [("도곡동","dogok"),("삼성동","samseong"),("역삼동","yeoksam")]),
    ("도곡동","dogok",
     "도곡동은 타워팰리스로 대표되는 고층 주상복합과 대단지 아파트가 밀집한 주거 중심 지역입니다. 고층 건물이 많아 배관 계통이 길고 층간 배수 구조가 복잡한 편입니다.",
     "고층 주상복합은 공용 입상관과 세대 배관이 길게 연결되어 있어, 한 세대의 막힘이 다른 세대에 영향을 주거나 저층에서 역류가 나타나는 경우가 있습니다. 증상이 여러 층에 걸쳐 나타나면 공용관 점검이 우선입니다.",
     "도곡동에서는 고층 아파트 욕실·주방 배수 지연과 저층 세대 역류, 세면대막힘 상담이 많습니다. 고층 건물의 반복 막힘은 배관내시경으로 입상관 상태를 확인한 뒤 작업 범위를 정하는 것이 안전합니다.",
     [("대치동","daechi"),("개포동","gaepo"),("역삼동","yeoksam")]),
    ("개포동","gaepo",
     "개포동은 재건축으로 신축 아파트 단지가 빠르게 들어선 지역으로, 신축과 기존 주거가 혼재합니다. 신축 단지는 입주 초기 배관 점검 수요가, 기존 주거는 노후 배관 상담이 함께 들어옵니다.",
     "신축 아파트는 시공 마감 상태나 초기 이물질로 인한 배수 지연이 나타날 수 있고, 기존 빌라·단독은 배관 구배 불량이나 노후로 인한 막힘이 잦습니다. 신축은 점검 위주, 노후는 원인 제거 위주로 접근이 달라집니다.",
     "개포동에서는 신축 아파트 배수 점검과 기존 주택 욕실·싱크대막힘, 바닥 배수구 역류 상담이 많습니다. 입주 초기 반복 막힘은 배관내시경으로 시공 상태를 확인해 두면 이후 관리가 수월합니다.",
     [("도곡동","dogok"),("일원동","ilwon"),("대치동","daechi")]),
    ("일원동","ilwon",
     "일원동은 삼성서울병원과 대단지 아파트가 인접한 주거 중심 지역으로, 조용한 주거 환경 속에 생활 배관 상담이 주로 들어옵니다. 병원·상가 인근은 사용량이 많아 배수 부담이 있는 편입니다.",
     "대단지 아파트는 준공 연차에 따라 욕실·주방 배수 지연이 나타나며, 병원·상가 인근 건물은 화장실 사용 빈도가 높아 배수구 막힘이 반복되기도 합니다. 생활 배관은 머리카락·음식물·비누 찌꺼기가 주요 원인입니다.",
     "일원동에서는 아파트 욕실 배수 느림과 싱크대·세면대막힘, 상가 화장실 배수구 막힘 상담이 많습니다. 단순 막힘은 빠르게 해결되지만, 반복된다면 배관 내부 상태 확인 후 세척 여부를 판단하는 것이 좋습니다.",
     [("개포동","gaepo"),("수서동","suseo"),("대치동","daechi")]),
    ("수서동","suseo",
     "수서동은 SRT 수서역과 업무·물류 시설, 그리고 아파트 단지가 어우러진 지역입니다. 역세권 상가와 오피스, 주거가 함께 있어 상업용·가정용 배관 상담이 고루 들어옵니다.",
     "역세권 상가와 식당은 유동 인구가 많아 주방·화장실 배수 부담이 크고, 업무 시설은 지하 배관의 퇴적물이 문제가 되곤 합니다. 주거 단지는 생활 배관 막힘이 주를 이루어 현장별로 접근이 달라집니다.",
     "수서동에서는 상가·오피스 배수구 막힘과 식당 주방 하수구막힘, 아파트 욕실 배수 지연 상담이 많습니다. 사용량이 많은 영업장은 정기 고압세척으로 막힘을 예방하면 운영에 도움이 됩니다.",
     [("일원동","ilwon"),("세곡동","segok"),("대치동","daechi")]),
    ("세곡동","segok",
     "세곡동은 보금자리지구 개발로 신축 아파트와 상가가 들어선 지역으로, 비교적 새 건물이 많은 주거 중심 지역입니다. 신축 단지의 초기 배관 점검 수요가 꾸준히 들어옵니다.",
     "신축 아파트·상가는 시공 마감이나 입주 초기 이물질로 인한 배수 지연이 나타날 수 있고, 상가는 업종에 따라 주방·화장실 배수 부담이 다릅니다. 새 건물이라도 구배 불량이나 시공 문제로 막힘이 생길 수 있어 점검이 유효합니다.",
     "세곡동에서는 신축 아파트 배수 점검과 상가 싱크대·화장실 배수구 막힘, 바닥 배수 지연 상담이 많습니다. 입주 초기 반복 증상은 배관내시경으로 내부 상태를 확인해 원인을 명확히 하는 것이 좋습니다.",
     [("수서동","suseo"),("자곡동","jagok"),("율현동","yulhyeon")]),
    ("자곡동","jagok",
     "자곡동은 강남보금자리지구에 속한 신축 아파트 중심의 주거 지역으로, 단지와 근린 상가가 함께 조성되어 있습니다. 생활 배관과 근린 상가 배관 상담이 주로 들어옵니다.",
     "신축 단지는 입주 초기 배수 지연이나 이물질 막힘이 나타날 수 있고, 근린 상가는 식당·카페 업종에서 주방 배관 막힘이 발생하기도 합니다. 주거 배관은 생활 이물질이, 상가는 업종별 특성이 원인이 됩니다.",
     "자곡동에서는 아파트 욕실·싱크대막힘과 근린 상가 주방 하수구막힘, 배수구 역류 상담이 많습니다. 반복 막힘은 단순 이물질 외에 배관 내부 문제일 수 있어 내시경 확인 후 작업 방향을 정하는 것을 권합니다.",
     [("세곡동","segok"),("율현동","yulhyeon"),("수서동","suseo")]),
    ("율현동","yulhyeon",
     "율현동은 세곡지구 일대의 신축 아파트와 단독·다세대가 혼재한 주거 지역으로, 비교적 한적한 환경 속에 생활 배관 상담이 주를 이룹니다. 근린 상가의 배관 상담도 함께 들어옵니다.",
     "신축 아파트는 초기 점검 위주, 단독·다세대는 노후나 구배 문제로 인한 막힘 위주로 상담이 나뉩니다. 단독주택은 외부 오수관과 정화조 연결부에서 문제가 생기는 경우도 있어 현장 확인이 중요합니다.",
     "율현동에서는 아파트·주택 욕실 배수 지연과 싱크대막힘, 단독주택 오수관 막힘 상담이 많습니다. 외부 배관이나 정화조 관련 증상은 현장 구조를 먼저 확인한 뒤 작업 방식을 안내드립니다.",
     [("자곡동","jagok"),("세곡동","segok"),("수서동","suseo")]),
]
GN_DONG_BY_SLUG = {slug: ko for ko, slug, *_ in GN_DONG}

# 공통 리스트 조각
SYMPTOM_LI = ("<li>물이 평소보다 천천히 빠지는 경우</li>"
              "<li>배수구에서 냄새가 올라오는 경우</li>"
              "<li>싱크대 물이 역류하는 경우</li>"
              "<li>욕실 바닥 배수가 늦어지는 경우</li>"
              "<li>변기가 반복적으로 막히는 경우</li>"
              "<li>음식점 주방 배관에 기름때가 쌓인 경우</li>"
              "<li>오래된 건물의 배관 구배가 좋지 않은 경우</li>")
SERVICE_LI = ("<li>하수구막힘</li><li>배관공사</li><li>싱크대막힘</li><li>변기막힘</li>"
              "<li>욕실 배수구막힘</li><li>세면대막힘</li><li>오수관막힘</li><li>배관내시경</li>"
              "<li>고압세척</li><li>음식점 하수구막힘</li><li>상가 배관공사</li><li>아파트·빌라 배관보수</li>")
WORK_LI = ("<li>증상 확인 및 사진·영상 상담</li><li>막힘 위치 추정 및 현장 접근 여부 확인</li>"
           "<li>작업 전 비용 기준 안내</li><li>장비 선택(스프링·관통·고압세척 등)</li>"
           "<li>막힘 제거 또는 배관 세척</li><li>배수 테스트 및 재발 방지 안내</li>")
COST_LI = ("<li>막힘 위치와 배관 길이</li><li>배관 노후도와 구배 상태</li>"
           "<li>사용 장비(스프링·관통기·고압세척기)</li><li>배관내시경 필요 여부</li>"
           "<li>야간·주말 출동 여부</li><li>상가·음식점 등 영업장 여부</li><li>배관 교체 필요 여부</li>")
COST_NOTE = ("정확한 비용은 현장 구조와 막힘 정도를 확인한 뒤 안내됩니다. 단순 막힘인지, 반복 막힘인지, "
             "배관 내부 문제인지에 따라 필요한 장비와 작업 시간이 달라질 수 있습니다.")
FIXTURE_P = ("주방 싱크대는 음식물과 기름이 함께 흘러가며 배관 안쪽에 퇴적물을 만들고, 변기는 이물질이나 노후 구배 문제로 "
             "반복 막힘이 나타납니다. 욕실 바닥 배수구와 세면대는 머리카락·비누때가 주요 원인으로, 배수가 늦어지거나 냄새가 "
             "올라오면 내부에 이물질이 쌓였을 가능성이 큽니다. 같은 막힘이라도 어느 곳이 막혔는지에 따라 필요한 장비와 접근 "
             "방법이 다르기 때문에, 작업 전에 막힌 위치와 증상을 확인하는 과정이 중요합니다.")
INSPECT_P = ("반복 막힘이나 원인을 알 수 없는 역류·악취는 배관내시경으로 내부를 직접 확인하면 원인 위치를 특정할 수 있습니다. "
             "기름때나 퇴적물이 두껍게 쌓였다면 단순 관통만으로는 다시 막히기 쉬워, 고압세척으로 관 벽을 세척해야 배수 흐름이 "
             "제대로 회복됩니다. 단순 막힘인지 내부 퇴적 문제인지에 따라 작업 방향이 달라지므로, 반복되는 증상은 내시경 확인 후 "
             "세척 여부를 판단하는 구성이 안전합니다.")
PREPARE_P = ("상담을 빠르게 진행하려면 막힌 위치(싱크대·변기·욕실·바닥 등), 건물 형태(아파트·빌라·상가·음식점), 물이 내려가는 속도, "
             "냄새나 역류 여부를 함께 알려주시면 좋습니다. 가능하다면 증상 부위를 찍은 사진이나 영상을 보내주시면 필요한 장비를 "
             "더 정확히 판단할 수 있어 현장에서의 작업 시간을 줄일 수 있습니다.")
FAQ_CHEMICAL = ("변기나 배수구가 막혔을 때 약품을 사용해도 되나요?",
                "약품은 일시적으로 도움이 될 수 있지만 배관 손상이나 악취 문제가 생길 수 있습니다. 특히 반복 막힘이나 역류가 "
                "있으면 무리한 자가 조치보다 상담이 안전합니다.")
SELFCARE_P = ("막힘이 생겼을 때 뚫어뻥이나 시중 약품으로 무리하게 조치하면 배관이 손상되거나 악취·역류가 더 심해질 수 있습니다. "
              "특히 반복 막힘이나 여러 곳에서 동시에 증상이 나타나는 경우에는 자가 조치보다 내부 상태를 먼저 확인한 뒤 작업하는 "
              "것이 안전합니다. 사용을 잠시 멈추고 막힌 위치와 증상, 물이 빠지는 속도를 기록해 두면 상담과 작업이 더 빠르게 "
              "진행됩니다.")

# ---------------------------------------------------------------------------
# 문구 변형(스핀) — 지역명 기반으로 같은 의미의 다른 문장을 선택해 페이지 중복도를 낮춤
# ---------------------------------------------------------------------------
import hashlib as _hl
def vpick(seed, options):
    return options[int(_hl.md5(str(seed).encode("utf-8")).hexdigest(), 16) % len(options)]

FIXTURE_V = [FIXTURE_P,
    ("싱크대는 음식물과 기름이 함께 흘러 배관 안쪽에 퇴적물을 쌓고, 변기는 이물질이나 노후 구배 탓에 반복적으로 막히곤 합니다. "
     "욕실 바닥 배수구·세면대는 머리카락과 비누때가 주된 원인이라 배수가 느려지거나 냄새가 올라오면 내부에 이물질이 쌓였을 가능성이 큽니다. "
     "막힌 위치에 따라 필요한 장비와 접근 방법이 달라지므로, 작업 전에 어디가 막혔는지 확인하는 과정이 중요합니다."),
    ("주방 싱크대 배관에는 기름·음식물 찌꺼기가 들러붙어 좁아지고, 변기는 이물질 투입이나 배관 구배 문제로 자주 막힙니다. "
     "세면대와 욕실 바닥 배수구는 머리카락·비누때가 쌓이며 배수가 느려지고 악취가 동반되기 쉽습니다. "
     "같은 막힘이라도 부위마다 원인과 해법이 다르기 때문에, 증상과 위치를 먼저 파악한 뒤 작업 방법을 정하는 것이 좋습니다.")]
INSPECT_V = [INSPECT_P,
    ("원인을 알 수 없는 역류나 악취, 반복되는 막힘은 배관내시경으로 관 내부를 들여다보면 문제 지점을 정확히 찾을 수 있습니다. "
     "기름때·퇴적물이 두껍게 쌓였다면 스프링 관통만으로는 금세 다시 막히므로, 고압세척으로 관 벽을 닦아내야 흐름이 회복됩니다. "
     "단순 막힘인지 내부 퇴적인지에 따라 작업이 달라지니 반복 증상은 내시경 확인 후 세척 여부를 정하는 편이 안전합니다."),
    ("같은 자리가 자꾸 막히거나 냄새·역류가 사라지지 않는다면 배관내시경으로 내부 상태를 확인하는 것이 가장 확실합니다. "
     "기름·스케일이 관 벽에 두껍게 붙은 경우에는 고압세척으로 제거해야 배수가 제대로 돌아옵니다. "
     "내부 상태를 보고 단순 관통으로 끝낼지, 세척까지 할지를 판단하면 불필요한 재작업을 줄일 수 있습니다.")]
SELFCARE_V = [SELFCARE_P,
    ("뚫어뻥이나 시중 약품으로 무리하게 뚫으려다 배관이 상하거나 악취·역류가 더 심해지는 경우가 적지 않습니다. "
     "반복 막힘이거나 여러 곳에서 동시에 증상이 나타난다면 자가 조치보다 내부를 먼저 확인하는 편이 안전합니다. "
     "사용을 잠시 멈추고 막힌 위치·증상·배수 속도를 메모해 두면 상담과 현장 작업이 한결 빨라집니다."),
    ("강한 약품이나 도구로 억지로 뚫으면 배관 손상이나 2차 누수로 이어질 수 있어 주의가 필요합니다. "
     "특히 자주 막히거나 동시에 여러 배수구가 막히는 상황은 배관 내부 문제일 수 있어 상담을 권합니다. "
     "물 사용을 멈추고 어디가 어떻게 막혔는지 사진·메모로 남겨두면 더 정확한 안내가 가능합니다.")]
WORKINTRO_V = [
    "현장도 증상 확인과 사진·영상 상담을 먼저 진행한 뒤, 막힘 위치와 원인을 추정해 필요한 장비를 선택합니다. 작업 전 비용 기준을 안내드리고, 동의 후 막힘 제거 또는 배관 세척을 진행합니다.",
    "먼저 증상과 사진·영상으로 상태를 확인하고 막힘 위치를 가늠한 다음, 현장에 맞는 장비를 정합니다. 비용 기준을 미리 안내하고 동의를 받은 뒤 막힘 제거나 세척 작업을 시작합니다.",
    "증상 청취와 사진·영상 상담으로 원인을 좁힌 뒤 필요한 장비를 준비합니다. 작업 전에 예상 비용 기준을 설명드리고, 확인이 되면 막힘 제거 또는 고압세척을 진행합니다.",
]
SYMPTOM_TAIL_V = [
    "현장마다 건물 형태와 사용 환경이 달라 원인도 제각각입니다. 가정집은 머리카락·음식물·비누 찌꺼기가, 음식점은 기름 슬러지가 주요 원인이 되곤 합니다.",
    "같은 증상이라도 주거지인지 영업장인지에 따라 원인이 다릅니다. 단순 이물질이면 관통으로 해결되지만, 반복된다면 배관 내부 상태를 확인해보는 것이 좋습니다.",
    "건물 연식과 용도에 따라 막힘의 원인이 달라집니다. 일시적 이물질일 수도 있지만, 자주 반복된다면 내부 퇴적이나 구배 문제를 의심해볼 수 있습니다.",
]

def local_sidebar(title, note):
    return f"""<aside class="sidebar-card">
      <h3>{title}</h3>
      <p>{note}</p>
      <a class="phone-big" href="tel:0000-0000">0000-0000</a>
      <p style="margin-bottom:18px;">증상·위치·건물 형태를 알려주시면 더 정확히 안내드립니다.</p>
      <a class="btn btn--primary btn--block" href="tel:0000-0000">☎ 전화 상담하기</a>
      <a class="btn btn--ghost-light btn--block" href="https://t.me/googleseolab" target="_blank" rel="noopener" style="margin-top:10px;">사진 보내기 · 상담</a>
    </aside>"""

def gangnam_faq_jsonld(items):
    return faq_jsonld(items)

# ---- 강남구 종합 페이지 ----
def build_gangnam_gu():
    crumbs = [("홈","/"),("지역별 서비스","/area/"),("서울특별시","/area/seoul/"),("강남구", None)]
    dong_links = "".join(f'<a href="/area/seoul/gangnam-gu/{slug}-dong/">{ko}</a>' for ko, slug, *_ in GN_DONG)
    adj = [("서초구","/area/seoul/seocho-gu/"),("송파구","/area/seoul/songpa-gu/"),
           ("강동구","/area/seoul/"),("성동구","/area/seoul/"),("광진구","/area/seoul/")]
    adj_links = "".join(f'<a href="{u}">{n} 배관공사</a>' for n, u in adj)
    faq = [
        ("강남 하수구막힘은 바로 출동 가능한가요?",
         "지역과 시간대, 현장 상황에 따라 상담 후 안내됩니다. 사진이나 증상을 먼저 보내주시면 필요한 장비를 더 정확히 판단할 수 있습니다."),
        ("싱크대가 자주 막히면 고압세척이 필요한가요?",
         "반복 막힘이라면 단순 이물질보다 배관 내부 기름때나 퇴적물이 원인일 수 있습니다. 이 경우 배관내시경 확인 후 고압세척 여부를 판단하는 것이 좋습니다."),
        ("변기가 막혔을 때 약품을 사용해도 되나요?",
         "약품은 일시적으로 도움이 될 수 있지만 배관 손상이나 악취 문제가 생길 수 있습니다. 특히 반복 막힘이나 역류가 있으면 무리한 자가 조치보다 상담이 안전합니다."),
        ("강남 상가나 음식점도 작업 가능한가요?",
         "상가, 음식점, 카페, 사무실, 병원, 학원 등 현장 구조에 따라 상담 가능합니다. 영업장 배관은 가정집보다 원인이 복잡할 수 있어 작업 전 확인이 중요합니다."),
    ]
    body = f"""{phero("강남 배관공사", "강남 배관공사·하수구막힘 긴급 상담 | 스피드 배관공사", "역삼·논현·삼성·청담·대치 등 강남 전역의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다.", crumbs)}
<main>
<section class="section">
  <div class="container layout-sidebar">
    <div class="prose">
      <nav class="anchor-nav" aria-label="강남 배관공사 바로가기">
        <h2>강남 배관공사 바로가기</h2>
        <ul>
          <li><a href="#intro">강남 배관공사 안내</a></li>
          <li><a href="#symptom">강남 하수구막힘 증상</a></li>
          <li><a href="#fixtures">싱크대·변기·욕실 배수구 문제</a></li>
          <li><a href="#inspection">배관내시경·고압세척 작업</a></li>
          <li><a href="#area">강남구 서비스 가능 지역</a></li>
          <li><a href="#cost">비용이 달라지는 기준</a></li>
          <li><a href="#prepare">현장 확인 전 준비사항</a></li>
          <li><a href="#faq">자주 묻는 질문</a></li>
          <li><a href="#call">전화 상담</a></li>
        </ul>
      </nav>

      <h2 id="intro">강남 배관공사 안내</h2>
      <p>강남구는 아파트, 오피스텔, 상가, 음식점, 병원, 사무실이 함께 밀집된 지역이기 때문에 배관 문제가 단순한 가정용 막힘에서 끝나지 않는 경우가 많습니다. 특히 역삼동, 삼성동, 논현동, 청담동, 대치동 일대는 상가와 주거 시설이 섞여 있어 싱크대 배수 불량, 바닥 배수구 역류, 화장실 악취, 오수관 막힘 상담이 자주 발생합니다.</p>
      <p>스피드 배관공사는 현장의 건물 형태와 막힘 정도를 먼저 확인한 뒤 필요한 작업 방향을 안내합니다. 증상이 단순 막힘인지 반복 막힘인지, 또는 배관 내부 문제인지에 따라 장비와 작업 시간이 달라지기 때문에, 무리한 자가 조치보다 상담을 통해 원인을 정확히 파악하는 것이 안전합니다.</p>

      <h2 id="symptom">강남 하수구막힘 주요 증상</h2>
      <ul class="ticks">{SYMPTOM_LI}</ul>
      <p>강남구는 오래된 빌라와 신축 오피스텔, 대형 상가가 함께 있기 때문에 현장마다 원인이 다릅니다. 가정집은 머리카락·비누 찌꺼기·음식물 찌꺼기가 원인이 되는 경우가 많고, 음식점이나 카페는 기름 슬러지와 배관 내부 퇴적물이 막힘의 주요 원인이 될 수 있습니다. 단순 스프링 작업으로 해결되는 경우도 있지만, 반복 막힘이 있으면 배관내시경으로 내부 상태를 확인하는 구성이 좋습니다.</p>

      <h2 id="fixtures">싱크대·변기·욕실 배수구 문제</h2>
      <p>주방 싱크대는 음식물과 기름이 함께 흘러가며 배관 안쪽에 퇴적물을 만들고, 변기는 이물질이나 노후 배관 구배 문제로 반복 막힘이 나타납니다. 욕실 바닥 배수구와 세면대는 머리카락·비누때가 주요 원인이며, 배수가 늦어지거나 냄새가 올라오면 내부에 이물질이 쌓였을 가능성이 큽니다. 증상별로 필요한 장비가 다르므로 작업 전 상태 확인이 중요합니다.</p>
      <h3>서비스 가능 항목</h3>
      <ul class="ticks">{SERVICE_LI}</ul>

      <h2 id="inspection">배관내시경·고압세척 작업</h2>
      <p>반복 막힘이나 원인을 알 수 없는 역류·악취는 배관내시경으로 내부를 직접 확인하면 원인 위치를 특정할 수 있습니다. 기름때나 퇴적물이 두껍게 쌓인 경우에는 고압세척으로 관 벽을 세척해야 배수 흐름이 제대로 회복됩니다. 작업은 아래 순서로 진행됩니다.</p>
      <ol style="padding-left:20px;display:flex;flex-direction:column;gap:8px;">{WORK_LI}</ol>

      <h2 id="area">강남구 서비스 가능 지역</h2>
      <p>강남구 페이지에서는 1동·2동을 무리하게 나누지 않고 대표 동명으로 통합해 안내합니다. 아래 지역을 선택하면 해당 동의 배관공사·하수구막힘 안내를 확인할 수 있습니다.</p>
      <div class="tag-list">{dong_links}</div>
      <h3>인접 지역</h3>
      <div class="adjacent-links">{adj_links}</div>

      <h2 id="cost">비용이 달라지는 기준</h2>
      <p>강남 배관공사 비용은 현장 조건에 따라 달라집니다. 아래 항목에 따라 필요한 장비와 작업 시간이 달라질 수 있습니다.</p>
      <ul class="ticks">{COST_LI}</ul>
      <p class="price-note">{COST_NOTE}</p>

      <h2 id="prepare">현장 확인 전 준비사항</h2>
      <p>상담을 빠르게 진행하려면 막힘 증상, 막힌 위치(싱크대·변기·욕실·바닥 등), 건물 형태(아파트·빌라·상가·음식점), 물이 내려가는 속도, 냄새나 역류 여부를 함께 알려주시면 좋습니다. 가능하다면 증상 부위를 찍은 사진이나 영상을 보내주시면 필요한 장비를 더 정확히 판단할 수 있습니다.</p>

      <h2 id="cases">강남 현장 상담 유형</h2>
      <p>아래는 강남구에서 자주 들어오는 상담 유형입니다. (실제 시공 사진과 작업 기록은 현장 진행 후 사례로 추가됩니다.)</p>
      <ul class="ticks">
        <li>역삼동 오피스텔 싱크대 배수 불량 상담</li>
        <li>논현동 음식점 주방 하수구막힘 상담</li>
        <li>삼성동 상가 화장실 배수구 역류 상담</li>
        <li>대치동 아파트 욕실 배수 느림 상담</li>
        <li>청담동 건물 지하 배수 악취 상담</li>
      </ul>

      <h2 id="faq">자주 묻는 질문</h2>
      <div class="faq-list">
{faq_html(faq)}      </div>

      <h2 id="call">강남 전화 상담</h2>
      <p>강남구 하수구막힘이나 배관공사 상담이 필요하다면 증상, 위치, 건물 형태, 물이 내려가는 속도, 냄새 여부를 알려주세요. 스피드 배관공사는 현장 조건을 먼저 확인하고 필요한 작업 방향을 안내합니다.</p>
      <div class="local-cta">
        <a class="btn btn--primary btn--lg" href="tel:0000-0000">☎ 전화 상담하기</a>
        <a class="btn btn--secondary btn--lg" href="https://t.me/googleseolab" target="_blank" rel="noopener">사진 보내기</a>
        <a class="btn btn--secondary btn--lg" href="#cost">비용 기준 보기</a>
        <a class="btn btn--secondary btn--lg" href="/cases.html">강남 현장사례 보기</a>
      </div>
    </div>
    {local_sidebar("강남 배관 상담", "강남 전역 상담 가능. 증상·사진을 보내주시면 더 정확합니다.")}
  </div>
</section>
</main>
"""
    print("  [강남구] 본문 글자수 ~", _chars(body.split('</aside>')[0]))
    page("area/seoul/gangnam-gu/index.html",
         "강남 배관공사·하수구막힘 | 싱크대·변기·배수구 막힘 상담 - 스피드 배관공사",
         "강남구 하수구막힘·배관공사·누수탐지·고압세척 24시간 출동. 싱크대·변기·욕실 막힘 상담.",
         S + "/area/seoul/gangnam-gu/", body,
         jsonld=breadcrumb_jsonld(crumbs) + gangnam_faq_jsonld(faq))
build_gangnam_gu()

# ---- 강남구 행정동 하위 페이지 ----
def build_gangnam_dong(ko, slug, intro1, intro2, problem, adjacency):
    crumbs = [("홈","/"),("지역별 서비스","/area/"),("서울특별시","/area/seoul/"),
              ("강남구","/area/seoul/gangnam-gu/"),(ko, None)]
    adj_links = '<a href="/area/seoul/gangnam-gu/">강남구 배관공사</a>' + "".join(
        f'<a href="/area/seoul/gangnam-gu/{s}-dong/">{n}</a>' if s in GN_DONG_BY_SLUG
        else f'<a href="/area/seoul/seocho-gu/">{n} 배관공사</a>'
        for n, s in adjacency)
    faq = [
        (f"{ko} 하수구막힘은 바로 출동 가능한가요?",
         "지역과 시간대, 현장 상황에 따라 상담 후 안내됩니다. 증상과 사진을 먼저 보내주시면 필요한 장비를 더 정확히 판단할 수 있습니다."),
        (f"{ko}에서 싱크대가 자주 막히면 어떻게 하나요?",
         "반복 막힘은 단순 이물질보다 배관 내부 기름때·퇴적물이 원인일 수 있습니다. 배관내시경으로 내부를 확인한 뒤 고압세척 여부를 판단하는 것이 좋습니다."),
        (f"{ko} 상가·음식점도 작업 가능한가요?",
         "상가, 음식점, 카페, 사무실 등 현장 구조에 따라 상담 가능합니다. 영업장 배관은 가정집보다 원인이 복잡할 수 있어 작업 전 확인이 중요합니다."),
        FAQ_CHEMICAL,
    ]
    body = f"""{phero(f"{ko} 배관공사", f"{ko} 배관공사·하수구막힘 상담 | 스피드 배관공사", f"강남구 {ko}의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다.", crumbs)}
<main>
<section class="section">
  <div class="container layout-sidebar">
    <div class="prose">
      <nav class="anchor-nav" aria-label="{ko} 배관공사 바로가기">
        <h2>{ko} 배관공사 바로가기</h2>
        <ul>
          <li><a href="#intro">{ko} 배관공사 안내</a></li>
          <li><a href="#symptom">하수구막힘 증상</a></li>
          <li><a href="#fixtures">싱크대·변기·욕실</a></li>
          <li><a href="#services">서비스 가능 항목</a></li>
          <li><a href="#work">작업 방식</a></li>
          <li><a href="#inspection">배관내시경·고압세척</a></li>
          <li><a href="#cost">비용 기준</a></li>
          <li><a href="#area">인접 지역</a></li>
          <li><a href="#faq">자주 묻는 질문</a></li>
          <li><a href="#call">전화 상담</a></li>
        </ul>
      </nav>

      <h2 id="intro">{ko} 배관공사 안내</h2>
      <p>{intro1}</p>
      <p>{intro2}</p>

      <h2 id="symptom">{ko} 하수구막힘 증상</h2>
      <ul class="ticks">{SYMPTOM_LI}</ul>
      <p>{problem}</p>

      <h2 id="fixtures">{ko} 싱크대·변기·욕실 배수구 문제</h2>
      <p>{FIXTURE_P}</p>

      <h2 id="services">{ko} 서비스 가능 항목</h2>
      <ul class="ticks">{SERVICE_LI}</ul>

      <h2 id="work">{ko} 작업 방식 안내</h2>
      <p>{ko} 현장도 증상 확인과 사진·영상 상담을 먼저 진행한 뒤, 막힘 위치와 원인을 추정해 필요한 장비를 선택합니다. 작업 전 비용 기준을 안내드리고, 동의 후 막힘 제거 또는 배관 세척을 진행합니다.</p>
      <ol style="padding-left:20px;display:flex;flex-direction:column;gap:8px;">{WORK_LI}</ol>

      <h2 id="inspection">{ko} 배관내시경·고압세척</h2>
      <p>{INSPECT_P}</p>

      <h2 id="prepare">현장 확인 전 준비사항</h2>
      <p>{PREPARE_P}</p>

      <h2 id="cost">비용이 달라지는 기준</h2>
      <p>{ko} 배관공사 비용은 현장 조건에 따라 달라집니다. 아래 항목에 따라 필요한 장비와 작업 시간이 달라질 수 있습니다.</p>
      <ul class="ticks">{COST_LI}</ul>
      <p class="price-note">{COST_NOTE}</p>

      <h2 id="area">인접 지역</h2>
      <p>{ko}과 함께 인근 지역도 상담 가능합니다.</p>
      <div class="adjacent-links">{adj_links}</div>

      <h2 id="faq">자주 묻는 질문</h2>
      <div class="faq-list">
{faq_html(faq)}      </div>

      <h2 id="call">{ko} 전화 상담</h2>
      <p>{ko}에서 하수구막힘이나 배관공사 상담이 필요하다면 증상, 위치, 건물 형태, 물이 내려가는 속도, 냄새 여부를 알려주세요. 현장 조건을 먼저 확인하고 필요한 작업 방향을 안내합니다.</p>
      <div class="local-cta">
        <a class="btn btn--primary btn--lg" href="tel:0000-0000">☎ 전화 상담하기</a>
        <a class="btn btn--secondary btn--lg" href="https://t.me/googleseolab" target="_blank" rel="noopener">사진 보내기</a>
        <a class="btn btn--secondary btn--lg" href="/area/seoul/gangnam-gu/">강남구 전체 보기</a>
      </div>
    </div>
    {local_sidebar(f"{ko} 배관 상담", f"{ko} 및 인근 지역 상담 가능. 증상·사진을 보내주시면 더 정확합니다.")}
  </div>
</section>
</main>
"""
    print(f"  [{ko}] 본문 글자수 ~", _chars(body.split('</aside>')[0]))
    page(f"area/seoul/gangnam-gu/{slug}-dong/index.html",
         f"{ko} 배관공사·하수구막힘 | 싱크대·변기·배수구 막힘 상담 - 스피드 배관공사",
         f"강남구 {ko} 하수구막힘·배관공사·누수탐지·고압세척 24시간 출동. 싱크대·변기·욕실 막힘 상담.",
         f"{S}/area/seoul/gangnam-gu/{slug}-dong/", body,
         jsonld=breadcrumb_jsonld(crumbs) + faq_jsonld(faq))

print("\\n강남구 + 행정동 글자수 확인:")
for ko, slug, i1, i2, prob, adj in GN_DONG:
    build_gangnam_dong(ko, slug, i1, i2, prob, adj)
print("\\nGANGNAM-GU SYSTEM BUILT.")


# ===========================================================================
# 범용 구(區) 종합 + 행정동 하위 페이지 생성기  (강남 패턴을 일반화)
# ===========================================================================
def build_gu_system(sido_ko, sido_slug, sido_url, gu_ko, gu_slug, lead, intro_paras,
                    services_line, dongs, adj_gu):
    """gu_ko: '서초구', gu_slug: 'seocho', dongs: [(ko,slug,intro1,intro2,problem,[(adjko,adjslug)]) ...]"""
    gu_url = f"/area/{sido_slug}/{gu_slug}-gu/"
    gu_crumbs = [("홈","/"),("지역별 서비스","/area/"),(sido_ko, sido_url),(gu_ko, None)]
    dong_by_slug = {s: k for k, s, *_ in dongs}

    # --- 구 종합 페이지 ---
    dong_links = "".join(f'<a href="{gu_url}{s}-dong/">{k}</a>' for k, s, *_ in dongs)
    adj_links = "".join(f'<a href="{u}">{n} 배관공사</a>' for n, u in adj_gu)
    gu_short = gu_ko.replace("구","").replace("시","")
    fixt = vpick(gu_ko+"f", FIXTURE_V)
    insp = vpick(gu_ko+"i", INSPECT_V)
    intro_html = "".join(f"<p>{p}</p>" for p in intro_paras)
    faq = [
        (f"{gu_ko} 하수구막힘은 바로 출동 가능한가요?",
         "지역과 시간대, 현장 상황에 따라 상담 후 안내됩니다. 증상과 사진을 먼저 보내주시면 필요한 장비를 더 정확히 판단할 수 있습니다."),
        (f"{gu_ko}에서 싱크대가 자주 막히면 고압세척이 필요한가요?",
         "반복 막힘은 단순 이물질보다 배관 내부 기름때·퇴적물이 원인일 수 있습니다. 배관내시경 확인 후 고압세척 여부를 판단하는 것이 좋습니다."),
        FAQ_CHEMICAL,
        (f"{gu_ko} 상가·음식점도 작업 가능한가요?",
         "상가, 음식점, 카페, 사무실, 병원, 학원 등 현장 구조에 따라 상담 가능합니다. 영업장 배관은 가정집보다 원인이 복잡할 수 있어 작업 전 확인이 중요합니다."),
    ]
    body = f"""{phero(f"{gu_ko} 배관공사", f"{gu_ko} 배관공사·하수구막힘 긴급 상담 | 스피드 배관공사", lead, gu_crumbs)}
<main>
<section class="section">
  <div class="container layout-sidebar">
    <div class="prose">
      <nav class="anchor-nav" aria-label="{gu_ko} 배관공사 바로가기">
        <h2>{gu_ko} 배관공사 바로가기</h2>
        <ul>
          <li><a href="#intro">{gu_ko} 배관공사 안내</a></li>
          <li><a href="#symptom">하수구막힘 증상</a></li>
          <li><a href="#fixtures">싱크대·변기·욕실 배수구</a></li>
          <li><a href="#inspection">배관내시경·고압세척</a></li>
          <li><a href="#area">{gu_ko} 서비스 가능 지역</a></li>
          <li><a href="#cost">비용 기준</a></li>
          <li><a href="#prepare">현장 확인 전 준비사항</a></li>
          <li><a href="#faq">자주 묻는 질문</a></li>
          <li><a href="#call">전화 상담</a></li>
        </ul>
      </nav>

      <h2 id="intro">{gu_ko} 배관공사 안내</h2>
      {intro_html}

      <h2 id="symptom">{gu_ko} 하수구막힘 주요 증상</h2>
      <ul class="ticks">{SYMPTOM_LI}</ul>
      <p>{gu_ko}는 건물 형태와 사용 환경이 다양해 현장마다 막힘의 원인이 다릅니다. 가정집은 머리카락·비누 찌꺼기·음식물 찌꺼기가, 음식점·카페는 기름 슬러지와 배관 내부 퇴적물이 주요 원인이 될 수 있습니다. 단순 스프링 작업으로 해결되기도 하지만, 반복 막힘이라면 배관내시경으로 내부 상태를 먼저 확인하는 구성이 좋습니다.</p>

      <h2 id="fixtures">싱크대·변기·욕실 배수구 문제</h2>
      <p>{fixt}</p>
      <h3>서비스 가능 항목</h3>
      <ul class="ticks">{SERVICE_LI}</ul>

      <h2 id="inspection">배관내시경·고압세척 작업</h2>
      <p>{insp}</p>
      <ol style="padding-left:20px;display:flex;flex-direction:column;gap:8px;">{WORK_LI}</ol>

      <h2 id="area">{gu_ko} 서비스 가능 지역</h2>
      <p>{gu_ko} 페이지에서는 1동·2동을 무리하게 나누지 않고 대표 동명으로 통합해 안내합니다. 아래 지역을 선택하면 해당 동의 배관공사·하수구막힘 안내를 확인할 수 있습니다.</p>
      <div class="tag-list">{dong_links}</div>
      <h3>인접 지역</h3>
      <div class="adjacent-links">{adj_links}</div>

      <h2 id="cost">비용이 달라지는 기준</h2>
      <p>{gu_ko} 배관공사 비용은 현장 조건에 따라 달라집니다. 아래 항목에 따라 필요한 장비와 작업 시간이 달라질 수 있습니다.</p>
      <ul class="ticks">{COST_LI}</ul>
      <p class="price-note">{COST_NOTE}</p>

      <h2 id="prepare">현장 확인 전 준비사항</h2>
      <p>{PREPARE_P}</p>

      <h2 id="faq">자주 묻는 질문</h2>
      <div class="faq-list">
{faq_html(faq)}      </div>

      <h2 id="call">{gu_ko} 전화 상담</h2>
      <p>{gu_ko}에서 하수구막힘이나 배관공사 상담이 필요하다면 증상, 위치, 건물 형태, 물이 내려가는 속도, 냄새 여부를 알려주세요. 스피드 배관공사는 현장 조건을 먼저 확인하고 필요한 작업 방향을 안내합니다.</p>
      <div class="local-cta">
        <a class="btn btn--primary btn--lg" href="tel:0000-0000">☎ 전화 상담하기</a>
        <a class="btn btn--secondary btn--lg" href="https://t.me/googleseolab" target="_blank" rel="noopener">사진 보내기</a>
        <a class="btn btn--secondary btn--lg" href="#cost">비용 기준 보기</a>
        <a class="btn btn--secondary btn--lg" href="/cases.html">현장사례 보기</a>
      </div>
    </div>
    {local_sidebar(f"{gu_ko} 배관 상담", f"{gu_ko} 전역 상담 가능. 증상·사진을 보내주시면 더 정확합니다.")}
  </div>
</section>
</main>
"""
    page(f"area/{sido_slug}/{gu_slug}-gu/index.html",
         f"{gu_ko} 배관공사·하수구막힘 | 싱크대·변기·배수구 막힘 상담 - 스피드 배관공사",
         f"{gu_ko} 하수구막힘·배관공사·누수탐지·고압세척 24시간 출동. 싱크대·변기·욕실 막힘 상담.",
         S + gu_url, body, jsonld=breadcrumb_jsonld(gu_crumbs) + faq_jsonld(faq))
    print(f"  [{gu_ko}] ~{_chars(body.split('</aside>')[0])}자")

    # --- 행정동 하위 페이지 ---
    for ko, slug, intro1, intro2, problem, adjacency in dongs:
        d_crumbs = [("홈","/"),("지역별 서비스","/area/"),(sido_ko, sido_url),(gu_ko, gu_url),(ko, None)]
        adj_html = f'<a href="{gu_url}">{gu_ko} 배관공사</a>' + "".join(
            (f'<a href="{gu_url}{s}-dong/">{n}</a>' if s in dong_by_slug
             else f'<a href="{u2}">{n}</a>')
            for entry in adjacency
            for (n, s, u2) in [(entry[0], entry[1], entry[2] if len(entry) > 2 else gu_url)])
        dfaq = [
            (f"{ko} 하수구막힘은 바로 출동 가능한가요?",
             "지역과 시간대, 현장 상황에 따라 상담 후 안내됩니다. 증상과 사진을 먼저 보내주시면 필요한 장비를 더 정확히 판단할 수 있습니다."),
            (f"{ko}에서 싱크대가 자주 막히면 어떻게 하나요?",
             "반복 막힘은 단순 이물질보다 배관 내부 기름때·퇴적물이 원인일 수 있습니다. 배관내시경으로 내부를 확인한 뒤 고압세척 여부를 판단하는 것이 좋습니다."),
            FAQ_CHEMICAL,
            (f"{ko} 상가·음식점도 작업 가능한가요?",
             "상가, 음식점, 카페, 사무실 등 현장 구조에 따라 상담 가능합니다. 영업장 배관은 가정집보다 원인이 복잡할 수 있어 작업 전 확인이 중요합니다."),
        ]
        dbody = f"""{phero(f"{ko} 배관공사", f"{ko} 배관공사·하수구막힘 상담 | 스피드 배관공사", f"{gu_ko} {ko}의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다.", d_crumbs)}
<main>
<section class="section">
  <div class="container layout-sidebar">
    <div class="prose">
      <nav class="anchor-nav" aria-label="{ko} 배관공사 바로가기">
        <h2>{ko} 배관공사 바로가기</h2>
        <ul>
          <li><a href="#intro">{ko} 배관공사 안내</a></li>
          <li><a href="#symptom">하수구막힘 증상</a></li>
          <li><a href="#fixtures">싱크대·변기·욕실</a></li>
          <li><a href="#services">서비스 가능 항목</a></li>
          <li><a href="#work">작업 방식</a></li>
          <li><a href="#inspection">배관내시경·고압세척</a></li>
          <li><a href="#cost">비용 기준</a></li>
          <li><a href="#area">인접 지역</a></li>
          <li><a href="#faq">자주 묻는 질문</a></li>
          <li><a href="#call">전화 상담</a></li>
        </ul>
      </nav>

      <h2 id="intro">{ko} 배관공사 안내</h2>
      <p>{intro1}</p>
      <p>{intro2}</p>

      <h2 id="symptom">{ko} 하수구막힘 증상</h2>
      <ul class="ticks">{SYMPTOM_LI}</ul>
      <p>{problem}</p>

      <h2 id="fixtures">{ko} 싱크대·변기·욕실 배수구 문제</h2>
      <p>{FIXTURE_P}</p>

      <h2 id="services">{ko} 서비스 가능 항목</h2>
      <ul class="ticks">{SERVICE_LI}</ul>

      <h2 id="work">{ko} 작업 방식 안내</h2>
      <p>{ko} 현장도 증상 확인과 사진·영상 상담을 먼저 진행한 뒤, 막힘 위치와 원인을 추정해 필요한 장비를 선택합니다. 작업 전 비용 기준을 안내드리고, 동의 후 막힘 제거 또는 배관 세척을 진행합니다.</p>
      <ol style="padding-left:20px;display:flex;flex-direction:column;gap:8px;">{WORK_LI}</ol>

      <h2 id="inspection">{ko} 배관내시경·고압세척</h2>
      <p>{INSPECT_P}</p>

      <h2 id="prepare">{ko} 자가 조치 시 주의사항</h2>
      <p>{SELFCARE_P}</p>

      <h2 id="cost">비용이 달라지는 기준</h2>
      <p>{ko} 배관공사 비용은 현장 조건에 따라 달라집니다. 아래 항목에 따라 필요한 장비와 작업 시간이 달라질 수 있습니다.</p>
      <ul class="ticks">{COST_LI}</ul>
      <p class="price-note">{COST_NOTE}</p>

      <h2 id="area">인접 지역</h2>
      <p>{ko}과 함께 인근 지역도 상담 가능합니다.</p>
      <div class="adjacent-links">{adj_html}</div>

      <h2 id="faq">자주 묻는 질문</h2>
      <div class="faq-list">
{faq_html(dfaq)}      </div>

      <h2 id="call">{ko} 전화 상담</h2>
      <p>{ko}에서 하수구막힘이나 배관공사 상담이 필요하다면 증상, 위치, 건물 형태, 물이 내려가는 속도, 냄새 여부를 알려주세요. 현장 조건을 먼저 확인하고 필요한 작업 방향을 안내합니다.</p>
      <div class="local-cta">
        <a class="btn btn--primary btn--lg" href="tel:0000-0000">☎ 전화 상담하기</a>
        <a class="btn btn--secondary btn--lg" href="https://t.me/googleseolab" target="_blank" rel="noopener">사진 보내기</a>
        <a class="btn btn--secondary btn--lg" href="{gu_url}">{gu_ko} 전체 보기</a>
      </div>
    </div>
    {local_sidebar(f"{ko} 배관 상담", f"{ko} 및 인근 지역 상담 가능. 증상·사진을 보내주시면 더 정확합니다.")}
  </div>
</section>
</main>
"""
        page(f"area/{sido_slug}/{gu_slug}-gu/{slug}-dong/index.html",
             f"{ko} 배관공사·하수구막힘 | 싱크대·변기·배수구 막힘 상담 - 스피드 배관공사",
             f"{gu_ko} {ko} 하수구막힘·배관공사·누수탐지·고압세척 24시간 출동. 싱크대·변기·욕실 막힘 상담.",
             f"{S}{gu_url}{slug}-dong/", dbody, jsonld=breadcrumb_jsonld(d_crumbs) + faq_jsonld(dfaq))
        print(f"    [{ko}] ~{_chars(dbody.split('</aside>')[0])}자")


# ---- 서초구 (행정동: 대표 동명 통합) ----
SEOCHO_DONGS = [
 ("서초동","seocho",
  "서초동은 서울중앙지방법원과 검찰청이 자리한 법조타운과 강남대로 변 오피스빌딩, 상가가 밀집한 지역입니다. 업무시설과 식당가가 함께 있어 사무실·상가 배관과 가정용 배관 상담이 동시에 들어옵니다.",
  "법조타운과 강남대로 주변은 점심·저녁 시간대 식당 이용이 많아 주방 배관에 기름때가 쌓이기 쉽고, 오피스빌딩은 화장실과 탕비실 배수 사용량이 많습니다. 업무에 지장이 없도록 시간대를 조율한 작업이 중요합니다.",
  "서초동에서는 사무실 탕비실 싱크대막힘과 상가 화장실 배수구 역류, 식당 주방 하수구막힘 상담이 잦습니다. 반복 막힘이라면 배관내시경으로 내부를 확인한 뒤 작업 방향을 정하는 것이 안전합니다.",
  [("잠원동","jamwon"),("반포동","banpo"),("방배동","bangbae")]),
 ("잠원동","jamwon",
  "잠원동은 한강변을 따라 신반포 일대 아파트 단지가 늘어선 주거 중심 지역입니다. 준공 연차가 있는 아파트가 많아 노후 배관에서 비롯된 상담이 꾸준히 들어옵니다.",
  "오래된 아파트는 배관 구배가 좋지 않거나 내부에 스케일이 쌓여 배수가 느려지는 경우가 많습니다. 한강변 고층 단지는 입상관이 길어 여러 세대에 걸쳐 증상이 나타나기도 합니다.",
  "잠원동에서는 아파트 욕실 배수 지연과 세면대·싱크대막힘, 저층 세대 역류 상담이 많습니다. 여러 세대 동시 증상은 공용관 문제일 수 있어 배관내시경 확인이 도움이 됩니다.",
  [("서초동","seocho"),("반포동","banpo"),("방배동","bangbae")]),
 ("반포동","banpo",
  "반포동은 반포자이·래미안 등 대단지 아파트와 고속터미널 상권이 어우러진 지역입니다. 대규모 주거와 대형 상권이 함께 있어 가정용·상업용 배관 상담이 고루 들어옵니다.",
  "대단지 아파트는 세대 전용관과 공용관을 구분한 진단이 중요하고, 고속터미널 상권의 식당가는 주방 기름때로 인한 막힘이 잦습니다. 사용량이 많은 만큼 정기 점검이 유효한 지역입니다.",
  "반포동에서는 아파트 욕실·주방 배수 지연과 상가 화장실 배수구 막힘, 식당 주방 하수구막힘 상담이 많습니다. 반복 증상은 내부 퇴적물이 원인일 수 있어 고압세척 여부를 검토합니다.",
  [("잠원동","jamwon"),("서초동","seocho"),("방배동","bangbae")]),
 ("방배동","bangbae",
  "방배동은 카페골목과 주택가가 어우러진 지역으로, 빌라·단독주택과 저층 상가가 많습니다. 노후 주택 배관과 카페·음식점 주방 배관 상담이 함께 들어옵니다.",
  "오래된 빌라·단독은 배관 노후나 구배 문제로 막힘이 잦고, 카페골목의 음료 매장은 우유·시럽·커피 찌꺼기가 배관에 엉기기도 합니다. 현장별로 원인이 달라 작업 전 확인이 중요합니다.",
  "방배동에서는 빌라 화장실 악취·배수 지연과 카페 싱크대막힘, 단독주택 오수관 막힘 상담이 많습니다. 외부 배관이나 정화조 관련 증상은 현장 구조를 먼저 확인합니다.",
  [("서초동","seocho"),("반포동","banpo"),("양재동","yangjae")]),
 ("양재동","yangjae",
  "양재동은 양재시민의숲과 화물터미널, 오피스·전시시설이 자리한 지역으로, 업무·물류 시설과 상가가 섞여 있습니다. 상업용 배관과 대형 시설 배관 상담이 들어옵니다.",
  "물류·전시시설은 사용량이 많아 화장실과 식당가 배수 부담이 크고, 오피스는 지하 배관의 퇴적물이 문제가 되곤 합니다. 시설 운영에 지장이 없도록 시간대 조율이 필요합니다.",
  "양재동에서는 상가·오피스 화장실 배수구 막힘과 식당 주방 하수구막힘, 지하 배관 상담이 많습니다. 사용량이 많은 시설은 정기 고압세척으로 막힘을 예방하는 것이 좋습니다.",
  [("방배동","bangbae"),("우면동","umyeon"),("서초동","seocho")]),
 ("우면동","umyeon",
  "우면동은 우면산 자락의 연구단지와 보금자리 아파트가 어우러진 지역입니다. 연구시설과 신축 주거가 함께 있어 시설 배관과 생활 배관 상담이 들어옵니다.",
  "신축 아파트는 입주 초기 배수 점검 수요가, 연구·업무 시설은 사용량에 따른 배수 부담이 있습니다. 새 건물이라도 시공 마감이나 구배 문제로 막힘이 생길 수 있어 점검이 유효합니다.",
  "우면동에서는 아파트 욕실·싱크대막힘과 시설 화장실 배수구 막힘, 바닥 배수 지연 상담이 많습니다. 입주 초기 반복 증상은 배관내시경으로 시공 상태를 확인해 두면 관리가 수월합니다.",
  [("양재동","yangjae"),("내곡동","naegok"),("방배동","bangbae")]),
 ("내곡동","naegok",
  "내곡동은 헌인마을과 보금자리지구를 포함한 지역으로, 단독주택과 신축 아파트가 혼재합니다. 단독·주거 배관과 외부 오수관 상담이 주로 들어옵니다.",
  "단독주택은 외부 오수관과 정화조 연결부에서 문제가 생기는 경우가 있고, 신축 아파트는 초기 점검 위주의 상담이 많습니다. 외부 배관은 현장 구조 확인이 특히 중요합니다.",
  "내곡동에서는 단독주택 오수관 막힘과 아파트 욕실 배수 지연, 싱크대막힘 상담이 많습니다. 정화조·외부 배관 관련 증상은 현장을 먼저 확인한 뒤 작업 방식을 안내드립니다.",
  [("우면동","umyeon"),("양재동","yangjae"),("방배동","bangbae")]),
]
build_gu_system("서울특별시","seoul","/area/seoul/","서초구","seocho",
    "서초동 법조타운과 반포·잠원 아파트, 방배 주택가까지 — 서초구 전역의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다.",
    ["서초구는 서초동 법조타운과 강남대로 업무지구, 반포·잠원 대단지 아파트, 방배동 주택가가 어우러진 지역입니다. 업무시설과 주거, 상권이 섞여 있어 배관 문제가 단순한 가정용 막힘에서 끝나지 않는 경우가 많습니다.",
     "특히 서초동, 반포동, 잠원동, 방배동, 양재동 일대는 오피스빌딩과 식당가, 대단지 아파트가 함께 있어 싱크대 배수 불량, 바닥 배수구 역류, 화장실 악취, 오수관 막힘 상담이 자주 발생합니다.",
     "스피드 배관공사는 현장의 건물 형태와 막힘 정도를 먼저 확인한 뒤 필요한 작업 방향을 안내합니다. 단순 막힘인지 반복 막힘인지에 따라 장비와 작업 시간이 달라지므로, 무리한 자가 조치보다 상담을 통해 원인을 정확히 파악하는 것이 안전합니다."],
    "", SEOCHO_DONGS,
    [("강남구","/area/seoul/gangnam-gu/"),("송파구","/area/seoul/songpa-gu/"),("동작구","/area/seoul/"),("관악구","/area/seoul/")])

# ---- 송파구 (행정동: 대표 동명 통합) ----
SONGPA_DONGS = [
 ("잠실동","jamsil",
  "잠실동은 롯데월드타워와 대단지 아파트, 대형 상권이 밀집한 송파의 중심 지역입니다. 대형 시설과 주거가 함께 있어 상업용·가정용 배관 상담이 고루 들어옵니다.",
  "대형 상가·시설은 화장실과 식당가 사용량이 많아 바닥 배수구 역류와 오수관 막힘이 잦고, 대단지 아파트는 공용관과 세대 전용관 구분이 중요합니다.",
  "잠실동에서는 상가 화장실 배수구 역류와 아파트 욕실 배수 지연, 식당 주방 하수구막힘 상담이 많습니다. 사용량이 많은 시설은 정기 점검과 고압세척이 도움이 됩니다.",
  [("신천동","sincheon"),("삼전동","samjeon"),("석촌동","seokchon")]),
 ("신천동","sincheon",
  "신천동은 잠실역 일대 상권과 먹자골목이 발달한 지역으로, 음식점·술집·카페가 밀집해 있습니다. 영업장 주방 배관 상담이 특히 많이 들어옵니다.",
  "음식점이 많아 기름 슬러지로 인한 배관 막힘이 잦고, 지하 매장은 바닥 배수구 역류 상담이 자주 발생합니다. 영업 시간을 고려한 무중단 작업이 중요합니다.",
  "신천동에서는 음식점 주방 하수구막힘과 지하 상가 바닥 배수구 역류, 싱크대막힘 상담이 많습니다. 반복 막힘은 고압세척으로 배관 내부를 세척해야 재발을 줄일 수 있습니다.",
  [("잠실동","jamsil"),("방이동","bangi"),("석촌동","seokchon")]),
 ("풍납동","pungnap",
  "풍납동은 서울아산병원 인근의 주택·아파트가 어우러진 주거 중심 지역입니다. 주거 배관과 병원 인근 상가 배관 상담이 들어옵니다.",
  "주거 시설은 생활 이물질로 인한 막힘이 주를 이루고, 병원 인근 상가·식당은 화장실·주방 사용량이 많습니다. 오래된 주택은 배관 노후 상담도 함께 들어옵니다.",
  "풍납동에서는 아파트·주택 욕실 배수 지연과 싱크대막힘, 상가 화장실 배수구 막힘 상담이 많습니다. 반복 증상은 배관 내부 상태 확인 후 세척 여부를 판단합니다.",
  [("송파동","songpa"),("삼전동","samjeon"),("잠실동","jamsil")]),
 ("송파동","songpa",
  "송파동은 백제고분로 상권과 주택가가 어우러진 지역으로, 상가와 주거가 섞여 있습니다. 가정용·상업용 배관 상담이 고루 들어옵니다.",
  "주택가는 생활 배관 막힘이, 상권의 식당·카페는 주방 기름때로 인한 막힘이 잦습니다. 노후 건물은 배관 구배 문제로 반복 막힘이 나타나기도 합니다.",
  "송파동에서는 주택 욕실·싱크대막힘과 상가 화장실 배수구 역류, 식당 주방 하수구막힘 상담이 많습니다. 반복 막힘은 내시경 확인 후 작업 방향을 정합니다.",
  [("석촌동","seokchon"),("삼전동","samjeon"),("가락동","garak")]),
 ("석촌동","seokchon",
  "석촌동은 석촌호수 인근의 카페·음식점과 주택이 어우러진 지역입니다. 카페·외식 상권 배관과 주거 배관 상담이 함께 들어옵니다.",
  "카페·음료 매장은 우유·시럽·커피 찌꺼기가 배관에 엉기는 경우가 있고, 주택은 생활 이물질로 인한 막힘이 주를 이룹니다. 매장은 영업 시간 조율이 중요합니다.",
  "석촌동에서는 카페·음식점 싱크대막힘과 주택 욕실 배수 지연, 바닥 배수구 역류 상담이 많습니다. 매장의 반복 막힘은 고압세척이 효과적입니다.",
  [("송파동","songpa"),("삼전동","samjeon"),("잠실동","jamsil")]),
 ("삼전동","samjeon",
  "삼전동은 다세대·빌라가 밀집한 주거 중심 지역으로, 생활 배관 상담이 주를 이룹니다. 근린 상가의 배관 상담도 함께 들어옵니다.",
  "다세대·빌라는 공용 배수관에 부담이 큰 편이라 한 세대의 막힘이 다른 세대에 영향을 주기도 합니다. 오래된 건물은 배관 노후 상담이 잦습니다.",
  "삼전동에서는 빌라 화장실 배수 지연·악취와 싱크대막힘, 공용관 역류 상담이 많습니다. 여러 세대 동시 증상은 공용관 점검이 우선입니다.",
  [("석촌동","seokchon"),("송파동","songpa"),("잠실동","jamsil")]),
 ("가락동","garak",
  "가락동은 가락농수산물도매시장이 자리한 지역으로, 대규모 시장과 상가, 아파트가 어우러져 있습니다. 시장·상가의 대량 배수 상담이 특징적입니다.",
  "시장과 식당가는 물·음식물 사용량이 매우 많아 바닥 배수구 역류와 오수관 막힘이 잦습니다. 대량 배수 시설은 정기적인 고압세척 관리가 중요합니다.",
  "가락동에서는 시장·상가 대량 배수관 막힘과 식당 주방 하수구막힘, 아파트 배수 지연 상담이 많습니다. 대량 배수 현장은 내시경 점검과 정기 세척이 효과적입니다.",
  [("문정동","munjeong"),("석촌동","seokchon"),("송파동","songpa")]),
 ("문정동","munjeong",
  "문정동은 법조단지와 가든파이브, 오피스·상가가 밀집한 업무 중심 지역입니다. 업무시설과 상가 배관 상담이 주로 들어옵니다.",
  "오피스·상가는 화장실과 탕비실, 식당가 사용량이 많아 배수 부담이 크고, 지하 배관의 퇴적물이 문제가 되곤 합니다. 업무에 지장이 없도록 시간대 조율이 필요합니다.",
  "문정동에서는 오피스·상가 화장실 배수구 막힘과 탕비실 싱크대막힘, 식당 주방 하수구막힘 상담이 많습니다. 사용량이 많은 시설은 정기 점검이 유효합니다.",
  [("가락동","garak"),("장지동","jangji"),("송파동","songpa")]),
 ("장지동","jangji",
  "장지동은 위례·문정 인근의 아파트와 물류시설이 어우러진 지역입니다. 신축 주거와 물류 시설의 배관 상담이 들어옵니다.",
  "신축 아파트는 입주 초기 배수 점검이, 물류 시설은 사용량에 따른 배수 부담이 있습니다. 새 건물이라도 시공·구배 문제로 막힘이 생길 수 있어 점검이 유효합니다.",
  "장지동에서는 아파트 욕실·싱크대막힘과 물류 시설 화장실 배수구 막힘, 바닥 배수 지연 상담이 많습니다. 초기 반복 증상은 내시경으로 시공 상태를 확인합니다.",
  [("문정동","munjeong"),("가락동","garak"),("거여동","geoyeo")]),
 ("방이동","bangi",
  "방이동은 올림픽공원과 먹자골목이 어우러진 지역으로, 음식점·술집 상권과 주거가 함께 있습니다. 영업장 주방 배관 상담이 많이 들어옵니다.",
  "먹자골목 음식점은 기름 슬러지로 인한 막힘이 잦고, 주거지는 생활 배관 막힘이 주를 이룹니다. 영업 시간을 고려한 작업 일정 조율이 중요합니다.",
  "방이동에서는 음식점 주방 하수구막힘과 상가 바닥 배수구 역류, 주택 싱크대막힘 상담이 많습니다. 반복 막힘은 고압세척으로 내부를 세척하는 것이 효과적입니다.",
  [("오금동","ogeum"),("가락동","garak"),("신천동","sincheon")]),
 ("오금동","ogeum",
  "오금동은 아파트와 주택이 어우러진 주거 중심 지역으로, 생활 배관 상담이 주를 이룹니다. 근린 상가의 배관 상담도 함께 들어옵니다.",
  "아파트는 준공 연차에 따라 배수 지연이 나타나고, 주택은 생활 이물질로 인한 막힘이 잦습니다. 근린 상가는 업종에 따라 배수 부담이 다릅니다.",
  "오금동에서는 아파트 욕실 배수 느림과 싱크대·세면대막힘, 상가 화장실 배수구 막힘 상담이 많습니다. 반복 증상은 내부 상태 확인 후 세척 여부를 판단합니다.",
  [("방이동","bangi"),("가락동","garak"),("거여동","geoyeo")]),
 ("거여동","geoyeo",
  "거여동은 위례신도시 인근의 재개발 아파트가 들어선 지역으로, 신축과 기존 주거가 혼재합니다. 신축 단지의 초기 점검과 기존 주거의 노후 배관 상담이 함께 들어옵니다.",
  "신축 아파트는 입주 초기 이물질로 인한 배수 지연이, 기존 주택은 노후·구배 문제로 인한 막힘이 나타납니다. 신축은 점검 위주, 노후는 원인 제거 위주로 접근이 다릅니다.",
  "거여동에서는 신축 아파트 배수 점검과 기존 주택 욕실·싱크대막힘, 바닥 배수구 역류 상담이 많습니다. 초기 반복 막힘은 내시경 확인이 도움이 됩니다.",
  [("마천동","macheon"),("오금동","ogeum"),("장지동","jangji")]),
 ("마천동","macheon",
  "마천동은 단독·다세대 주택과 재개발이 진행되는 지역으로, 노후 주택 배관 상담이 주를 이룹니다. 근린 상가의 배관 상담도 함께 들어옵니다.",
  "오래된 단독·다세대는 배관 노후나 구배 문제로 막힘이 잦고, 외부 오수관·정화조 관련 증상이 나타나기도 합니다. 현장 구조 확인이 특히 중요합니다.",
  "마천동에서는 단독·다세대 욕실 배수 지연과 싱크대막힘, 외부 오수관 막힘 상담이 많습니다. 외부 배관·정화조 증상은 현장을 먼저 확인한 뒤 작업 방식을 안내드립니다.",
  [("거여동","geoyeo"),("오금동","ogeum"),("방이동","bangi")]),
]
build_gu_system("서울특별시","seoul","/area/seoul/","송파구","songpa",
    "잠실 상권과 가락시장, 문정 업무단지까지 — 송파구 전역의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다.",
    ["송파구는 잠실 롯데월드타워 상권과 대단지 아파트, 가락시장, 문정 법조·업무단지, 위례 인근 신축 주거가 어우러진 지역입니다. 대형 시설과 주거, 시장이 함께 있어 배관 문제의 원인이 현장마다 다양합니다.",
     "특히 잠실동, 신천동, 가락동, 문정동, 방이동 일대는 대형 상가와 시장, 먹자골목이 밀집해 바닥 배수구 역류, 주방 기름때 막힘, 오수관 막힘 상담이 자주 발생합니다.",
     "스피드 배관공사는 현장의 건물 형태와 사용 환경을 먼저 확인한 뒤 필요한 작업 방향을 안내합니다. 사용량이 많은 시설은 정기 점검과 고압세척으로 막힘을 예방하는 것이 운영에 유리합니다."],
    "", SONGPA_DONGS,
    [("강남구","/area/seoul/gangnam-gu/"),("서초구","/area/seoul/seocho-gu/"),("강동구","/area/seoul/gangdong-gu/"),("성남시","/area/gyeonggi/seongnam-si/")])

print("\\nSEOCHO/SONGPA SYSTEMS BUILT.")


# ===========================================================================
# 전국 시·군·구 페이지 자동 생성 (공식 데이터 기반, 브리프 권장 granularity)
#   - 이미 고유 콘텐츠가 있는 시군구(CUSTOM_GUNGU_URL)는 제외
#   - 각 페이지: 지역유형별 안내 + 형제 시군구 내부링크 + 서비스 본문 + FAQ
# ===========================================================================
# 시군구별 지역 특성 데이터 — 고유 콘텐츠 생성에 활용
SIGUNGU_DATA = {
    "강남구": {"type":"도심상권","trait":"삼성·현대 본사와 압구정·신사 고급상권, 신축 대형 오피스텔과 고급 아파트 밀집","plumbing":"고급 주택 정밀 배관 손상, 대형 빌딩 복합 배수 역류, 스테인리스 싱크대 연결부 악취"},
    "서초구": {"type":"도심상권","trait":"법원·검찰·대형 로펌 밀집, 강남대로 따라 업무시설과 고급 주택 혼재","plumbing":"고층 오피스텔 배수 역류, 바닥 배수구 기름때 역류, 반복 막힘 근본 원인 세척"},
    "강동구": {"type":"주거밀집","trait":"아파트 대단지·다세대·빌라 혼합, 장지·고덕동 신축 아파트 증가","plumbing":"신축 배관 구배 불량, 수압 불균형으로 트랩 건조, 공동 오수관 퇴적"},
    "송파구": {"type":"도심상권","trait":"롯데월드·스타필드·가락농수산물시장·법조단지 복합 지역","plumbing":"대형 상가 기름 슬러지, 시장 오수관 퇴적, 대형 주방 배수 고장"},
    "종로구": {"type":"구도심","trait":"역사문화·관광 중심, 한옥 구역·오래된 저층 주택과 현대 빌딩 혼재","plumbing":"노후 철제 배관 내부 녹슬음, 한옥 Y자관 손상, 외부 오수관 기울기 불량"},
    "중구": {"type":"도심상권","trait":"명동·남대문시장 상업지구 중심, 노후 저층건물과 현대 쇼핑몰 혼재","plumbing":"노후 배관 부식, 시장 기름 슬러지, 지표면 침하 오수관 손상"},
    "용산구": {"type":"도심상권","trait":"이태원·한남동 특수 상권, 미군기지 이전 후 재개발 활발, 외국인 밀집","plumbing":"상업용 배수 과부하, 외부 오수관 누수, 지반 침하 배관 파열"},
    "성동구": {"type":"주거밀집","trait":"아파트 단지 밀집, 성수동 카페거리 특성상 식음료 업종 증가","plumbing":"카페 폐수 기름때, 다세대 주택 부실 배관, 공동 오수관 역류"},
    "마포구": {"type":"도심상권","trait":"홍대·망원·마곡 상권 이원화, 신축 주상복합과 노후 주택 공존","plumbing":"신축 배수 용량 오류, 구 배관 내부 퇴적, 음식점 기름 슬러지"},
    "영등포구": {"type":"도심상권","trait":"여의도 금융·방송 단지와 당산·문래 상권 혼합, 대형 건물 밀집","plumbing":"대형 건물 공용 배관 역류, 지하층 역류 침수, 복합용도 배수 간선 막힘"},
    "강서구": {"type":"주거밀집","trait":"목동 대단지 아파트·마곡지구 신축 혼합, 김포공항 인근 물류 상권","plumbing":"대단지 아파트 바닥 배수구 역류, 노후 금속 배관 녹슬음, 세탁기 배수 막힘"},
    "구로구": {"type":"산업공단","trait":"구로 디지털단지·가리봉동 IT·제조업 상권, 소규모 공장·사무실 밀집","plumbing":"공장 배수 기름·금속 찌꺼기, 다세대 상가 폐수 처리 과부하, 외부 오수관 손상"},
    "노원구": {"type":"주거밀집","trait":"중계동·상계동·노원역 대단지 아파트 중심, 학원가·상권 혼합","plumbing":"대단지 공동 배관 역류, 오래된 배관 내부 스케일, 세탁기·비누 거품 막힘"},
    "은평구": {"type":"주거밀집","trait":"불광·역촌·녹번동 주거지, 아파트·다세대·빌라 혼합, 한옥마을 일부","plumbing":"다세대 주택 개별 정화조 불량, 오래된 배관 부식, 욕실 배수구 모래·흙 유입"},
    "서대문구": {"type":"대학가","trait":"이화여대·연세대·홍제동 주택 혼재, 대학 상권과 다세대 주택 집중","plumbing":"학생 다세대 구조 불량, 하수 처리 용량 부족, 음식물쓰레기 직투 막힘"},
    "관악구": {"type":"대학가","trait":"서울대·신림동 대학가 중심, 학생 원룸·저가 식당 고밀도 밀집","plumbing":"저가 주택 배관 부실, 음식물 직투 막힘, 공동 오수관 반복 역류"},
    "동대문구": {"type":"도심상권","trait":"동대문시장·광장시장 의류·도매 상권 중심, 노후 저층 건물 다수","plumbing":"시장 상가 기름 슬러지, 노후 배관 부식, 지표면 침하 배관 손상"},
    "성북구": {"type":"주거밀집","trait":"정릉·길음동 아파트와 단독주택 혼합, 고려대 인근 대학가 상권","plumbing":"다세대·단독 혼합 배관 구조, 오래된 노후관 부식, 대학가 음식점 기름때"},
    "강북구": {"type":"주거밀집","trait":"미아사거리·수유동 주거 밀집, 단독·다세대 주택 비율 높음","plumbing":"노후 단독 주택 배관 부식, 다세대 공동 오수관 역류, 외부 배관 정화조 연결 불량"},
    "도봉구": {"type":"주거밀집","trait":"도봉산 인근 주거지, 창동·방학동 아파트와 단독 주택 혼재","plumbing":"산기슭 지형상 외부 배관 기울기 문제, 낙엽·토사 유입, 아파트 공동관 역류"},
    "중랑구": {"type":"주거밀집","trait":"면목동·상봉동 다세대·빌라 밀집 주거지, 서울 외곽 접경지역","plumbing":"다세대 빌라 배관 부실, 공동 오수관 퇴적, 노후 건물 배관 부식"},
    "광진구": {"type":"주거밀집","trait":"건국대·화양동 대학가 상권, 능동·군자동 아파트 단지 혼합","plumbing":"대학가 음식점 기름때, 아파트 공동관 역류, 신촌처럼 상권 하수 과부하"},
    "동작구": {"type":"주거밀집","trait":"흑석·노량진 대학가 상권, 사당·방배 주거지 혼합","plumbing":"학원가 상가 배수 부하, 오래된 배관 스케일, 노량진 고시촌 다세대 막힘"},
    "양천구": {"type":"주거밀집","trait":"목동 중산층 아파트 단지, 신정·신월동 다세대 혼재","plumbing":"아파트 공동 배수관 역류, 목동 구형 배관 스케일, 다세대 배수 연결 불량"},
    "수원시": {"type":"신도시","trait":"장안·권선·팔달·영통구 복합, 삼성전자 직원 주거 수요와 신도시 아파트 밀집","plumbing":"신도시 배수 설계 오류, 고지대 수압 불균형, 다원화된 상업 배수 처리"},
    "성남시": {"type":"신도시","trait":"판교테크노밸리 IT 기업 밀집, 분당 중산층 아파트와 구시가지 이원화","plumbing":"신축 건물 배수 설계 오류, 판교 지반 침하 배관 손상, 수압 변동"},
    "고양시": {"type":"주거밀집","trait":"일산신도시 완성형 도시, 호수공원·대형 쇼핑몰과 주택 밀집 혼재","plumbing":"신도시 지반 기울기 문제, 공동 주택 대규모 역류, 신축 배관 시공 오류"},
    "용인시": {"type":"신도시","trait":"분당선 연장 급성장, 기흥·처인구 신축 아파트 대규모 공급","plumbing":"신축 배관 용량 부족, 고지대 수압 불균형, 개발지역 토양 침하"},
    "부천시": {"type":"주거밀집","trait":"소사·원미구 아파트 밀집, 상동·중동 구도시 다세대 주택 다수","plumbing":"구도시 배관 노후화, 다세대 주택 부실 배수 연결, 공동 오수관 역류"},
    "안양시": {"type":"주거밀집","trait":"평촌신도시·동안구 중산층 주택 밀집, 범계역·평촌 상권 발달","plumbing":"신도시 지반 배관 손상, 저수지 수압 불균형, 구 배관 부식"},
    "화성시": {"type":"신도시","trait":"동탄1·2신도시 급성장, 삼성전자 기흥캠퍼스 인근, 인구 급증 지역","plumbing":"신도시 기반시설 미흡, 배수 간선 용량 부족, 지반 침하 배관 손상"},
    "남양주시": {"type":"주거밀집","trait":"별내신도시·진접읍 신축 주거 확대, 구시가지와 신도시 이원화","plumbing":"신축 배관 설계 오류, 지형 고저차로 수압 불균형, 개별 정화조 불량"},
    "평택시": {"type":"산업공단","trait":"삼성전자·LG전자 반도체 공장 밀집, 주한미군기지 평택 이전으로 인구 급증","plumbing":"공장 폐수 기름·금속 찌꺼기, 군부대 대규모 배수 시스템, 산업 배수 특수 처리"},
    "의정부시": {"type":"주거밀집","trait":"경의중앙선 따라 발달, 장암·가능동 아파트와 다가구 주택 혼재","plumbing":"다세대 주택 배관 부실, 음식물 쓰레기 직투, 오래된 하수도 용량 부족"},
    "파주시": {"type":"농어촌","trait":"임진강 인근 농촌지역, 교하신도시·운정신도시 확장, 한류월드 개발","plumbing":"농촌 정화조 불량, 단독주택 외부 오수관 손상, 강변 침수 배관 매몰"},
    "시흥시": {"type":"산업공단","trait":"시화공단·배곧신도시 혼합, 석유화학·전자·기계 산업 집중","plumbing":"화학 배수 부식성 물질, 공업 폐수 특수 처리, 높은 지표수위 배관 침수"},
    "김포시": {"type":"농어촌","trait":"한강 변 농경지·어촌 혼합, 장기지구 신도시 개발 급진행","plumbing":"농촌 정화조 오수 역류, 강변 침수 위험 배관, 신도시 외부 오수관 누수"},
    "광명시": {"type":"주거밀집","trait":"철산·하안동 구도시 아파트 집중, 광명역세권 KTX 신개발 진행","plumbing":"구도시 배관 노후화, 지반 침하 오수관 손상, 대단지 공동 배수 역류"},
    "광주시": {"type":"신도시","trait":"경강선 개통 급성장, 오포·곤지암 신축 상권과 공장 혼합","plumbing":"신도시 기반시설 미흡, 지반 불안정 배관 손상, 배수 간선 용량 초과"},
    "이천시": {"type":"산업공단","trait":"도자기산업 클러스터, SK하이닉스 반도체 공장 밀집, 산업용 배수 다량","plumbing":"반도체 공장 초순수 배수, 도자기 산업 폐수 오염, 산업용 대용량 배관 막힘"},
    "안산시": {"type":"산업공단","trait":"반월·시화공단 화학·정유·철강 산업 밀집, 다문화 외국인 거주 집중","plumbing":"화학 배수 부식성, 공업 폐수 특수 처리, 고농도 기름 슬러지"},
    "오산시": {"type":"주거밀집","trait":"지제역·세교신도시 아파트 밀집, KTX 세마역 개발 기대감","plumbing":"신도시 배수 용량 문제, 신축 배관 설계 오류, 지반 침하 손상"},
    "하남시": {"type":"신도시","trait":"미사강변도시·위례신도시 신축 아파트 대규모 공급, 강변 입지","plumbing":"강변 지반 수위 영향 배관, 신도시 배수 용량 부족, 신축 배관 구배 오류"},
    "구리시": {"type":"주거밀집","trait":"토평·갈매동 아파트 단지, 광릉내 수변지역, 중산층 주거지","plumbing":"신도시 배수 용량 부족, 신축 배관 오류, 지반 기울기 문제"},
    "의왕시": {"type":"주거밀집","trait":"포일·고천동 신도시 아파트, 철도 차량기지 인근 소규모 공장 혼합","plumbing":"신도시 배수 설계 미흡, 신축 배관 용량 오류, 지반 침하 손상"},
    "해운대구": {"type":"관광특구","trait":"해수욕장·마리나·센텀시티·고급 주상복합 밀집, 관광객과 주민 혼재","plumbing":"고급 주택 역류 방지 배관 고장, 염분 부식, 대형 호텔 배수 시스템 복잡"},
    "부산진구": {"type":"도심상권","trait":"서면·가야동 상권과 주택 혼재, 부전시장·롯데몰 인접 복합 지역","plumbing":"상가 기름 슬러지, 노후 배관 스케일, 상가·주거 혼합 배수 역류"},
    "남구": {"type":"주거밀집","trait":"대연·용호동 아파트 밀집, 부산항 인근 물류기지, UN기념공원 인근","plumbing":"다세대 주택 배관 부실, 항만 염분 부식, 공동 오수관 정기 청소"},
    "동래구": {"type":"주거밀집","trait":"사직·온천동 주택 밀집, 온천관광지역 특성, KBS부산 방송국 인근","plumbing":"온천수 미네랄 퇴적, 노후 배관 부식, 온천시설 고온수 배관 손상"},
    "수성구": {"type":"주거밀집","trait":"범어·만촌·신매동 고급 아파트 밀집, 대구 강남 역할, 수성못 관광지","plumbing":"고급 주택 정밀 배관 손상, 수압 불균형, 신축 배관 설계 오류"},
    "달서구": {"type":"주거밀집","trait":"월배·송현동 아파트 대단지, 성당못공원 주변 주택 집중, 상업 지구 혼합","plumbing":"대단지 공동 배관 역류, 오래된 배관 스케일, 욕실 배수구 역류 방지"},
    "남동구": {"type":"주거밀집","trait":"인천공항 동쪽, 주안·간석동 주택 밀집, 남동공단 인근 산업지역 혼합","plumbing":"구도시 배관 노후화, 공단 배수 오염, 높은 지표수위 침수"},
    "연수구": {"type":"신도시","trait":"송도국제도시·인천대학교 인근, 신축 고급 아파트와 국제 비즈니스 혼합","plumbing":"신도시 배수 용량 부족, 해양 염수 유입 부식, 신축 배관 설계 오류"},
    "부평구": {"type":"주거밀집","trait":"부평역·산곡동 상권, 아파트·다세대 혼합 구도시 주거지역","plumbing":"구도시 배관 부식, 다세대 배수 연결 불량, 공동 오수관 정기 점검"},
    "서구": {"type":"도심상권","trait":"둔산신도시 금융·의료 밀집, 대전역·으능정이 문화거리 인근 신구 혼재","plumbing":"신도시 배수 용량 초과, 신축 배관 설계 오류, 복합용도 배수 간선 혼잡"},
    "유성구": {"type":"신도시","trait":"카이스트·대덕연구단지 인근, 신도시 아파트와 연구시설 집중","plumbing":"신도시 지반 기울기 문제, 연구시설 특수 배수, 신축 배관 시공 오류"},
    "북구": {"type":"도심상권","trait":"광주 첨단산업단지·신도시 상권 중심, 신축 주거·상업 복합 집중","plumbing":"신도시 배수 설계 오류, 지반 기울기 불리, 신축 배관 용량 오류"},
    "남구_광주": {"type":"주거밀집","trait":"봉선동·주월동 중산층 아파트 밀집, 광주대·조선대 대학가 인근","plumbing":"대학가 음식점 기름때, 아파트 공동관 역류, 구 배관 스케일"},
    "남구_울산": {"type":"산업공단","trait":"현대중공업·현대자동차 공장 밀집, 산업용 배수 다량, 석유화학 시설 인근","plumbing":"산업 배수 특수 물질, 공장 폐수 기름·중금속, 대규모 배관 복잡"},
    "창원시": {"type":"산업공단","trait":"마산·진해·창원 3개 시 통합, 조선·기계·전기산업 클러스터, 항만 물류 집중","plumbing":"조선 산업 기름 찌꺼기, 해양 염분 부식, 대규모 산업 배수 시스템"},
    "청주시": {"type":"신도시","trait":"오창과학산업단지·흥덕구 신도시 발달, 충청권 행정·유통 중심","plumbing":"신도시 배수 용량 부족, 신축 배관 설계 오류, 지반 기울기 문제"},
    "전주시": {"type":"도심상권","trait":"전주한옥마을·전주역 상권, 문화·관광·교육 도시, 전북도청 소재지","plumbing":"한옥 기와지붕 Y자관 손상, 노후 배관 부식, 관광지 음식점 기름 슬러지"},
    "세종시": {"type":"신도시","trait":"정부세종청사 중심 계획도시, 신축 비율 매우 높음, 행복도시 지속 개발","plumbing":"신도시 배수 설계 미흡, 신축 배관 용량 오류, 지반 불안정 손상"},
    "울주군": {"type":"농어촌","trait":"온양읍·웅촌면 농촌지역, 현대자동차 울산공장 인근 단독주택 밀집","plumbing":"농촌 정화조 오수 역류, 단독주택 외부 배관 손상, 공장 인근 지반 침하"},
    "기장군": {"type":"관광특구","trait":"기장해변·오시리아 관광단지, 고리원전 인근, 해안 관광지","plumbing":"해안 염분 부식, 관광시설 배수 과부하, 원전 인근 특수 지반"},
    "경주시": {"type":"관광특구","trait":"불국사·석굴암·대릉원 세계문화유산, 관광객 연중 집중, 숙박시설 다수","plumbing":"관광지 숙박 배수 부하 증가, 노후 배관 부식, 정기 청소 필수"},
    "포항시": {"type":"산업공단","trait":"포스코 철강 산업 중심, 영일만 항만 물류, 첨단소재 산업 집중","plumbing":"철강 산업 금속 찌꺼기, 항만 염분 부식, 대용량 산업 배관"},
    "구미시": {"type":"산업공단","trait":"구미국가산업단지 전자·반도체 밀집, 삼성·LG 생산기지, 외국인 근로자 다수","plumbing":"전자 공장 초순수 배수, 산업 배수 특수 처리, 공단 기숙사 배관 부하"},
    "안동시": {"type":"관광특구","trait":"하회마을·도산서원 전통문화 관광지, 경북도청 신도청 이전","plumbing":"전통 한옥 배관 노후화, 관광지 음식점 기름때, 신도청 신축 배관 오류"},
    "익산시": {"type":"주거밀집","trait":"전북혁신도시·익산역 상권, 식품·보석산업 클러스터","plumbing":"식품 공장 폐수 처리, 노후 구도시 배관 부식, 혁신도시 신축 배관 오류"},
    "군산시": {"type":"산업공단","trait":"군산항 물류·조선·자동차 산업, 철새도래지 인근 관광 혼합","plumbing":"항만 염분 부식, 조선 산업 기름 찌꺼기, 관광지 음식점 배수"},
    "여수시": {"type":"관광특구","trait":"여수엑스포·돌산도 해양관광, 석유화학 국가산업단지 혼합","plumbing":"해양 염분 부식, 관광 성수기 배수 과부하, 화학 공장 특수 폐수"},
    "순천시": {"type":"신도시","trait":"순천만국가정원·생태도시 브랜드, 혁신도시 개발, 신흥 상권 성장","plumbing":"생태 친화 배수 요구, 신도시 배관 설계 오류, 관광 성수기 부하"},
    "목포시": {"type":"도심상권","trait":"목포항 물류, 남악신도시 인근, 다도해 관광 거점 도시","plumbing":"항만 염분 부식, 구도시 노후 배관 부식, 신도시 배수 용량 문제"},
    "제주시": {"type":"관광특구","trait":"제주공항·제주시 원도심 관광 상권, 이주민 급증, 숙박시설 밀집","plumbing":"관광지 숙박 배수 과부하, 화산암 지반 특수 배관, 이주민 신축 배관 오류"},
    "서귀포시": {"type":"관광특구","trait":"중문관광단지·성산일출봉 관광지, 외국인 관광객 연중 집중","plumbing":"리조트·호텔 대형 배수 부하, 염분 부식, 화산암 지반 배관 손상"},
    "춘천시": {"type":"대학가","trait":"강원대·한림대 캠퍼스 중심, 호반의 도시 관광, 레고랜드 개장","plumbing":"대학가 음식점 기름때, 호반 지형 지반 침수, 관광지 성수기 배수 부하"},
    "원주시": {"type":"신도시","trait":"기업도시·혁신도시 급성장, 강원도 최대 도시, 세브란스병원 이전","plumbing":"혁신도시 신축 배관 설계 오류, 의료시설 특수 배수, 지반 침하 손상"},
    "강릉시": {"type":"관광특구","trait":"경포대·오죽헌 해양관광, 스키시즌 관광객 집중, KTX 강릉선 개통","plumbing":"관광 성수기 배수 과부하, 해안 염분 부식, 스키리조트 대형 배수"},
    "천안시": {"type":"신도시","trait":"천안아산역 SRT 환승, 성성지구·두정동 신도시, 삼성·LG 생산기지","plumbing":"신도시 배수 설계 오류, 공장 배수 특수 처리, KTX 역세권 상업 배수"},
    "아산시": {"type":"산업공단","trait":"탕정·온양 삼성디스플레이·현대차 공장, 아산만 물류, 아산신도시","plumbing":"반도체 공장 초순수 배수, 항만 염분 부식, 신도시 배수 용량 부족"},
    "공주시": {"type":"관광특구","trait":"공산성·무령왕릉 백제문화 유산, 충남도청 인근, 공주대 캠퍼스","plumbing":"역사 문화재 인근 노후 배관, 대학가 상가 기름때, 문화재 보존 구역 제한 작업"},
    "보령시": {"type":"관광특구","trait":"대천해수욕장 머드축제 관광지, 화력발전소·LNG 터미널 산업 혼합","plumbing":"해안 염분 부식, 관광 성수기 숙박 배수 부하, 발전소 특수 냉각수 배관"},
}

# 시군구 지역 특성 기반 고유 콘텐츠 생성
def _sigungu_intro(name, sido):
    d = SIGUNGU_DATA.get(name) or SIGUNGU_DATA.get(name + "_" + sido[:2])
    if d:
        t = d["type"]
        trait = d["trait"]
        plumb = d["plumbing"]
        # 지역 유형별 p1 도입부 변형
        type_intros = {
            "도심상권": f"{name}은 {sido}의 핵심 상업·업무 지구입니다. {trait}.",
            "주거밀집": f"{name}은 {sido}의 주요 주거 밀집 지역입니다. {trait}.",
            "신도시": f"{name}은 {sido}에서 빠르게 성장 중인 신도시 지역입니다. {trait}.",
            "산업공단": f"{name}은 {sido}의 산업·공단 중심 지역입니다. {trait}.",
            "농어촌": f"{name}은 {sido}의 농어촌 지역으로, {trait}.",
            "관광특구": f"{name}은 {sido}의 대표적인 관광 특구입니다. {trait}.",
            "대학가": f"{name}은 {sido}의 대학가 밀집 지역입니다. {trait}.",
            "구도심": f"{name}은 {sido}의 역사 깊은 구도심 지역입니다. {trait}.",
        }
        p1 = type_intros.get(t, f"{name}은 {sido}에 속한 지역으로, {trait}.")
        p2 = f"{name} 일대에서 주로 접수되는 배관 문제는 {plumb} 등입니다. 현장 건물 형태와 사용 환경에 따라 원인이 달라지므로, 증상을 먼저 확인한 뒤 작업 방향을 정하는 것이 중요합니다."
    elif name.endswith("구"):
        p1 = f"{name}은 {sido}에 속한 자치구로, 아파트·오피스텔·빌라 같은 주거시설과 상가·사무실이 혼재한 지역입니다."
        p2 = f"{name} 일대는 식당·카페 등 상가와 주거가 섞여 있어 싱크대 배수 불량, 욕실·바닥 배수구 역류, 화장실 악취, 주방 기름때 막힘 등 현장마다 원인이 다양하게 나타납니다."
    elif name.endswith("군"):
        p1 = f"{name}은 {sido}의 군 지역으로, 주거지와 소규모 상권, 농어촌 시설이 어우러져 있습니다."
        p2 = f"{name}은 단독주택과 농어촌 시설이 많아 외부 오수관이나 정화조 연결부에서 비롯된 문제가 나타나기도 하며, 상가는 업종에 따라 배수 부담이 달라집니다."
    else:
        p1 = f"{name}은 {sido}의 시 지역으로, 아파트 단지와 상권, 사무·상업시설이 어우러진 곳입니다."
        p2 = f"{name}은 신축 아파트부터 노후 주택, 상가·사무실까지 건물 형태가 다양해 막힘의 원인도 제각각입니다. 가정집은 머리카락·음식물 찌꺼기가, 음식점은 기름 슬러지가 주요 원인이 되곤 합니다."
    p3 = f"스피드 배관공사는 {name} 현장의 건물 형태와 막힘 정도를 먼저 확인한 뒤 필요한 작업 방향을 안내드립니다. 단순 막힘인지 반복 막힘인지에 따라 장비와 작업 시간이 달라지므로, 무리한 자가 조치보다 전화 상담을 통해 원인을 먼저 파악하는 것이 안전합니다."
    return p1, p2, p3

def gen_sigungu_page(sido_ko, sido_slug, gu_ko, siblings):
    sido_url = f"/area/{sido_slug}/"
    crumbs = [("홈","/"),("지역별 서비스","/area/"),(sido_ko, sido_url),(gu_ko, None)]
    p1, p2, p3 = _sigungu_intro(gu_ko, sido_ko)
    fixt = vpick(gu_ko+"f", FIXTURE_V)
    insp = vpick(gu_ko+"i", INSPECT_V)
    sib_links = "".join(f'<a href="{gungu_url(sido_slug, g)}">{g}</a>' for g in siblings)
    _base = gungu_url(sido_slug, gu_ko)
    dong_links = "".join(f'<a href="{_base}{dong_slug(dn)}/">{dn}</a>' for dn in dongs_of(sido_slug, gu_ko)) \
                 or '<span>전 지역 상담 가능</span>'
    faq = [
        (f"{gu_ko} 하수구막힘은 바로 출동 가능한가요?",
         "지역과 시간대, 현장 상황에 따라 상담 후 안내됩니다. 증상과 사진을 먼저 보내주시면 필요한 장비를 더 정확히 판단할 수 있습니다."),
        (f"{gu_ko}에서 싱크대가 자주 막히면 어떻게 하나요?",
         "반복 막힘은 단순 이물질보다 배관 내부 기름때·퇴적물이 원인일 수 있습니다. 배관내시경으로 내부를 확인한 뒤 고압세척 여부를 판단하는 것이 좋습니다."),
        FAQ_CHEMICAL,
        (f"{gu_ko} 상가·음식점도 작업 가능한가요?",
         "상가, 음식점, 카페, 사무실 등 현장 구조에 따라 상담 가능합니다. 영업장 배관은 가정집보다 원인이 복잡할 수 있어 작업 전 확인이 중요합니다."),
    ]
    body = f"""{phero(f"{gu_ko} 배관공사", f"{gu_ko} 배관공사·하수구막힘 상담 | 스피드 배관공사", f"{sido_ko} {gu_ko}의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다.", crumbs)}
<main>
<section class="section">
  <div class="container layout-sidebar">
    <div class="prose">
      <nav class="anchor-nav" aria-label="{gu_ko} 배관공사 바로가기">
        <h2>{gu_ko} 배관공사 바로가기</h2>
        <ul>
          <li><a href="#intro">{gu_ko} 배관공사 안내</a></li>
          <li><a href="#symptom">하수구막힘 증상</a></li>
          <li><a href="#fixtures">싱크대·변기·욕실</a></li>
          <li><a href="#services">서비스 가능 항목</a></li>
          <li><a href="#work">작업 방식</a></li>
          <li><a href="#cost">비용 기준</a></li>
          <li><a href="#area">인접 시·군·구</a></li>
          <li><a href="#faq">자주 묻는 질문</a></li>
          <li><a href="#call">전화 상담</a></li>
        </ul>
      </nav>

      <h2 id="intro">{gu_ko} 배관공사 안내</h2>
      <p>{p1}</p>
      <p>{p2}</p>
      <p>{p3}</p>

      <h2 id="symptom">{gu_ko} 하수구막힘 증상</h2>
      <ul class="ticks">{SYMPTOM_LI}</ul>

      <h2 id="fixtures">{gu_ko} 싱크대·변기·욕실 배수구 문제</h2>
      <p>{FIXTURE_P}</p>

      <h2 id="services">{gu_ko} 서비스 가능 항목</h2>
      <ul class="ticks">{SERVICE_LI}</ul>

      <h2 id="work">{gu_ko} 작업 방식 안내</h2>
      <p>{gu_ko} 현장도 증상 확인과 사진·영상 상담을 먼저 진행한 뒤, 막힘 위치와 원인을 추정해 필요한 장비를 선택합니다. 작업 전 비용 기준을 안내드리고, 동의 후 막힘 제거 또는 배관 세척을 진행합니다.</p>
      <ol style="padding-left:20px;display:flex;flex-direction:column;gap:8px;">{WORK_LI}</ol>
      <p>{INSPECT_P}</p>

      <h2 id="prepare">{gu_ko} 자가 조치 시 주의사항</h2>
      <p>{SELFCARE_P}</p>

      <h2 id="cost">비용이 달라지는 기준</h2>
      <p>{gu_ko} 배관공사 비용은 현장 조건에 따라 달라집니다. 아래 항목에 따라 필요한 장비와 작업 시간이 달라질 수 있습니다.</p>
      <ul class="ticks">{COST_LI}</ul>
      <p class="price-note">{COST_NOTE}</p>

      <h2 id="dong">{gu_ko} 서비스 가능 지역(행정동)</h2>
      <p>{gu_ko} 전역으로 상담 가능합니다. 아래 동을 선택하면 해당 지역의 배관공사·하수구막힘 안내를 확인할 수 있습니다.</p>
      <div class="tag-list">{dong_links}</div>

      <h2 id="area">{sido_ko} 인접 시·군·구</h2>
      <p>{sido_ko}의 다른 시·군·구도 상담 가능합니다. 가까운 지역을 선택해 확인하세요.</p>
      <div class="tag-list">{sib_links}</div>

      <h2 id="faq">자주 묻는 질문</h2>
      <div class="faq-list">
{faq_html(faq)}      </div>

      <h2 id="call">{gu_ko} 전화 상담</h2>
      <p>{gu_ko}에서 하수구막힘이나 배관공사 상담이 필요하다면 증상, 위치, 건물 형태, 물이 내려가는 속도, 냄새 여부를 알려주세요. 현장 조건을 먼저 확인하고 필요한 작업 방향을 안내합니다.</p>
      <div class="local-cta">
        <a class="btn btn--primary btn--lg" href="tel:0000-0000">☎ 전화 상담하기</a>
        <a class="btn btn--secondary btn--lg" href="https://t.me/googleseolab" target="_blank" rel="noopener">사진 보내기</a>
        <a class="btn btn--secondary btn--lg" href="{sido_url}">{sido_ko} 전체 보기</a>
      </div>
    </div>
    {local_sidebar(f"{gu_ko} 배관 상담", f"{gu_ko} 및 {sido_ko} 인근 지역 상담 가능. 증상·사진을 보내주시면 더 정확합니다.")}
  </div>
</section>
</main>
"""
    page(f"area/{sido_slug}/{gungu_slug(gu_ko)}/index.html",
         f"{gu_ko} 배관공사·하수구막힘 | 싱크대·변기·배수구 막힘 상담 - 스피드 배관공사",
         f"{gu_ko} 하수구막힘·배관공사·누수탐지·고압세척 24시간 출동. 싱크대·변기·욕실 막힘 상담.",
         f"{S}/area/{sido_slug}/{gungu_slug(gu_ko)}/", body,
         jsonld=breadcrumb_jsonld(crumbs) + faq_jsonld(faq))

def gen_dong_page(sido_ko, sido_slug, gu_ko, gu_url, dong_ko, siblings, override_dir=None):
    _dir = override_dir or f"area/{sido_slug}/{gungu_slug(gu_ko)}"
    crumbs = [("홈","/"),("지역별 서비스","/area/"),(sido_ko, f"/area/{sido_slug}/")]
    if gu_ko != sido_ko:
        crumbs.append((gu_ko, gu_url))
    crumbs.append((dong_ko, None))
    _dgu = SIGUNGU_DATA.get(gu_ko)
    if dong_ko.endswith(("읍","면")):
        if _dgu:
            p1 = f"{dong_ko}은 {gu_ko}에 속한 읍·면 지역입니다. {gu_ko}는 {_dgu['trait']}이며, {dong_ko} 일대의 배관공사·하수구막힘 상담을 안내합니다."
        else:
            p1 = f"{dong_ko}은 {gu_ko}에 속한 지역으로, 주거지와 소규모 상권, 농어촌·단독주택이 어우러진 곳입니다. {dong_ko} 일대의 배관공사·하수구막힘 상담을 안내합니다."
        p2 = f"{dong_ko}은 단독주택과 다세대가 많아 외부 오수관이나 정화조 연결부에서 비롯된 문제가 나타나기도 하며, 상가는 업종에 따라 배수 부담이 달라집니다. 현장 구조를 먼저 확인하는 것이 중요합니다."
    else:
        if _dgu:
            p1 = f"{dong_ko}은 {gu_ko}의 행정동으로, {_dgu['trait']}인 지역 안에 위치합니다. {dong_ko} 일대의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다."
            p2 = f"{gu_ko} 일대에서 자주 접수되는 문제는 {_dgu['plumbing']} 등이며, {dong_ko}도 비슷한 유형의 배관 상담이 들어옵니다. 가정집은 머리카락·음식물·비누 찌꺼기가, 음식점은 기름 슬러지가 주요 원인이 되곤 합니다."
        else:
            p1 = f"{dong_ko}은 {gu_ko}에 속한 행정동으로, 아파트·주택과 상가가 어우러진 지역입니다. {dong_ko} 일대의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다."
            p2 = f"{dong_ko}은 주거와 상가가 섞여 있어 가정용·상업용 배관 상담이 함께 들어옵니다. 가정집은 머리카락·음식물·비누 찌꺼기가, 음식점은 기름 슬러지가 주요 원인이 되곤 합니다."
    p3 = vpick(dong_ko+"p", [
        f"스피드 배관공사는 {dong_ko}의 건물 형태와 막힘 정도를 먼저 확인한 뒤 필요한 작업 방향을 안내합니다. 단순 막힘인지 반복 막힘인지에 따라 장비와 작업 시간이 달라지므로, 무리한 자가 조치보다 상담을 통해 원인을 정확히 파악하는 것이 안전합니다.",
        f"{dong_ko} 현장은 건물과 사용 환경에 따라 막힘의 양상이 달라, 먼저 상태를 확인한 뒤 작업 방향을 정하는 것이 중요합니다. 반복 막힘이라면 단순 관통보다 내부 점검을 병행하는 편이 재발을 줄입니다.",
        f"스피드 배관공사는 {dong_ko}에서 증상과 현장 조건을 먼저 살핀 뒤 필요한 작업을 안내합니다. 막힘의 정도와 위치에 따라 장비·시간이 달라지므로, 무리한 자가 조치보다 상담으로 원인을 파악하는 것이 안전합니다.",
    ])
    fixt = vpick(dong_ko+"f", FIXTURE_V)
    insp = vpick(dong_ko+"i", INSPECT_V)
    selfc = vpick(dong_ko+"s", SELFCARE_V)
    wintro = vpick(dong_ko+"w", WORKINTRO_V)
    stail = vpick(dong_ko+"y", SYMPTOM_TAIL_V)
    sib_links = "".join(f'<a href="{gu_url}{dong_slug(d)}/">{d}</a>' for d in siblings) or '<span>전 지역 상담 가능</span>'
    faq = [
        (f"{dong_ko} 하수구막힘은 바로 출동 가능한가요?",
         vpick(dong_ko+"q1", [
            "지역과 시간대, 현장 상황에 따라 상담 후 안내됩니다. 증상과 사진을 먼저 보내주시면 필요한 장비를 더 정확히 판단할 수 있습니다.",
            "현장 위치와 시간대에 따라 달라지므로 먼저 상담을 받아보시는 것이 좋습니다. 증상과 사진을 보내주시면 더 빠르게 안내드릴 수 있습니다."])),
        (f"{dong_ko}에서 싱크대가 자주 막히면 어떻게 하나요?",
         vpick(dong_ko+"q2", [
            "반복 막힘은 단순 이물질보다 배관 내부 기름때·퇴적물이 원인일 수 있습니다. 배관내시경으로 내부를 확인한 뒤 고압세척 여부를 판단하는 것이 좋습니다.",
            "자주 막힌다면 내부에 기름때나 퇴적물이 쌓였을 가능성이 큽니다. 내시경으로 상태를 확인하고 필요하면 고압세척으로 관 벽까지 정리하는 것이 효과적입니다."])),
        FAQ_CHEMICAL,
    ]
    body = f"""{phero(f"{dong_ko} 배관공사", f"{dong_ko} 배관공사·하수구막힘 상담 | 스피드 배관공사", f"{gu_ko} {dong_ko}의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다.", crumbs)}
<main>
<section class="section">
  <div class="container layout-sidebar">
    <div class="prose">
      <h2 id="intro">{dong_ko} 배관공사 안내</h2>
      <p>{p1}</p>
      <p>{p2}</p>
      <p>{p3}</p>

      <h2 id="symptom">{dong_ko} 하수구막힘 증상</h2>
      <ul class="ticks">{SYMPTOM_LI}</ul>
      <p>{stail}</p>

      <h2 id="fixtures">{dong_ko} 싱크대·변기·욕실 배수구 문제</h2>
      <p>{fixt}</p>

      <h2 id="services">{dong_ko} 서비스 가능 항목</h2>
      <ul class="ticks">{SERVICE_LI}</ul>

      <h2 id="work">{dong_ko} 작업 방식 안내</h2>
      <p>{dong_ko} {wintro}</p>
      <ol style="padding-left:20px;display:flex;flex-direction:column;gap:8px;">{WORK_LI}</ol>
      <p>{insp}</p>

      <h2 id="prepare">{dong_ko} 자가 조치 시 주의사항</h2>
      <p>{selfc}</p>

      <h2 id="cost">비용이 달라지는 기준</h2>
      <p>{dong_ko} 배관공사 비용은 현장 조건에 따라 달라집니다. 아래 항목에 따라 필요한 장비와 작업 시간이 달라질 수 있습니다.</p>
      <ul class="ticks">{COST_LI}</ul>
      <p class="price-note">{COST_NOTE}</p>

      <h2 id="area">{gu_ko} 인근 지역</h2>
      <p>{gu_ko}의 다른 지역도 상담 가능합니다. 가까운 동을 선택해 확인하세요.</p>
      <div class="tag-list">{sib_links}</div>

      <h2 id="faq">자주 묻는 질문</h2>
      <div class="faq-list">
{faq_html(faq)}      </div>

      <h2 id="call">{dong_ko} 전화 상담</h2>
      <p>{dong_ko}에서 하수구막힘이나 배관공사 상담이 필요하다면 증상, 위치, 건물 형태, 물이 내려가는 속도, 냄새 여부를 알려주세요. 현장 조건을 먼저 확인하고 필요한 작업 방향을 안내합니다.</p>
      <div class="local-cta">
        <a class="btn btn--primary btn--lg" href="tel:0000-0000">☎ 전화 상담하기</a>
        <a class="btn btn--secondary btn--lg" href="https://t.me/googleseolab" target="_blank" rel="noopener">사진 보내기</a>
        <a class="btn btn--secondary btn--lg" href="{gu_url}">{gu_ko} 전체 보기</a>
      </div>
    </div>
    {local_sidebar(f"{dong_ko} 배관 상담", f"{dong_ko} 및 {gu_ko} 인근 지역 상담 가능. 증상·사진을 보내주시면 더 정확합니다.")}
  </div>
</section>
</main>
"""
    page(f"{_dir}/{dong_slug(dong_ko)}/index.html",
         f"{dong_ko} 배관공사·하수구막힘 | 싱크대·변기·배수구 막힘 상담 - 스피드 배관공사",
         f"{gu_ko} {dong_ko} 하수구막힘·배관공사·누수탐지·고압세척 24시간 출동. 싱크대·변기·욕실 막힘 상담.",
         f"{S}/{_dir}/{dong_slug(dong_ko)}/", body,
         jsonld=breadcrumb_jsonld(crumbs) + faq_jsonld(faq))

_cnt = 0; _dcnt = 0
for _sido_ko, _gus in OFFICIAL.items():
    _ss = sido_slug_of(_sido_ko)
    for _gu in _gus:
        if (_ss, _gu) not in CUSTOM_GUNGU_URL:
            sibs = [g for g in _gus if g != _gu]
            gen_sigungu_page(_sido_ko, _ss, _gu, sibs)
            _cnt += 1
        # 행정동 자동 생성 (이미 상세가 있는 시군구는 제외)
        if (_ss, _gu) in SKIP_DONG:
            continue
        _gu_url = gungu_url(_ss, _gu)
        _dongs = dongs_of(_ss, _gu)
        for _dn in _dongs:
            _sib = [x for x in _dongs if x != _dn]
            gen_dong_page(_sido_ko, _ss, _gu, _gu_url, _dn, _sib)
            _dcnt += 1
# 세종특별자치시: 시군구 없이 행정동을 시도 하위에 직접 생성
_sejong = DONG_DATA.get("sejong", {}).get("__SEJONG__", [])
for _dn in _sejong:
    _sib = [x for x in _sejong if x != _dn]
    gen_dong_page("세종특별자치시","sejong","세종특별자치시","/area/sejong/", _dn, _sib,
                  override_dir="area/sejong")
    _dcnt += 1
print(f"\\n전국 시·군·구 자동 생성: {_cnt}개 / 행정동 자동 생성: {_dcnt}개")


# ===========================================================================
# 서울 강동구·마포구·영등포구 — 구+행정동 상세 (메뉴 사양서 명시 구)
# ===========================================================================
GANGDONG_DONGS = [
 ("천호동","cheonho",
  "천호동은 천호역 로데오 상권과 대형 상가, 아파트가 밀집한 강동구의 중심 지역입니다. 음식점·상가와 주거가 함께 있어 상업용·가정용 배관 상담이 고루 들어옵니다.",
  "로데오 상권의 음식점은 주방 기름때로 인한 막힘이 잦고, 상가 건물은 화장실·바닥 배수구 역류 상담이 자주 발생합니다. 영업 시간을 고려한 무중단 작업이 중요합니다.",
  "천호동에서는 음식점 주방 하수구막힘과 상가 화장실 배수구 역류, 아파트 욕실 배수 지연 상담이 많습니다. 반복 막힘은 고압세척으로 배관 내부를 세척해야 재발을 줄일 수 있습니다.",
  [("성내동","seongnae"),("길동","gil"),("암사동","amsa")]),
 ("성내동","seongnae",
  "성내동은 강동구청이 자리한 행정 중심으로, 아파트와 상가, 사무시설이 어우러진 지역입니다. 생활 배관과 상가 배관 상담이 함께 들어옵니다.",
  "주거 단지는 생활 이물질로 인한 막힘이 주를 이루고, 상가·사무시설은 화장실 배수 부담이 큰 편입니다. 노후 건물은 배관 구배 문제로 반복 막힘이 나타나기도 합니다.",
  "성내동에서는 아파트 욕실·싱크대막힘과 상가 화장실 배수구 막힘, 세면대막힘 상담이 많습니다. 반복 증상은 배관 내부 상태 확인 후 세척 여부를 판단합니다.",
  [("천호동","cheonho"),("길동","gil"),("둔촌동","dunchon")]),
 ("길동","gil",
  "길동은 굽은다리 일대 주거와 상가가 어우러진 지역으로, 빌라·다세대와 근린 상가가 많습니다. 생활 배관과 소규모 상가 배관 상담이 들어옵니다.",
  "다세대·빌라는 공용 배수관에 부담이 큰 편이라 한 세대의 막힘이 다른 세대에 영향을 주기도 합니다. 상가는 업종에 따라 배수 부담이 다릅니다.",
  "길동에서는 빌라 화장실 배수 지연·악취와 싱크대막힘, 상가 배수구 막힘 상담이 많습니다. 여러 세대 동시 증상은 공용관 점검이 우선입니다.",
  [("천호동","cheonho"),("성내동","seongnae"),("암사동","amsa")]),
 ("둔촌동","dunchon",
  "둔촌동은 대규모 재건축으로 신축 아파트 단지가 들어선 지역으로, 새 건물 비중이 높습니다. 입주 초기 배관 점검 수요가 특히 많습니다.",
  "신축 아파트는 시공 마감이나 입주 초기 이물질로 인한 배수 지연이 나타날 수 있습니다. 새 건물이라도 구배 불량이나 시공 문제로 막힘이 생길 수 있어 점검이 유효합니다.",
  "둔촌동에서는 신축 아파트 배수 점검과 싱크대·욕실 배수 지연, 바닥 배수구 역류 상담이 많습니다. 입주 초기 반복 증상은 배관내시경으로 시공 상태를 확인하면 관리가 수월합니다.",
  [("성내동","seongnae"),("명일동","myeongil"),("길동","gil")]),
 ("암사동","amsa",
  "암사동은 선사유적지 인근의 아파트와 빌라가 어우러진 주거 중심 지역입니다. 생활 배관 상담이 주를 이루며 근린 상가 배관 상담도 함께 들어옵니다.",
  "준공 연차가 있는 아파트·빌라는 배수 지연이나 악취 상담이 잦고, 단독·다세대는 노후 배관 문제가 나타나기도 합니다. 생활 배관은 머리카락·음식물·비누 찌꺼기가 주요 원인입니다.",
  "암사동에서는 아파트·빌라 욕실 배수 느림과 싱크대막힘, 바닥 배수구 역류 상담이 많습니다. 반복 막힘은 내부 상태 확인 후 세척 여부를 판단하는 것이 좋습니다.",
  [("천호동","cheonho"),("길동","gil"),("고덕동","godeok")]),
 ("명일동","myeongil",
  "명일동은 학원가와 대단지 아파트가 어우러진 주거 지역으로, 가족 단위 주거와 학원·상가가 함께 있습니다. 생활 배관과 상가 배관 상담이 들어옵니다.",
  "대단지 아파트는 준공 연차에 따라 욕실·주방 배수 지연이 나타나고, 학원·상가 건물은 화장실 사용 빈도가 높아 배수구 막힘이 반복되기도 합니다.",
  "명일동에서는 아파트 욕실 배수 느림과 싱크대·세면대막힘, 학원 상가 화장실 배수구 막힘 상담이 많습니다. 반복 증상은 내시경 확인 후 고압세척 여부를 판단합니다.",
  [("둔촌동","dunchon"),("고덕동","godeok"),("암사동","amsa")]),
 ("고덕동","godeok",
  "고덕동은 고덕신도시 개발로 신축 아파트 단지가 밀집한 지역입니다. 새 건물이 많아 입주 초기 배관 점검 수요가 꾸준히 들어옵니다.",
  "신축 아파트는 입주 초기 이물질이나 시공 마감으로 인한 배수 지연이 나타날 수 있습니다. 근린 상가는 업종에 따라 배수 부담이 달라 현장별 확인이 필요합니다.",
  "고덕동에서는 신축 아파트 배수 점검과 욕실·싱크대 배수 지연, 상가 배수구 막힘 상담이 많습니다. 초기 반복 막힘은 배관내시경으로 시공 상태를 확인하는 것이 좋습니다.",
  [("명일동","myeongil"),("상일동","sangil"),("암사동","amsa")]),
 ("상일동","sangil",
  "상일동은 고덕비즈밸리와 신축 아파트가 어우러진 지역으로, 업무시설과 신축 주거가 함께 조성되고 있습니다. 시설 배관과 생활 배관 상담이 들어옵니다.",
  "신축 아파트는 초기 점검 위주, 업무·상업 시설은 사용량에 따른 배수 부담이 있습니다. 새 건물이라도 시공·구배 문제로 막힘이 생길 수 있어 점검이 유효합니다.",
  "상일동에서는 신축 아파트 배수 점검과 시설 화장실 배수구 막힘, 싱크대 배수 지연 상담이 많습니다. 반복 증상은 내시경 확인 후 작업 방향을 정합니다.",
  [("고덕동","godeok"),("강일동","gangil"),("명일동","myeongil")]),
 ("강일동","gangil",
  "강일동은 강일지구 신축 아파트가 중심인 주거 지역으로, 단지와 근린 상가가 함께 조성되어 있습니다. 생활 배관과 근린 상가 배관 상담이 주로 들어옵니다.",
  "신축 단지는 입주 초기 배수 지연이나 이물질 막힘이 나타날 수 있고, 근린 상가는 식당·카페 업종에서 주방 배관 막힘이 발생하기도 합니다.",
  "강일동에서는 아파트 욕실·싱크대막힘과 근린 상가 주방 하수구막힘, 배수구 역류 상담이 많습니다. 초기 반복 막힘은 내시경 확인 후 작업 방향을 정하는 것을 권합니다.",
  [("상일동","sangil"),("고덕동","godeok"),("명일동","myeongil")]),
]
build_gu_system("서울특별시","seoul","/area/seoul/","강동구","gangdong",
    "천호 상권과 둔촌·고덕 신축 아파트, 암사 주거지까지 — 강동구 전역의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다.",
    ["강동구는 천호역 상권과 둔촌·고덕·강일 신축 아파트 단지, 암사·길동 주거지가 어우러진 지역입니다. 신축과 기존 주거, 상권이 섞여 있어 배관 문제의 원인이 현장마다 다양합니다.",
     "특히 천호동, 성내동, 둔촌동, 고덕동 일대는 상가와 대단지 아파트가 함께 있어 싱크대 배수 불량, 바닥 배수구 역류, 화장실 악취, 주방 기름때 막힘 상담이 자주 발생합니다.",
     "스피드 배관공사는 현장의 건물 형태와 막힘 정도를 먼저 확인한 뒤 필요한 작업 방향을 안내합니다. 단순 막힘인지 반복 막힘인지에 따라 장비와 작업 시간이 달라지므로, 무리한 자가 조치보다 상담을 통해 원인을 정확히 파악하는 것이 안전합니다."],
    "", GANGDONG_DONGS,
    [("송파구","/area/seoul/songpa-gu/"),("강남구","/area/seoul/gangnam-gu/"),("광진구","/area/seoul/gwangjin-gu/"),("하남시","/area/gyeonggi/")])

MAPO_DONGS = [
 ("공덕동","gongdeok",
  "공덕동은 공덕역 일대 오피스빌딩과 상권이 밀집한 마포의 업무 중심 지역입니다. 사무시설과 식당가가 함께 있어 상업용·업무용 배관 상담이 주로 들어옵니다.",
  "오피스빌딩은 화장실·탕비실 배수 사용량이 많고, 상권의 식당은 주방 기름때로 인한 막힘이 잦습니다. 업무에 지장이 없도록 시간대를 조율한 작업이 중요합니다.",
  "공덕동에서는 오피스 탕비실 싱크대막힘과 상가 화장실 배수구 역류, 식당 주방 하수구막힘 상담이 많습니다. 반복 막힘은 내시경 확인 후 고압세척 여부를 판단합니다.",
  [("아현동","ahyeon"),("도화동","dohwa"),("용강동","yonggang")]),
 ("아현동","ahyeon",
  "아현동은 재개발로 신축 아파트와 기존 주택이 혼재한 지역입니다. 신축 단지의 초기 점검과 기존 주거의 노후 배관 상담이 함께 들어옵니다.",
  "신축 아파트는 입주 초기 이물질로 인한 배수 지연이, 기존 주택은 노후·구배 문제로 인한 막힘이 나타납니다. 신축은 점검 위주, 노후는 원인 제거 위주로 접근이 다릅니다.",
  "아현동에서는 신축 아파트 배수 점검과 기존 주택 욕실·싱크대막힘, 바닥 배수구 역류 상담이 많습니다. 초기 반복 막힘은 내시경 확인이 도움이 됩니다.",
  [("공덕동","gongdeok"),("대흥동","daeheung"),("염리동","yeomni")]),
 ("도화동","dohwa",
  "도화동은 마포역 인근의 주거와 오피스가 어우러진 지역으로, 아파트 단지와 사무시설이 함께 있습니다. 생활 배관과 업무용 배관 상담이 고루 들어옵니다.",
  "주거 단지는 생활 이물질로 인한 막힘이 주를 이루고, 오피스는 화장실·탕비실 배수 부담이 있습니다. 준공 연차가 있는 건물은 배수 지연 상담이 잦습니다.",
  "도화동에서는 아파트 욕실·싱크대막힘과 오피스 화장실 배수구 막힘, 세면대막힘 상담이 많습니다. 반복 증상은 내부 상태 확인 후 세척 여부를 판단합니다.",
  [("공덕동","gongdeok"),("용강동","yonggang"),("대흥동","daeheung")]),
 ("용강동","yonggang",
  "용강동은 마포 먹자골목과 주택가가 어우러진 지역으로, 음식점과 주거가 함께 있습니다. 영업장 주방 배관과 생활 배관 상담이 들어옵니다.",
  "먹자골목 음식점은 기름 슬러지로 인한 배관 막힘이 잦고, 주거지는 생활 배관 막힘이 주를 이룹니다. 영업 시간을 고려한 작업 일정 조율이 중요합니다.",
  "용강동에서는 음식점 주방 하수구막힘과 상가 바닥 배수구 역류, 주택 싱크대막힘 상담이 많습니다. 반복 막힘은 고압세척으로 내부를 세척하는 것이 효과적입니다.",
  [("도화동","dohwa"),("대흥동","daeheung"),("공덕동","gongdeok")]),
 ("대흥동","daeheung",
  "대흥동은 대학가 인근의 주거 지역으로, 다세대·원룸과 근린 상가가 많습니다. 생활 배관과 다세대 공용관 상담이 주로 들어옵니다.",
  "다세대·원룸은 공용 배수관에 부담이 큰 편이라 한 세대의 막힘이 다른 세대에 영향을 주기도 합니다. 카페·식당 상가는 주방 배관 막힘이 나타나기도 합니다.",
  "대흥동에서는 다세대 화장실 배수 지연과 싱크대막힘, 공용관 역류 상담이 많습니다. 여러 세대 동시 증상은 공용관 점검이 우선입니다.",
  [("아현동","ahyeon"),("염리동","yeomni"),("신수동","sinsu")]),
 ("염리동","yeomni",
  "염리동은 소금길로 알려진 주택가 중심 지역으로, 단독·다세대 주택이 많습니다. 노후 주택 배관과 생활 배관 상담이 주로 들어옵니다.",
  "오래된 단독·다세대는 배관 노후나 구배 문제로 막힘이 잦고, 외부 오수관 관련 증상이 나타나기도 합니다. 현장 구조를 먼저 확인하는 것이 중요합니다.",
  "염리동에서는 주택 욕실 배수 지연·악취와 싱크대막힘, 외부 오수관 막힘 상담이 많습니다. 외부 배관 관련 증상은 현장을 먼저 확인한 뒤 작업 방식을 안내드립니다.",
  [("대흥동","daeheung"),("아현동","ahyeon"),("신수동","sinsu")]),
 ("신수동","sinsu",
  "신수동은 서강대 인근의 주거와 상가가 어우러진 지역으로, 다세대 주택과 카페·식당이 함께 있습니다. 생활 배관과 상가 배관 상담이 들어옵니다.",
  "대학가 상권의 카페·음식점은 주방·음료 찌꺼기로 인한 막힘이 잦고, 다세대 주거는 공용관 부담이 있습니다. 현장별로 원인이 달라 작업 전 확인이 중요합니다.",
  "신수동에서는 카페·음식점 싱크대막힘과 다세대 화장실 배수 지연, 바닥 배수구 역류 상담이 많습니다. 반복 막힘은 내시경 확인 후 세척 여부를 판단합니다.",
  [("대흥동","daeheung"),("서교동","seogyo"),("염리동","yeomni")]),
 ("합정동","hapjeong",
  "합정동은 카페·상권과 출판·문화시설이 어우러진 지역으로, 상업시설 비중이 높습니다. 카페·음식점 주방 배관 상담이 특히 많이 들어옵니다.",
  "카페·음료 매장은 우유·시럽·커피 찌꺼기가 배관에 엉기는 경우가 있고, 지하 매장은 바닥 배수구 역류 상담이 잦습니다. 매장 영업 시간을 고려한 작업이 중요합니다.",
  "합정동에서는 카페·음식점 싱크대막힘과 지하 상가 바닥 배수구 역류, 화장실 배수 불량 상담이 많습니다. 매장의 반복 막힘은 고압세척이 효과적입니다.",
  [("서교동","seogyo"),("망원동","mangwon"),("연남동","yeonnam")]),
 ("망원동","mangwon",
  "망원동은 망리단길 카페골목과 망원시장이 어우러진 지역으로, 카페·음식점과 전통시장 상권이 함께 있습니다. 영업장 주방 배관 상담이 많이 들어옵니다.",
  "카페골목과 시장의 식당은 기름때·음식물 슬러지로 인한 막힘이 잦고, 시장 상가는 대량 배수 부담이 있습니다. 영업에 지장이 없도록 작업 시간 조율이 중요합니다.",
  "망원동에서는 카페·음식점 주방 하수구막힘과 시장 상가 배수구 역류, 싱크대막힘 상담이 많습니다. 반복 막힘은 고압세척으로 배관 내부를 세척해야 재발을 줄일 수 있습니다.",
  [("합정동","hapjeong"),("연남동","yeonnam"),("성산동","seongsan")]),
 ("연남동","yeonnam",
  "연남동은 연트럴파크를 중심으로 한 카페골목 상권 지역으로, 카페·음식점이 밀집해 있습니다. 영업장 주방 배관 상담이 특히 많이 들어옵니다.",
  "카페·디저트 매장은 음료·시럽 찌꺼기가 배관에 엉기기 쉽고, 음식점은 기름 슬러지로 인한 막힘이 잦습니다. 인테리어가 중요한 매장이 많아 작업 시 현장 보양이 중요합니다.",
  "연남동에서는 카페 싱크대막힘과 음식점 주방 하수구막힘, 바닥 배수구 역류 상담이 많습니다. 반복 막힘은 배관내시경 확인 후 고압세척으로 근본 해결하는 것이 좋습니다.",
  [("망원동","mangwon"),("서교동","seogyo"),("성산동","seongsan")]),
 ("성산동","seongsan",
  "성산동은 월드컵경기장 인근의 아파트와 주거가 어우러진 지역입니다. 생활 배관 상담이 주를 이루며 근린 상가 배관 상담도 함께 들어옵니다.",
  "아파트는 준공 연차에 따라 배수 지연이 나타나고, 주택·다세대는 생활 이물질로 인한 막힘이 잦습니다. 근린 상가는 업종에 따라 배수 부담이 다릅니다.",
  "성산동에서는 아파트 욕실 배수 느림과 싱크대·세면대막힘, 상가 화장실 배수구 막힘 상담이 많습니다. 반복 증상은 내부 상태 확인 후 세척 여부를 판단합니다.",
  [("망원동","mangwon"),("상암동","sangam"),("연남동","yeonnam")]),
 ("상암동","sangam",
  "상암동은 디지털미디어시티(DMC)의 방송·미디어 오피스단지가 자리한 지역입니다. 대형 업무시설과 신축 아파트가 함께 있어 시설 배관 상담이 많이 들어옵니다.",
  "대형 오피스는 화장실과 식당가 사용량이 많아 배수 부담이 크고, 지하 배관의 퇴적물이 문제가 되곤 합니다. 시설 운영에 지장이 없도록 시간대 조율이 필요합니다.",
  "상암동에서는 오피스 화장실 배수구 막힘과 구내식당 주방 하수구막힘, 아파트 배수 지연 상담이 많습니다. 사용량이 많은 시설은 정기 점검과 고압세척이 도움이 됩니다.",
  [("성산동","seongsan"),("망원동","mangwon"),("연남동","yeonnam")]),
 ("서교동","seogyo",
  "서교동은 홍대 상권의 중심으로, 음식점·주점·클럽과 카페가 빼곡한 지역입니다. 영업장 주방·지하 배관 상담이 특히 많이 들어옵니다.",
  "유흥·외식 상권은 기름 슬러지와 음식물로 인한 막힘이 매우 잦고, 지하 매장은 바닥 배수구 역류가 자주 발생합니다. 야간 영업이 많아 작업 시간 조율이 중요합니다.",
  "서교동에서는 음식점 주방 하수구막힘과 지하 상가 바닥 배수구 역류, 화장실 배수 불량 상담이 많습니다. 반복 막힘은 고압세척으로 배관 내부를 세척하는 것이 효과적입니다.",
  [("합정동","hapjeong"),("신수동","sinsu"),("연남동","yeonnam")]),
]
build_gu_system("서울특별시","seoul","/area/seoul/","마포구","mapo",
    "공덕 오피스와 홍대·합정·연남 카페 상권, 상암 DMC까지 — 마포구 전역의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다.",
    ["마포구는 공덕 오피스 상권과 홍대·합정·연남·망원의 카페·외식 상권, 상암 DMC 업무단지, 아현·도화 주거지가 어우러진 지역입니다. 상업시설 비중이 높아 영업장 배관 상담이 특히 많습니다.",
     "특히 서교동, 합정동, 연남동, 망원동 일대는 카페·음식점이 밀집해 주방 기름때 막힘과 바닥 배수구 역류 상담이 자주 발생하고, 상암·공덕은 대형 오피스 배관 수요가 많습니다.",
     "스피드 배관공사는 현장의 건물 형태와 사용 환경을 먼저 확인한 뒤 필요한 작업 방향을 안내합니다. 영업장의 반복 막힘은 배관내시경과 고압세척으로 근본 원인을 해결하는 것이 좋습니다."],
    "", MAPO_DONGS,
    [("영등포구","/area/seoul/yeongdeungpo-gu/"),("서대문구","/area/seoul/seodaemun-gu/"),("용산구","/area/seoul/yongsan-gu/"),("은평구","/area/seoul/eunpyeong-gu/")])

YEONGDEUNGPO_DONGS = [
 ("영등포동","yeongdeungpo",
  "영등포동은 영등포역과 전통시장, 대형 상권이 밀집한 지역으로, 시장 상가와 음식점이 많습니다. 시장·상가의 대량 배수 상담이 특징적입니다.",
  "전통시장과 식당가는 물·음식물 사용량이 많아 바닥 배수구 역류와 오수관 막힘이 잦습니다. 노후 상가 건물은 배관 구배 문제로 반복 막힘이 나타나기도 합니다.",
  "영등포동에서는 시장·상가 대량 배수관 막힘과 음식점 주방 하수구막힘, 화장실 배수구 역류 상담이 많습니다. 대량 배수 현장은 내시경 점검과 정기 세척이 효과적입니다.",
  [("당산동","dangsan"),("문래동","mullae"),("신길동","singil")]),
 ("여의도동","yeouido",
  "여의도동은 금융 오피스와 국회·방송사가 자리한 업무 중심 지역입니다. 대형 오피스빌딩이 밀집해 시설 배관 상담이 많이 들어옵니다.",
  "대형 오피스는 화장실과 구내식당 사용량이 많아 배수 부담이 크고, 지하 메인 배관의 퇴적물이 문제가 되곤 합니다. 업무에 지장이 없도록 시간대 조율이 필요합니다.",
  "여의도동에서는 오피스 화장실 배수구 막힘과 구내식당 주방 하수구막힘, 지하 배관 상담이 많습니다. 사용량이 많은 시설은 정기적인 배관내시경 점검과 고압세척이 유리합니다.",
  [("당산동","dangsan"),("영등포동","yeongdeungpo"),("양평동","yangpyeong")]),
 ("당산동","dangsan",
  "당산동은 당산역 인근의 주거와 오피스가 어우러진 지역으로, 아파트 단지와 사무시설이 함께 있습니다. 생활 배관과 업무용 배관 상담이 고루 들어옵니다.",
  "주거 단지는 생활 이물질로 인한 막힘이 주를 이루고, 오피스는 화장실·탕비실 배수 부담이 있습니다. 준공 연차가 있는 건물은 배수 지연 상담이 잦습니다.",
  "당산동에서는 아파트 욕실·싱크대막힘과 오피스 화장실 배수구 막힘, 세면대막힘 상담이 많습니다. 반복 증상은 내부 상태 확인 후 세척 여부를 판단합니다.",
  [("영등포동","yeongdeungpo"),("문래동","mullae"),("양평동","yangpyeong")]),
 ("도림동","dorim",
  "도림동은 다세대·주택이 밀집한 주거 중심 지역으로, 생활 배관 상담이 주를 이룹니다. 근린 상가의 배관 상담도 함께 들어옵니다.",
  "다세대·빌라는 공용 배수관 부담이 크고, 오래된 주택은 배관 노후나 구배 문제로 막힘이 잦습니다. 생활 배관은 머리카락·음식물·비누 찌꺼기가 주요 원인입니다.",
  "도림동에서는 다세대 화장실 배수 지연과 싱크대막힘, 공용관 역류 상담이 많습니다. 여러 세대 동시 증상은 공용관 점검이 우선입니다.",
  [("신길동","singil"),("문래동","mullae"),("대림동","daerim")]),
 ("문래동","mullae",
  "문래동은 문래창작촌의 철공소·공방과 카페·갤러리가 어우러진 독특한 지역입니다. 소규모 공장·작업장과 카페 상권 배관 상담이 함께 들어옵니다.",
  "철공소·작업장은 오래된 건물의 배관 노후 문제가, 카페·음식점은 주방 기름때·음료 찌꺼기로 인한 막힘이 나타납니다. 현장 유형이 다양해 작업 전 확인이 중요합니다.",
  "문래동에서는 카페·음식점 싱크대막힘과 작업장 노후 배관 막힘, 바닥 배수구 역류 상담이 많습니다. 반복 막힘은 내시경 확인 후 세척·보수 방향을 정합니다.",
  [("영등포동","yeongdeungpo"),("당산동","dangsan"),("양평동","yangpyeong")]),
 ("양평동","yangpyeong",
  "양평동은 준공업지역과 아파트, 물류시설이 어우러진 지역입니다. 공장·물류 시설 배관과 주거 배관 상담이 함께 들어옵니다.",
  "준공업 시설은 사용량이 많아 대형 배관 부담이 크고, 아파트는 생활 배관 막힘이 주를 이룹니다. 노후 시설은 배관 부식·구배 문제 상담이 나타나기도 합니다.",
  "양평동에서는 공장·물류 시설 배수관 막힘과 아파트 욕실·싱크대막힘, 바닥 배수구 역류 상담이 많습니다. 대형 배관은 정기 고압세척과 내시경 점검이 효과적입니다.",
  [("당산동","dangsan"),("문래동","mullae"),("여의도동","yeouido")]),
 ("신길동","singil",
  "신길동은 재개발로 신축 아파트와 기존 주택이 혼재한 지역입니다. 신축 단지의 초기 점검과 기존 주거의 노후 배관 상담이 함께 들어옵니다.",
  "신축 아파트는 입주 초기 이물질로 인한 배수 지연이, 기존 주택은 노후·구배 문제로 인한 막힘이 나타납니다. 신축은 점검 위주, 노후는 원인 제거 위주로 접근이 다릅니다.",
  "신길동에서는 신축 아파트 배수 점검과 기존 주택 욕실·싱크대막힘, 바닥 배수구 역류 상담이 많습니다. 초기 반복 막힘은 내시경 확인이 도움이 됩니다.",
  [("도림동","dorim"),("대림동","daerim"),("영등포동","yeongdeungpo")]),
 ("대림동","daerim",
  "대림동은 대림 상권과 다세대 주택이 밀집한 지역으로, 음식점과 주거가 함께 있습니다. 영업장 주방 배관과 다세대 공용관 상담이 들어옵니다.",
  "상권의 음식점은 기름 슬러지로 인한 막힘이 잦고, 다세대 주택은 공용 배수관 부담이 큽니다. 오래된 건물은 배관 노후 상담이 함께 들어옵니다.",
  "대림동에서는 음식점 주방 하수구막힘과 다세대 화장실 배수 지연, 공용관 역류 상담이 많습니다. 반복 막힘은 고압세척과 공용관 점검으로 대응하는 것이 효과적입니다.",
  [("도림동","dorim"),("신길동","singil"),("영등포동","yeongdeungpo")]),
]
build_gu_system("서울특별시","seoul","/area/seoul/","영등포구","yeongdeungpo",
    "여의도 금융단지와 영등포 상권, 문래·양평 준공업까지 — 영등포구 전역의 배관공사, 하수구막힘, 싱크대·변기·욕실 배수구 막힘 상담을 안내합니다.",
    ["영등포구는 여의도 금융 오피스단지와 영등포역 전통시장 상권, 문래창작촌, 양평 준공업지역, 신길·대림 주거지가 어우러진 지역입니다. 업무·상업·공업·주거가 모두 섞여 있어 배관 문제의 원인이 매우 다양합니다.",
     "특히 영등포동, 대림동 일대는 시장과 음식점이 밀집해 대량 배수와 주방 기름때 막힘 상담이 잦고, 여의도는 대형 오피스 배관, 양평·문래는 공장·작업장 배관 수요가 많습니다.",
     "스피드 배관공사는 현장의 건물 형태와 사용 환경을 먼저 확인한 뒤 필요한 작업 방향을 안내합니다. 사용량이 많은 시설과 영업장은 정기 점검과 고압세척으로 막힘을 예방하는 것이 유리합니다."],
    "", YEONGDEUNGPO_DONGS,
    [("마포구","/area/seoul/mapo-gu/"),("동작구","/area/seoul/dongjak-gu/"),("구로구","/area/seoul/guro-gu/"),("양천구","/area/seoul/yangcheon-gu/")])

print("\\n강동·마포·영등포 구+행정동 생성 완료.")
