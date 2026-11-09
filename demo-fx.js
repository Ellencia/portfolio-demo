// 효과 부품 어댑터 (FX_DESIGN.md 1층). vendor/gsap-*.min.js·rough-notation-*.min.js(쓰는 것만) 다음, 페이지 스크립트·demo.js 보다 먼저 로드.
// CSS 애니메이션은 demo.js 가 원래대로 다루고, 여기는 자기 시계로 도는 부품(GSAP)을 demo.js 시계에 묶는다.
//   장면에 타임라인:  demoFx.gsap(장면요소, tl => tl.fromTo(el, {...}, {...}, 1.2))   시각(초)은 CSS --d 와 같은 단위(배속 전)
//   한글 자모 타자:   demoFx.type(tl, 요소, '문장', 시작초, 길이초)   요소 바로 뒤에 <i class="cur">|</i> 가 있으면 커서도
//   효과음: GSAP 요소는 demo.js 가 시작 시각을 모름 → data-sfx-at="초:소리" 로 직접 적기
window.demoFx = (() => {
  const tls = new Map();   // 장면 요소 → 그 장면의 타임라인(멈춘 채 만들어 둠)

  // 자판 누르는 순서대로의 화면 목록: '견적' → ㄱ 겨 견 겭 견저 견적 (첫 자음이 앞 글자 받침에 붙었다 넘어가는 것까지)
  const CHO = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ', JUNG = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ', JONG = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ';
  const PAIR = { 'ㅘ': 'ㅗㅏ', 'ㅙ': 'ㅗㅐ', 'ㅚ': 'ㅗㅣ', 'ㅝ': 'ㅜㅓ', 'ㅞ': 'ㅜㅔ', 'ㅟ': 'ㅜㅣ', 'ㅢ': 'ㅡㅣ', 'ㄳ': 'ㄱㅅ', 'ㄵ': 'ㄴㅈ', 'ㄶ': 'ㄴㅎ', 'ㄺ': 'ㄹㄱ',
    'ㄻ': 'ㄹㅁ', 'ㄼ': 'ㄹㅂ', 'ㄽ': 'ㄹㅅ', 'ㄾ': 'ㄹㅌ', 'ㄿ': 'ㄹㅍ', 'ㅀ': 'ㄹㅎ', 'ㅄ': 'ㅂㅅ' };
  const syl = (c, v, j) => String.fromCharCode(0xAC00 + (c * 21 + v) * 28 + j);
  const split = ch => { const n = (ch || ' ').charCodeAt(0) - 0xAC00; return n >= 0 && n < 11172 ? [Math.floor(n / 588), Math.floor(n / 28) % 21, n % 28] : null };
  const addJong = (j, k) => j ? JONG.indexOf(Object.keys(PAIR).find(x => PAIR[x] === JONG[j] + k) || '?') : JONG.indexOf(k);   // 받침 j + 자음 k → 받침 번호, 안 되면 -1
  function jamoFrames(s) {
    const out = []; let pre = '';
    for (const ch of s) {
      const p = split(ch);
      if (!p) { pre += ch; out.push(pre); continue }
      const [c, v, j] = p, last = split(pre.slice(-1)), k = last ? addJong(last[2], CHO[c]) : -1;
      out.push(k > 0 ? pre.slice(0, -1) + syl(last[0], last[1], k) : pre + CHO[c]);
      const vs = PAIR[JUNG[v]] || JUNG[v];
      out.push(pre + syl(c, JUNG.indexOf(vs[0]), 0)); if (vs.length > 1) out.push(pre + syl(c, v, 0));
      if (j) { const js = PAIR[JONG[j]] || JONG[j]; out.push(pre + syl(c, v, JONG.indexOf(js[0]))); if (js.length > 1) out.push(pre + syl(c, v, j)) }
      pre += ch;
    }
    return out;
  }

  // Rough Notation(손으로 그은 형광펜·밑줄): 그림만 라이브러리, 움직임은 CSS 라 demo.js 시계(배속·영상·카드)가 그대로 잡음
  //   demoFx.rough(요소, 시작초, {type:'highlight'|'underline'|..., iterations, strokeWidth, padding, soft})   시작초는 CSS --d 와 같은 단위
  //   soft: true = 형광펜을 덜 삐뚤게(아래 drawRough 참고)
  const roughs = [];
  let roughCss = false;
  function drawRough(r, i) {
    if (!roughCss) {
      roughCss = true;
      document.head.insertAdjacentHTML('beforeend', '<style>.on .rough-annotation path { animation: var(--rn) }</style>');
      // dry: 마른 붓 결. 가로로 길쭉한 고정 무늬로 칠 안에 가로 틈을 뚫고 가장자리를 살짝 흔듦(seed 고정 = 영상과 같음)
      //   영역은 픽셀 고정(좌표 = 칠할 말의 부모 상자 기준): 선 상자 기준(%)이면 거의 수평인 선의 상자 높이가 1–2px 라 띠만 남음
      document.body.insertAdjacentHTML('beforeend', `<svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="rn-dry" filterUnits="userSpaceOnUse" x="-40" y="-40" width="440" height="400">
        <feTurbulence type="fractalNoise" baseFrequency=".012 .45" numOctaves="2" seed="3" result="n"/>
        <feDisplacementMap in="SourceGraphic" in2="n" scale="3" xChannelSelector="R" yChannelSelector="G" result="d"/>
        <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  5 0 0 0 -1.9" result="m"/>
        <feComposite in="d" in2="m" operator="in"/></filter></svg>`);
    }
    if (r.a) r.a.remove();
    const st = document.getElementById('stage'), tf = st.style.transform;
    st.style.transform = '';   // 무대(360) 좌표로 재야 폰 크기가 바뀌어도 맞음(svg 도 무대와 같이 확대됨)
    const pe = r.el.parentElement;   // 그림 기준 상자를 부모로 고정 + 부모 안 글자 전부(칠한 말 옆 글자도) 그림 위로
    if (getComputedStyle(pe).position === 'static') pe.style.position = 'relative';
    pe.style.isolation = 'isolate';
    let cfg = r.cfg;
    if (cfg.type === 'highlight' && cfg.soft) {   // 라이브러리 형광펜은 삐뚤기 3 고정(설정 없음) → 삐뚤기 1.5 인 밑줄을 글자 높이만큼 굵게, 줄 가운데에
      const h = r.el.getClientRects()[0].height;
      cfg = { ...cfg, type: 'underline', strokeWidth: h * .95, padding: -h / 2 };
    }
    const a = r.a = RoughNotation.annotate(r.el, { multiline: true, animationDuration: 600, color: getComputedStyle(r.el).getPropertyValue('--marker').trim() || '#FFD84A', ...cfg });
    a._seed = 11 + i; a._animationDelay = r.at * 1000;   // 고정 난수(재생 = 영상 = 카드), 장면 안 시작 시각
    a.show(); a.detachListeners();   // 창 크기 따라 다시 그리는 기능은 끔(무대 확대를 모르고 애니메이션 없이 다시 그림)
    st.style.transform = tf;
    a._svg.style.zIndex = '-1';   // 부모 배경 위, 부모 안 글자 아래
    a._svg.style.width = a._svg.style.height = '1px';   // 그림은 넘쳐서 그려짐. 상자가 100px 이면 줄 글자 범위를 재는 코드(하네스 A 화살표)에 섞임, 0 이면 SVG 가 안 그려짐
    a._svg.querySelectorAll('path').forEach(p => { p.style.setProperty('--rn', p.style.animation); p.style.animation = '' });   // 장면이 켜질 때(.on) 출발
    // cap: 굵은 선 끝이 수직으로 잘려 사각형처럼 보이는 것 완화. 'round' = 둥근 끝(튀어나온 반지름의 절반만큼 줄임: 다 줄이면 둥근 끝이 얇아 첫·끝 글자가 빔), 'slant' = 형광펜 촉처럼 사선
    // len: 왼쪽 기준으로 이 비율만큼만(붓 가닥 길이 차이), dry: 위 필터
    a._svg.querySelectorAll('path').forEach(p => {
      const t = [];
      if (cfg.cap === 'round') { p.setAttribute('stroke-linecap', 'round'); t.push(`scaleX(${Math.max(.5, 1 - cfg.strokeWidth / 2 / p.getBBox().width)})`) }
      if (cfg.cap === 'slant') t.push('skewX(-25deg)');
      if (cfg.len) t.push(`scaleX(${cfg.len})`);
      if (cfg.dry) p.style.filter = 'url(#rn-dry)';
      if (t.length) { p.style.transformBox = 'fill-box'; p.style.transformOrigin = cfg.len ? 'left' : 'center'; p.style.transform = t.join(' ') }
    });
  }
  // ponytail: 글꼴 로드 뒤 한 번 다시 그림. 지금 켜진 장면의 그림이면 배속이 다음 장면 전환부터 걸림(현재 쓰는 곳은 첫 장면 아님)
  document.fonts.ready.then(() => roughs.forEach(drawRough));

  return {
    jamoFrames,
    rough(el, at, cfg = {}) { const r = { el, at, cfg }; roughs.push(r); drawRough(r, roughs.length - 1); return r },
    gsap(scene, build) { const tl = gsap.timeline({ paused: true }); build(tl); tls.set(scene, tl); return tl },
    type(tl, el, text, at, dur) {
      const fr = jamoFrames(text); let seed = 7, acc = 0;
      const rnd = () => (seed = seed * 16807 % 2147483647) / 2147483647;   // 고정 난수: 들쭉날쭉하되 매번 같게(영상 = 재생)
      const ts = fr.map(f => { const t = acc; acc += .6 + rnd() + (f.endsWith(' ') ? 1.5 : 0); return t });
      const last = ts[ts.length - 1] || 1, p = { t: 0 };
      el.textContent = '';
      tl.fromTo(p, { t: 0 }, { t: dur, duration: dur, ease: 'none', onUpdate() {
        let i = -1; while (i + 1 < fr.length && ts[i + 1] * dur / last <= p.t) i++;
        el.textContent = p.t <= 0 ? '' : fr[i];
      } }, at);
      const cur = el.nextElementSibling;
      if (cur && cur.classList.contains('cur')) {   // 치는 동안 켜져 있다가 두 번 깜빡이고 꺼짐(끝없이 깜빡이면 장면 길이가 무한)
        gsap.set(cur, { opacity: 0 });
        tl.set(cur, { opacity: 1 }, at).to(cur, { opacity: 0, duration: .3, ease: 'steps(1)', repeat: 2, yoyo: true }, at + dur);
      }
      return tl;
    },
    // ↓ demo.js 가 부름. rate = demo.js 의 RATE, ms = 장면 시작부터 실제 경과 시간
    show(scene, rate) {   // 장면 켜짐: 그 장면만 처음부터, 장면 길이(ms) 돌려줌
      tls.forEach(tl => tl.pause(0, false));   // false: 되감을 때도 onUpdate → 치던 글자가 남지 않게
      const tl = tls.get(scene);
      if (!tl) return 0;
      tl.timeScale(rate).play(0, false);
      return tl.duration() * 1000 / rate;
    },
    frame(scene, ms, rate) { const tl = tls.get(scene); if (tl) tl.pause().seek(ms * rate / 1000, false) },   // false: onUpdate(자모·숫자)도 돌게
    end(scene) { const tl = tls.get(scene); if (tl) tl.pause().progress(1, false) },   // ?shot 카드 = 끝 모습
  };
})();
