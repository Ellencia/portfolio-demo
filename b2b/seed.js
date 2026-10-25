// my-b2b-apps 데모용 가상 데이터 — 앱의 localStorage 키 그대로 (프로필_키). capture.py 가 페이지에서 실행.
// 가상 고객사 "예시구청" 3개 부서 22대. 상태는 i*7 % 11 로 섞음 (0–6 완료, 7·8 보류, 9 불가, 10 없음)
() => {
  const P = '예시구청';
  localStorage.clear();
  localStorage.setItem('b2b_app_profiles', JSON.stringify([P, '예시저축은행 본점', '예시대학교 행정동']));
  localStorage.setItem('currentProfile', P);
  const k = (x) => `${P}_${x}`;
  const depts = [
    { name: '민원여권과', pre: '10.20.11.', n: 9 },
    { name: '세무과', pre: '10.20.12.', n: 7 },
    { name: '건축허가과', pre: '10.20.13.', n: 6 },
  ];
  const sur = '김이박최정강조윤장임한오서신권황안송류홍';
  const giv = ['민준', '서연', '도윤', '지우', '하준', '수아', '시우', '지민', '예준', '하은', '주원', '윤서', '지호', '채원', '준서', '다은', '현우', '서윤', '건우', '소율', '우진', '지아'];
  const presets = [
    { id: 1, name: '2층 민원실 복합기', model: 'Sindoh D420', ip: '10.20.11.250', port: '9100' },
    { id: 2, name: '3층 세무과 레이저', model: 'HP M404dn', ip: '10.20.12.250', port: '9100' },
  ];
  const customers = [];
  let i = 0;
  const t0 = Date.parse('2025-10-14T09:10:00+09:00');
  depts.forEach((d, di) => {
    const pos = {};
    for (let j = 0; j < d.n; j++, i++) {
      const id = 1000 + i, st = (i * 7) % 11, pr = presets[di === 1 ? 1 : 0];
      customers.push({
        id, createdAt: t0 + i * 17 * 60000,
        name: sur[i % sur.length] + giv[i % giv.length],
        workerName: ['김기사', '박기사'][i % 2], pcId: String(24100 + i), department: d.name,
        isCompleted: st < 7, isPending: st === 7 || st === 8, isError: st === 9,
        hasBackup: i % 3 !== 2, isRestored: i % 3 === 0,
        ip: d.pre + (21 + j), subnet: '255.255.255.0', gateway: d.pre + '1', dns1: '10.20.0.53', dns2: '168.126.63.1',
        backupNotes: st === 9 ? '메인보드 불량, 교체 요청' : st === 7 ? '사용자 부재, 오후 재방문' : st === 8 ? '전용 프로그램 설치 대기' : '',
        printers: [{ presetId: pr.id, model: pr.model, ip: pr.ip, port: pr.port }],
      });
      // 배치도: 3열 책상 줄 (가운데 통로), 앱 좌표계의 가운데 근처
      pos[id] = { left: `${360 + (j % 3) * 76 + (j % 3 === 2 ? 24 : 0)}px`, top: `${400 + Math.floor(j / 3) * 76}px` };
    }
    localStorage.setItem(k(`layout_${d.name}`), JSON.stringify({ positions: pos, lastModified: t0 }));
  });
  localStorage.setItem(k('customers'), JSON.stringify(customers));
  localStorage.setItem(k('printerPresets'), JSON.stringify(presets));
  localStorage.setItem(k('departmentPresets'), JSON.stringify(depts.map((d, n) => ({
    id: n + 1, name: d.name, ipPrefix: d.pre, subnet: '255.255.255.0', gateway: d.pre + '1', dns1: '10.20.0.53', dns2: '168.126.63.1' }))));
  localStorage.setItem(k('workerNames'), JSON.stringify(['김기사', '박기사']));
  localStorage.setItem(k('selectedLayoutDepartment'), '민원여권과');
  const n = (f) => customers.filter(f).length;
  return { total: customers.length, done: n(c => c.isCompleted), pending: n(c => c.isPending), error: n(c => c.isError),
           backup: n(c => c.hasBackup), restored: n(c => c.isRestored) };
}
