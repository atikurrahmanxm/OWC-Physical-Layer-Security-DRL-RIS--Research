// Headless Edge smoke check of the actual served dashboard. Uses an isolated temp profile.
// node paper_audit/browser_smoke.js http://127.0.0.1:PORT/
const fs=require('fs'),os=require('os'),path=require('path'),cp=require('child_process'),assert=require('assert');
const url=process.argv[2];if(!url)throw Error('Pass the local simulation URL');
const pause=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const profile=fs.mkdtempSync(path.join(os.tmpdir(),'owc-edge-check-'));
  const exe='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  const edge=cp.spawn(exe,['--headless','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{windowsHide:true,stdio:'ignore'});
  let ws;
  try {
    const portFile=path.join(profile,'DevToolsActivePort');
    for(let i=0;i<100&&!fs.existsSync(portFile);i++)await pause(100);
    const port=Number(fs.readFileSync(portFile,'utf8').split(/\r?\n/)[0]);
    const pages=await (await fetch('http://127.0.0.1:'+port+'/json/list')).json();
    const page=pages.find(p=>p.type==='page');
    ws=new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
    let id=0;const pending=new Map(),errors=[];
    ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text+': '+(m.params.exceptionDetails.exception?.description||''));};
    const send=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}));setTimeout(()=>{if(pending.has(n)){pending.delete(n);reject(Error('CDP timeout: '+method));}},15000).unref();});
    const evaluate=async expression=>(await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true})).result.value;
    await send('Runtime.enable');await send('Page.enable');
    await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
    await send('Page.navigate',{url});await pause(1800);
    const initial=await evaluate(`({title:document.title,rate:document.getElementById('dispCs').innerText,status:document.getElementById('trainingStatus').innerText,energy:energyModel(),snr:snrDefinition(),pending:computeSystemState([1.8,1.6,.85],[3.2,3.4,.85],12,.1,3.5,.4,1,true).sim.pending})`);
    assert(Number.isFinite(Number(initial.rate)));assert.strictEqual(initial.pending,true);
    assert.strictEqual(initial.energy,'l1');assert.strictEqual(initial.snr,'eq4');
    await evaluate(`switchMainView('fig6');switchMainView('fig7');setPreset('high_snr');`);
    assert.strictEqual(await evaluate(`document.getElementById('chkTable1Noise').checked`),false);
    await evaluate(`setPreset('paper_nominal');setRightPanelTab('math');switchMainView('room3d');document.getElementById('energyModel').value='paper_signed';updateUI();`);
    assert((await evaluate(`document.getElementById('m_energyLabel').innerText`)).includes('signed'));
    await evaluate(`document.getElementById('energyModel').value='l1';updateUI();`);
    const screenshot=await send('Page.captureScreenshot',{format:'png'});
    fs.writeFileSync(path.join(__dirname,'dashboard_smoke.png'),Buffer.from(screenshot.data,'base64'));
    assert.deepStrictEqual(errors,[]);
    const result={initial,js_errors:errors,figure_tabs:true,snr_preset_override:true,math_panel:true,defaults_and_energy_labels:true,scope:'Live UI navigation and physics; real-agent API parity tested in Python regressions.'};
    fs.writeFileSync(path.join(__dirname,'browser_smoke_result.json'),JSON.stringify(result,null,2));
    console.log(JSON.stringify(result,null,2));
    await send('Browser.close').catch(()=>{});
  } finally {if(ws)ws.close();edge.kill();}
})().catch(e=>{console.error(e);process.exitCode=1;});
