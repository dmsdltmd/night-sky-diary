/* 공통: 감정 색으로 무늬가 있는 행성 그리기 (모든 화면이 같이 씀)
   drawPlanet(g, x, y, r, color, {second, seed, ring, glow, lx, ly})
   - color: 가장 큰 감정 색, second: 두 번째 감정 색 (무늬에 섞임)
   - lx, ly: 빛이 오는 방향 (-1~1), 기본은 왼쪽 위 */
function _hex(h){const n=parseInt(h.slice(1),16);return[n>>16,n>>8&255,n&255]}
function _mix(a,b,t){const A=_hex(a),B=_hex(b);return A.map((v,i)=>Math.round(v+(B[i]-v)*t))}
function _rgb(c,a){return `rgba(${c[0]},${c[1]},${c[2]},${a})`}
function _rnd(s){return function(){s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
function drawPlanet(g, x, y, r, color, o){
  o = o || {}; const second = o.second || color, R = _rnd(o.seed || 7), lx = o.lx ?? -.45, ly = o.ly ?? -.5;
  const base = _hex(color), light = _mix(color,'#ffffff',.55), dark = _mix(color,'#060818',.6), sec = _hex(second);
  const tilt = -.35 + (R()-.5)*.2;
  // 고리 (뒤쪽 절반)
  const ring = (front) => { if (!o.ring) return; g.save(); g.translate(x,y); g.rotate(tilt);
    for (let k=0;k<4;k++){ g.strokeStyle = _rgb(_mix(color,'#ffffff',.3+k*.12), .5-k*.08); g.lineWidth = r*(.07-k*.012);
      g.beginPath(); g.ellipse(0,0,r*(1.55+k*.13),r*(.36+k*.03),0, front?0:Math.PI, front?Math.PI:Math.PI*2); g.stroke(); }
    g.restore(); };
  // 빛 번짐
  if (o.glow !== 0) { const gl = g.createRadialGradient(x,y,r*.7,x,y,r*(1.9*(o.glow||1))); gl.addColorStop(0,_rgb(base,.32)); gl.addColorStop(1,_rgb(base,0)); g.fillStyle = gl; g.beginPath(); g.arc(x,y,r*(1.9*(o.glow||1)),0,6.283); g.fill(); }
  ring(false);
  g.save(); g.beginPath(); g.arc(x,y,r,0,6.283); g.clip();
  // 바탕 구
  const b = g.createRadialGradient(x+lx*r*.5, y+ly*r*.5, r*.05, x, y, r*1.15);
  b.addColorStop(0,_rgb(light,1)); b.addColorStop(.45,_rgb(base,1)); b.addColorStop(1,_rgb(dark,1));
  g.fillStyle = b; g.fillRect(x-r,y-r,r*2,r*2);
  // 줄무늬 (기울어진 띠)
  g.save(); g.translate(x,y); g.rotate(tilt*.6);
  const bands = 7 + Math.floor(R()*5);
  for (let i=0;i<bands;i++){ const by = -r + (i+.5)*(2*r/bands) + (R()-.5)*r*.12, h = r*(.06+R()*.16), amp = r*(.02+R()*.05), fr = 2+R()*3, ph = R()*6;
    const c = R() < .35 ? sec : (R() < .5 ? _mix(color,'#ffffff',.35+R()*.25) : _mix(color,'#0a0a20',.25+R()*.3));
    g.fillStyle = _rgb(c, .18 + R()*.22); g.beginPath(); g.moveTo(-r*1.2, by);
    for (let t=-1.2;t<=1.2;t+=.1) g.lineTo(t*r, by + Math.sin(t*fr+ph)*amp);
    for (let t=1.2;t>=-1.2;t-=.1) g.lineTo(t*r, by + h + Math.sin(t*fr+ph+.6)*amp);
    g.closePath(); g.fill(); }
  // 점무늬 (구름, 폭풍)
  for (let i=0;i<10;i++){ const sx = (R()-.5)*1.6*r, sy = (R()-.5)*1.6*r, sr = r*(.04+R()*.13);
    g.fillStyle = R() < .5 ? _rgb(_mix(color,'#ffffff',.6), .16) : _rgb(_mix(second,'#000000',.2), .2);
    g.beginPath(); g.ellipse(sx,sy,sr*1.8,sr,0,0,6.283); g.fill(); }
  g.restore();
  // 그림자 (빛 반대쪽이 어둡게)
  const sh = g.createRadialGradient(x+lx*r*.6, y+ly*r*.6, r*.2, x+lx*r*.3, y+ly*r*.3, r*1.55);
  sh.addColorStop(0,'rgba(0,0,0,0)'); sh.addColorStop(.55,'rgba(4,6,20,.12)'); sh.addColorStop(1,'rgba(4,6,20,.88)');
  g.fillStyle = sh; g.fillRect(x-r,y-r,r*2,r*2);
  g.restore();
  // 가장자리 빛
  g.strokeStyle = _rgb(light,.45); g.lineWidth = Math.max(.8, r*.035); g.beginPath(); g.arc(x,y,r-.5,Math.PI*.9,Math.PI*1.75); g.stroke();
  ring(true);
}
