// 폰 데모 재생 (excel.html · harness.html 공용)
// 장면 길이 = 장면 안 애니메이션이 다 끝나는 시각 + HOLD (끝난 화면을 보여 주는 시간)
// HOLD 는 페이지마다 <div class="stage" data-hold="1300"> 로 바꿀 수 있음 (한눈에 읽히는 화면이면 짧게)
const stage = document.getElementById('stage'), phone = document.getElementById('phone');
const RATE = 1.15, HOLD = +stage.dataset.hold || 3500;
const scenes = [...stage.querySelectorAll('.scene')];
const bars = document.getElementById('bars'), chips = document.getElementById('chips');
const params = new URLSearchParams(location.search);
let cur = 0, timer = null, playing = true;

scenes.forEach((s, i) => {
  bars.insertAdjacentHTML('beforeend', '<i><b></b></i>');
  const b = document.createElement('button');
  b.type = 'button'; b.textContent = i + 1; b.onclick = () => show(i);
  chips.append(b);
  const pg = s.querySelector('.pg');
  if (pg) pg.textContent = `${i + 1} / ${scenes.length}`;
});

function fit() {
  if (document.body.classList.contains('shot')) { stage.style.transform = ''; return; }
  stage.style.transform = `scale(${phone.clientWidth / 360})`;
}

// 장면 애니메이션을 RATE 배로 빠르게 하고, 다 끝나는 시각(ms)을 돌려줌
function speedUp(s) {
  const anims = s.getAnimations({ subtree: true });
  anims.forEach(a => a.playbackRate = RATE);
  return Math.max(0, ...anims.map(a => a.effect.getComputedTiming().endTime)) / RATE;
}

function show(i) {
  cur = (i + scenes.length) % scenes.length;
  scenes.forEach(s => s.classList.remove('on'));
  void stage.offsetWidth; // 애니메이션 처음부터 다시
  scenes[cur].classList.add('on');
  const dur = speedUp(scenes[cur]) + HOLD;
  [...bars.children].forEach((b, j) => {
    b.className = j < cur ? 'done' : '';
    if (j === cur) { b.style.setProperty('--dur', dur + 'ms'); void b.offsetWidth; b.className = 'now'; }
  });
  bars.children[cur].firstChild.style.animationPlayState = playing ? 'running' : 'paused';
  [...chips.children].forEach((c, j) => c.setAttribute('aria-current', j === cur));
  clearTimeout(timer);
  if (playing) timer = setTimeout(() => show(cur + 1), dur);
  return dur;
}

// 일시정지 = 자동 넘김만 멈춤 (장면 안 움직임은 끝까지 재생)
function setPlaying(p) {
  playing = p;
  document.getElementById('play').textContent = p ? '일시정지' : '재생';
  bars.children[cur].firstChild.style.animationPlayState = p ? 'running' : 'paused';
  clearTimeout(timer);
  if (p) timer = setTimeout(() => show(cur + 1), 1500);
}

document.getElementById('prev').onclick = () => show(cur - 1);
document.getElementById('next').onclick = () => show(cur + 1);
document.getElementById('play').onclick = () => setPlaying(!playing);
document.getElementById('rec').onclick = () => { document.body.classList.add('rec'); fit(); show(0); };
phone.onclick = () => { if (document.body.classList.contains('rec')) { document.body.classList.remove('rec'); fit(); } };
addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') show(cur + 1);
  else if (e.key === 'ArrowLeft') show(cur - 1);
  else if (e.key === ' ' && e.target === document.body) { e.preventDefault(); setPlaying(!playing); }
});
addEventListener('resize', fit);

// 카드 렌더용: excel.html?shot=3 → 3번 장면 마지막 모습을 360x640 으로
if (params.has('video')) {
  // 영상 렌더용(make_video.py): 자동 넘김 없이, 바깥에서 demoShow(장면) → demoFrame(ms) 로 한 프레임씩 맞춰 찍음
  document.body.classList.add('shot', 'video');
  playing = false;
  window.demoScenes = scenes.length;
  window.demoShow = i => show(i);
  window.demoFrame = t => {
    document.getAnimations().forEach(a => { a.pause(); a.currentTime = t * a.playbackRate; });
    document.querySelectorAll('svg').forEach(s => { s.pauseAnimations(); s.setCurrentTime(t / 1000 + 2); });  // +2초: 늦게 출발하는 동그라미가 구석에 서 있지 않게
  };
  // 효과음(make_video.py --sfx): 지금 장면의 [ms, 소리] 목록. 소리는 요소의 첫 애니메이션이 시작하는 순간에 남
  // 클래스별 기본 소리 + 요소의 data-sfx="소리"(덮어쓰기, "none" 이면 끔) + data-sfx-at="초:소리 ..."(CSS 지연과 같은 단위)
  const SFX = { '.pop': 'pop', '.rip': 'click', '.bat': 'click', '.qbtns .go': 'click', '.mini .go': 'click', '.toast': 'menu', '.dock span': 'tick' };
  window.demoSfx = () => {
    const s = scenes[cur], hits = new Map(), out = [];
    for (const [sel, n] of Object.entries(SFX)) s.querySelectorAll(sel).forEach(e => hits.set(e, n));
    s.querySelectorAll('[data-sfx]').forEach(e => hits.set(e, e.dataset.sfx));
    hits.forEach((n, e) => {
      const a = e.getAnimations()[0];
      if (a && n !== 'none') out.push([a.effect.getTiming().delay / a.playbackRate, n]);
    });
    s.querySelectorAll('[data-sfx-at]').forEach(e => e.dataset.sfxAt.split(' ').forEach(p => {
      const [t, n] = p.split(':');
      out.push([t * 1000 / RATE, n]);
    }));
    return out.sort((x, y) => x[0] - y[0]);
  };
} else if (params.has('shot')) {
  document.body.classList.add('shot');
  stage.classList.add('still');
  playing = false;
  show(+params.get('shot') - 1);
} else {
  show(0);
}
fit();
