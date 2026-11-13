/* Dependency-free 3D geometry projection. No simulation metrics are computed here. */
(() => {
  const canvas=document.getElementById('room3D'),ctx=canvas.getContext('2d');
  let data=null,yaw=-.65,pitch=.55,zoom=1,drag=null,W=0,H=0;
  const sub=(a,b)=>a.map((v,i)=>v-b[i]),add=(a,b)=>a.map((v,i)=>v+b[i]),mul=(a,k)=>a.map(v=>v*k);
  const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  const unit=a=>mul(a,1/Math.hypot(...a));
  function project(p){const a=sub(p,[2.5,2.5,1.3]),x=a[0]*Math.cos(yaw)-a[1]*Math.sin(yaw),y=a[0]*Math.sin(yaw)+a[1]*Math.cos(yaw);const s=Math.min(W/8,H/6.7)*zoom;return [W/2+x*s,H/2+(y*Math.sin(pitch)-a[2]*Math.cos(pitch))*s,y*Math.cos(pitch)+a[2]*Math.sin(pitch)];}
  function line(a,b,color,width=1,dashed=false){const p=project(a),q=project(b);ctx.beginPath();ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dashed?[5,5]:[]);ctx.moveTo(...p.slice(0,2));ctx.lineTo(...q.slice(0,2));ctx.stroke();ctx.setLineDash([]);}
  function label(p,text,color){const q=project(p);ctx.fillStyle=color;ctx.font='13px system-ui';ctx.fillText(text,q[0]+9,q[1]-10);}
  function node(p,text,color,r=6){const q=project(p);ctx.beginPath();ctx.arc(q[0],q[1],r,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();label(p,text,color);line([p[0],p[1],0],p,color+'44',1,true);}
  function mirrorBasis(n){const n0=[0,1,0],axis=cross(n0,n),s=Math.hypot(...axis),c=dot(n0,n);if(s<1e-10)return [[c>=0?1:-1,0,0],[0,0,1]];const k=mul(axis,1/s);const rotate=v=>add(add(mul(v,c),mul(cross(k,v),s)),mul(k,dot(k,v)*(1-c)));return [rotate([1,0,0]),rotate([0,0,1])];}
  function draw(){const rect=canvas.getBoundingClientRect(),dpr=devicePixelRatio||1;W=rect.width;H=rect.height;canvas.width=W*dpr;canvas.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.fillStyle='#102337';ctx.fillRect(0,0,W,H);
    for(let i=0;i<=5;i++){line([i,0,0],[i,5,0],'#294357');line([0,i,0],[5,i,0],'#294357');}
    for(const z of [0,3]){line([0,0,z],[5,0,z],'#658096');line([5,0,z],[5,5,z],'#658096');line([5,5,z],[0,5,z],'#658096');line([0,5,z],[0,0,z],'#658096');}
    for(const x of [0,5])for(const y of [0,5])line([x,y,0],[x,y,3],'#658096');label([5,0,0],'x = 5 m','#9ab2c5');label([0,5,0],'y = 5 m','#9ab2c5');label([0,0,3],'ceiling z = 3 m','#9ab2c5');
    if(!data){ctx.fillStyle='#cadbe8';ctx.fillText('Waiting for valid backend response…',20,30);return;}
    const g=data.geometry,r=data.ris,s=data.selected,center=r.panel_center;
    if(document.getElementById('room3DLinks').checked){const link=(a,b,gain,color)=>{if(gain>0)line(a,b,color,1.5)};link(g.alice,g.bob,s.direct_gains.h_AB,'#58aaff');link(g.alice,g.eve,s.direct_gains.h_AE,'#ffad65');g.jammers.forEach((j,i)=>{link(j,g.bob,s.direct_gains.h_JB[i],'#b48af355');link(j,g.eve,s.direct_gains.h_JE[i],'#b48af355')});const reflect=(a,b,gain,color)=>{if(gain>0){line(a,center,color,2,true);line(center,b,color,2,true)}};reflect(g.alice,g.bob,s.reflected_gains.h_AB,'#3ee9be');reflect(g.alice,g.eve,s.reflected_gains.h_AE,'#ff886a');g.jammers.forEach((j,i)=>{reflect(j,g.bob,s.reflected_gains.h_JB[i],'#bbaaff');reflect(j,g.eve,s.reflected_gains.h_JE[i],'#ff6f89')});}
    const name=data.configuration_names[s.ris_index],normals=r.configurations[name].tile_normals;
    const tiles=r.tile_centers.map((m,i)=>({m,n:normals[i],depth:project(m)[2]})).sort((a,b)=>a.depth-b.depth);
    tiles.forEach(({m,n})=>{const [u,v]=mirrorBasis(n),half=r.tile_side_m/2,points=[[-1,-1],[1,-1],[1,1],[-1,1]].map(([a,b])=>project(add(m,add(mul(u,a*half),mul(v,b*half)))));ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();ctx.fillStyle=s.ris_index===0?'#697985':'#46cbd2';ctx.fill();ctx.strokeStyle='#d4ffff';ctx.stroke();line(m,add(m,mul(n,.22)),'#e8ffff',1.5);});
    label(center,'RIS: '+name,'#72eaf0');node(g.alice,'Alice · ceiling','#ffd05b',8);g.jammers.forEach((p,i)=>node(p,'FJ '+(i+1),'#bf8cff'));node(g.bob,'Bob · z='+g.bob[2]+' m','#58adff',8);node(g.eve,'Eve · z='+g.eve[2]+' m','#ff738b',7);
  }
  window.room3DView=view=>{yaw=view==='side'?0:-.65;pitch=view==='top'?Math.PI/2:view==='side'?0:.55;zoom=1;draw()};
  canvas.addEventListener('pointerdown',e=>{drag=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)});canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw+=(e.clientX-drag[0])*.008;pitch=Math.max(-.2,Math.min(1.57,pitch+(e.clientY-drag[1])*.008));drag=[e.clientX,e.clientY];draw()});canvas.addEventListener('pointerup',()=>drag=null);canvas.addEventListener('pointercancel',()=>drag=null);canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.5,Math.min(2.5,zoom*Math.exp(-e.deltaY*.001)));draw()},{passive:false});
  document.getElementById('room3DLinks').onchange=draw;window.addEventListener('resize',draw);window.addEventListener('ris-3d-update',e=>{data=e.detail;document.getElementById('room3DStatus').textContent=data?'Backend-linked 3D view · configuration '+data.selected.ris_index+' · '+data.ris.num_tiles+' mirrors · drag to orbit, wheel to zoom':'Backend error: live geometry cleared';draw()});draw();
})();
