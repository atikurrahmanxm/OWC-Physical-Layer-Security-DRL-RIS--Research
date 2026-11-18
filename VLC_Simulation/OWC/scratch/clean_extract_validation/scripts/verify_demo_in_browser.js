/**
 * verify_demo_in_browser.js
 * 
 * Performs genuine in-browser verification of supervisor_demo.html using headless Edge & CDP:
 * 1. Verifies metadata tile-size labels in DOM (0.159m x 0.159m present; 0.2m absent).
 * 2. Verifies zero weights handling (Python returns [0,0,0,0], zero-jamming unmodulated state).
 * 3. Verifies DRL replay scenario isolation (scenario snapshot, invalidation on manual preset change).
 * 4. Captures live screenshots (nominal, near_bob, stowed).
 * 5. Asserts 0 uncaught browser console exceptions.
 */

const http = require('http');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const EDGE_PATH = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const CDP_PORT = 9222;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.reqId = 1;
    this.pending = new Map();
    this.events = [];
    this.consoleErrors = [];
  }

  connect() {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.wsUrl);
      this.ws.onopen = () => resolve();
      this.ws.onerror = err => reject(err);
      this.ws.onmessage = msg => {
        const data = JSON.parse(msg.data);
        if (data.id && this.pending.has(data.id)) {
          const { resolve, reject } = this.pending.get(data.id);
          this.pending.delete(data.id);
          if (data.error) reject(new Error(data.error.message));
          else resolve(data.result);
        } else if (data.method) {
          if (data.method === 'Runtime.consoleAPICalled') {
            if (data.params.type === 'error') {
              this.consoleErrors.push(data.params.args.map(a => a.value || a.description).join(' '));
            }
          } else if (data.method === 'Runtime.exceptionThrown') {
            this.consoleErrors.push(data.params.exceptionDetails.text);
          }
        }
      };
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.reqId++;
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async eval(expr) {
    const res = await this.send('Runtime.evaluate', {
      expression: expr,
      returnByValue: true,
      awaitPromise: true
    });
    if (res.exceptionDetails) {
      throw new Error(`Eval failed for "${expr}": ${res.exceptionDetails.text}`);
    }
    return res.result ? res.result.value : undefined;
  }

  async captureScreenshot(outputPath) {
    const res = await this.send('Page.captureScreenshot', { format: 'png' });
    const buffer = Buffer.from(res.data, 'base64');
    fs.writeFileSync(outputPath, buffer);
    console.log(`Saved screenshot (${(buffer.length / 1024).toFixed(1)} KB) -> ${path.relative(ROOT, outputPath)}`);
  }

  close() {
    if (this.ws) this.ws.close();
  }
}

async function main() {
  console.log('=== Starting In-Browser Verification of supervisor_demo.html ===\n');

  // 1. Start Python server
  console.log('1. Launching Python loopback server...');
  const serverProc = spawn('python', ['-c', `
from app_server import start_server
import time, sys
s, url = start_server()
print(f"READY:{url}", flush=True)
while True:
    time.sleep(1)
`], { cwd: ROOT });

  let serverUrl = null;
  serverProc.stdout.on('data', data => {
    const str = data.toString();
    const match = str.match(/READY:(http:\/\/127\.0\.0\.1:\d+\/)/);
    if (match) serverUrl = match[1];
  });
  serverProc.stderr.on('data', data => console.error('[Server Error]', data.toString().trim()));

  for (let i = 0; i < 40; i++) {
    if (serverUrl) break;
    await sleep(250);
  }
  if (!serverUrl) throw new Error('Failed to start python loopback server');
  console.log(`   Python server running at ${serverUrl}`);

  // 2. Launch headless Edge with remote debugging
  console.log('2. Launching Microsoft Edge headless with CDP...');
  const tmpUserData = path.join(ROOT, 'scratch', 'edge_user_data_' + Date.now());
  const edgeProc = spawn(EDGE_PATH, [
    '--headless=new',
    `--remote-debugging-port=${CDP_PORT}`,
    '--window-size=1600,1000',
    `--user-data-dir=${tmpUserData}`,
    '--disable-gpu',
    'about:blank'
  ]);

  await sleep(2000);

  // 3. Connect to Edge CDP WebSocket
  console.log('3. Connecting to Edge via Chrome DevTools Protocol...');
  const targets = await fetchJson(`http://127.0.0.1:${CDP_PORT}/json`);
  const pageTarget = targets.find(t => t.type === 'page');
  if (!pageTarget) throw new Error('No page target found on Edge remote debugging');
  console.log(`   Target page: ${pageTarget.title} (${pageTarget.webSocketDebuggerUrl})`);

  const cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
  await cdp.connect();

  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');
  await cdp.send('Emulation.setDeviceMetricsOverride', {
    width: 1600,
    height: 1000,
    deviceScaleFactor: 1,
    mobile: false
  });

  try {
    // 4. Navigate to supervisor demo
    const demoUrl = `${serverUrl}demo`;
    console.log(`4. Navigating to ${demoUrl}...`);
    await cdp.send('Page.navigate', { url: demoUrl });
    await sleep(2500); // Allow DOM ready and initial /api/ris/metrics POST

    // =========================================================================
    // VERIFICATION 1: METADATA TILE SIZE LABELS
    // =========================================================================
    console.log('\n--- VERIFICATION 1: Metadata Tile-Size Labels ---');
    const hudTopLeftText = await cdp.eval('document.getElementById("hudTopLeft").innerText');
    console.log('   HUD text in DOM:\n', hudTopLeftText.split('\n').map(l => '     ' + l).join('\n'));

    const has0159 = hudTopLeftText.includes('0.159');
    const has020 = hudTopLeftText.includes('0.2m x 0.2m') || hudTopLeftText.includes('0.2m × 0.2m');

    console.log(`   [CHECK] Contains "0.159": ${has0159 ? 'PASS' : 'FAIL'}`);
    console.log(`   [CHECK] Contains old "0.2m": ${!has020 ? 'PASS (Absent)' : 'FAIL (Found!)'}`);

    if (!has0159 || has020) {
      throw new Error(`Tile size verification failed! hudTopLeftText: ${hudTopLeftText}`);
    }

    const hudRisInfoText = await cdp.eval('document.getElementById("hudRisInfo").innerText');
    console.log('   HUD RIS Info:', hudRisInfoText);
    if (!hudRisInfoText.includes('0.159')) {
      throw new Error(`hudRisInfo missing 0.159m: ${hudRisInfoText}`);
    }

    // =========================================================================
    // VERIFICATION 2: ZERO JAMMER WEIGHTS & TRUTHINESS FIX
    // =========================================================================
    console.log('\n--- VERIFICATION 2: Zero Jammer Weights Handling ---');
    console.log('   Executing setWeights([0, 0, 0, 0]) in browser...');
    await cdp.eval('setWeights([0, 0, 0, 0])');
    await sleep(1500); // Wait for /api/ris/metrics update

    const w0Val = await cdp.eval('document.getElementById("w0").value');
    const w1Val = await cdp.eval('document.getElementById("w1").value');
    const backendBeamformer = await cdp.eval('window._lastBackendData ? window._lastBackendData.selected.beamformer : null');
    console.log(`   DOM Input values: w0=${w0Val}, w1=${w1Val}`);
    console.log(`   Authoritative backend beamformer from Python: [${backendBeamformer.join(', ')}]`);

    const allZeros = Array.isArray(backendBeamformer) && backendBeamformer.every(x => Math.abs(x) < 1e-9);
    console.log(`   [CHECK] Python received and computed strictly zero weights: ${allZeros ? 'PASS' : 'FAIL'}`);
    if (!allZeros) {
      throw new Error(`Zero weights verification failed! Beamformer: ${JSON.stringify(backendBeamformer)}`);
    }

    // Restore nominal weights
    console.log('   Restoring nominal weights [-0.5, 1.0, 0.0, 1.0]...');
    await cdp.eval('setWeights([-0.5, 1.0, 0.0, 1.0])');
    await sleep(1500);

    // =========================================================================
    // VERIFICATION 3: DRL REPLAY SCENARIO ISOLATION
    // =========================================================================
    console.log('\n--- VERIFICATION 3: DRL Replay Scenario Isolation ---');
    console.log('   Executing runSmokeTrain() (24 slots) in browser...');
    await cdp.eval('document.getElementById("smokeSlots").value = "24"; runSmokeTrain()');

    // Poll until smokeReplayBox is visible (up to 25s)
    let replayBoxVisible = false;
    for (let i = 0; i < 50; i++) {
      const disp = await cdp.eval('document.getElementById("smokeReplayBox").style.display');
      if (disp === 'block') {
        replayBoxVisible = true;
        break;
      }
      await sleep(500);
    }
    console.log(`   [CHECK] Smoke replay box displayed: ${replayBoxVisible ? 'PASS' : 'FAIL'}`);
    if (!replayBoxVisible) throw new Error('Smoke replay box did not display after runSmokeExperiment');

    const replayBadgeText = await cdp.eval('document.getElementById("replaySlotBadge").textContent');
    console.log(`   Replay badge: "${replayBadgeText}"`);

    // Verify scenario snapshot exists
    const scenarioSnapshot = await cdp.eval('typeof replayScenario !== "undefined" ? replayScenario : null');
    console.log('   Scenario snapshot in browser memory:', scenarioSnapshot);
    if (!scenarioSnapshot || !scenarioSnapshot.bob || !scenarioSnapshot.eve) {
      throw new Error('Replay scenario snapshot missing in browser memory!');
    }

    // Now test isolation: user clicks Near-Bob preset
    console.log('   User manually clicks setPreset("near_bob")...');
    await cdp.eval('setPreset("near_bob")');
    await sleep(1000);

    const isReplayActive = await cdp.eval('typeof isReplayActive !== "undefined" ? isReplayActive : true');
    const badgeAfterPreset = await cdp.eval('document.getElementById("replaySlotBadge").textContent');
    console.log(`   isReplayActive after preset change: ${isReplayActive} (expected false)`);
    console.log(`   Replay badge after preset change: "${badgeAfterPreset}" (expected to contain "Paused")`);

    const isolationPassed = !isReplayActive && badgeAfterPreset.includes('Paused');
    console.log(`   [CHECK] Replay invalidation guard on manual scene change: ${isolationPassed ? 'PASS' : 'FAIL'}`);
    if (!isolationPassed) {
      throw new Error(`Replay isolation guard failed! isReplayActive=${isReplayActive}, badge="${badgeAfterPreset}"`);
    }

    // =========================================================================
    // CAPTURE AUTHORITATIVE SCREENSHOTS
    // =========================================================================
    console.log('\n--- Capturing Authoritative High-Resolution Screenshots ---');
    const figDir = path.join(ROOT, 'supervisor_package', 'figures');

    // 1. Nominal view (Bob 1.8, 1.6; Eve 3.2, 3.4; Config 1: Aim Alice -> Bob)
    await cdp.eval('setPreset("nominal")');
    await sleep(1500);
    await cdp.captureScreenshot(path.join(figDir, 'demo_3d_nominal.png'));
    await cdp.captureScreenshot(path.join(figDir, 'demo_screenshot.png'));

    // 2. Near-Bob view (Eve 1.85, 1.65, d_BE = 0.07m)
    await cdp.eval('setPreset("near_bob")');
    await sleep(1500);
    await cdp.captureScreenshot(path.join(figDir, 'demo_3d_near_bob.png'));

    // 3. Stowed RIS view (Config 0: Off)
    await cdp.eval('setPreset("nominal")');
    await sleep(1000);
    await cdp.eval('document.getElementById("cfg0").click()');
    await sleep(1500);
    await cdp.captureScreenshot(path.join(figDir, 'demo_3d_stowed.png'));

    // 4. Changed Positions view (Bob 2.0, 3.0; Eve 3.5, 1.5; d_BE = 2.12m)
    await cdp.eval('setPreset("changed")');
    await sleep(1500);
    const bobX = await cdp.eval('parseFloat(document.getElementById("bx").value)');
    const eveX = await cdp.eval('parseFloat(document.getElementById("ex").value)');
    console.log(`   [CHECK] Changed preset coordinates in DOM: Bob.x=${bobX}, Eve.x=${eveX}`);
    if (Math.abs(bobX - 2.0) > 1e-4 || Math.abs(eveX - 3.5) > 1e-4) {
      throw new Error(`Changed preset failed to update coordinates!`);
    }
    await cdp.captureScreenshot(path.join(figDir, 'demo_3d_changed_positions.png'));

    // Restore nominal Config 1
    await cdp.eval('setPreset("nominal")');
    await sleep(1000);
    await cdp.eval('document.getElementById("cfg1").click()');
    await sleep(1000);

    // =========================================================================
    // CONSOLE ERROR CHECK
    // =========================================================================
    console.log('\n--- Browser Console Errors ---');
    console.log(`   Uncaught console errors: ${cdp.consoleErrors.length}`);
    if (cdp.consoleErrors.length > 0) {
      console.error('   Errors encountered:', cdp.consoleErrors);
      throw new Error(`Browser console encountered ${cdp.consoleErrors.length} errors!`);
    } else {
      console.log('   [CHECK] Zero console errors: PASS');
    }

    console.log('\n=============================================================');
    console.log('🎉 ALL IN-BROWSER VERIFICATIONS & SCREENSHOTS COMPLETED 100%!');
    console.log('=============================================================');

  } finally {
    cdp.close();
    try { edgeProc.kill(); } catch (e) {}
    try { serverProc.kill(); } catch (e) {}
    try { fs.rmSync(tmpUserData, { recursive: true, force: true }); } catch (e) {}
  }
}

main().catch(err => {
  console.error('\n❌ In-Browser Verification Failed:\n', err);
  process.exit(1);
});
