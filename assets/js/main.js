/* 스피드 배관공사 — 경량 인터랙션 (vanilla JS)
   콘텐츠는 모두 HTML에 렌더링되어 있으며, JS는 보조 동작만 담당합니다. */
(function () {
  "use strict";

  /* ---------- 1. 스크롤 시 헤더 흰색 전환 ---------- */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () {
      if (window.scrollY > 24) header.classList.add("is-scrolled");
      else header.classList.remove("is-scrolled");
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- 2. 모바일 메뉴 토글 ---------- */
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- 3. 모바일 서브메뉴 펼침 ---------- */
  document.querySelectorAll(".gnb .has-sub > .gnb-link").forEach(function (link) {
    link.addEventListener("click", function (e) {
      // 데스크탑(hover)에서는 막지 않음 — 모바일 폭에서만 토글
      if (window.matchMedia("(max-width:1024px)").matches) {
        e.preventDefault();
        link.parentElement.classList.toggle("is-expanded");
      }
    });
  });

  /* ---------- 4. FAQ 아코디언 ---------- */
  document.querySelectorAll(".faq-q").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.closest(".faq-item");
      var open = item.classList.toggle("is-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  /* ---------- 5. 메뉴 링크 클릭 시 모바일 메뉴 닫기 ---------- */
  document.querySelectorAll(".gnb a:not(.has-sub > .gnb-link)").forEach(function (a) {
    a.addEventListener("click", function () {
      document.body.classList.remove("nav-open");
      if (toggle) toggle.setAttribute("aria-expanded", "false");
    });
  });

  /* ---------- 6. 견적 폼 (데모: 실제 전송 없이 안내) ---------- */
  var form = document.querySelector("form[data-quote-form]");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var msg = form.querySelector(".form-status");
      if (msg) {
        msg.hidden = false;
        msg.textContent = "상담 신청이 접수되었습니다. 빠르게 연락드리겠습니다. (데모 폼)";
      }
      form.reset();
    });
  }

  /* ---------- 7. 스크롤 등장 애니메이션 (프리미엄 스킨) ---------- */
  // JS·IntersectionObserver 지원 시에만 숨겼다가 등장. 미지원 시 항상 보임(SEO/접근성 안전).
  if ("IntersectionObserver" in window &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var sel = ".section-head, .trust-card, .service-card, .case-card, .review-card," +
              ".channel-card, .step, .faq-item, .link-card, .price-table-wrap, .cta-banner, .sidebar-card";
    var items = [].slice.call(document.querySelectorAll(sel));
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); obs.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    items.forEach(function (el, i) {
      el.classList.add("reveal");
      el.style.transitionDelay = (Math.min(i % 4, 3) * 60) + "ms";
      io.observe(el);
    });
  }

  /* ---------- 8. 광고주 모집 팝업 (SEO 안전: 지연·빈도제한·쉬운 닫기) ---------- */
  var pop = document.getElementById("adPopup");
  if (pop) {
    var DKEY = "adpop_hide_until";          // '오늘 하루' 해제 만료시각
    var SKEY = "adpop_seen_session";        // 이번 세션에서 이미 본 적 있음
    var hideUntil = parseInt(localStorage.getItem(DKEY) || "0", 10);
    var seen = sessionStorage.getItem(SKEY) === "1";
    var openPop = function () {
      pop.hidden = false;
      requestAnimationFrame(function () { pop.classList.add("open"); });
      document.addEventListener("keydown", onEsc);
    };
    var closePop = function () {
      pop.classList.remove("open");
      document.removeEventListener("keydown", onEsc);
      setTimeout(function () { pop.hidden = true; }, 320);
      sessionStorage.setItem(SKEY, "1");   // 세션 내 재노출 방지
    };
    var onEsc = function (e) { if (e.key === "Escape") closePop(); };

    // 검색 유입 직후 본문을 가리지 않도록 10초 지연 + 세션/하루 빈도 제한
    if (!seen && Date.now() > hideUntil) {
      setTimeout(openPop, 10000);
    }
    pop.querySelector(".ad-popup-close").addEventListener("click", closePop);
    pop.addEventListener("click", function (e) { if (e.target === pop) closePop(); });
    pop.querySelector("[data-dismiss-day]").addEventListener("click", function () {
      localStorage.setItem(DKEY, String(Date.now() + 24 * 60 * 60 * 1000)); // 24시간 동안 숨김
      closePop();
    });
    // 텔레그램 버튼을 누르면 다시 띄우지 않음(하루)
    pop.querySelector(".ad-popup-btn").addEventListener("click", function () {
      localStorage.setItem(DKEY, String(Date.now() + 24 * 60 * 60 * 1000));
    });
  }
})();
