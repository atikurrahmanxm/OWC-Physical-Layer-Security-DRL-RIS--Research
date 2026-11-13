// Compare browser physics and result decoding with actual current Python outputs.
// First run: python paper_audit/check_paper_match.py
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
assert.strictEqual(html,fs.readFileSync(path.join(root,'visualizer.html'),'utf8'));
const reference=JSON.parse(fs.readFileSync(path.join(__dirname,'browser_reference.json'),'utf8'));
const start=html.indexOf('    const ROOM ='),end=html.indexOf('    // 2. STATE MANAGEMENT');
assert(start>=0&&end>start);
const context=vm.createContext({});
vm.runInContext(html.slice(start,end),context);
for(const c of reference.cases) {
  context.input=c;
  const actual=vm.runInContext(`(() => {
    const c=input;
    return {cs:evalSecrecyRateExact(c.h_AB,c.h_AE,c.h_JB,c.h_JE,c.w,.1,c.sigma).cs,
            ber:evalBobBerExact(c.h_AB,c.h_JB,c.w,c.sigma),energy:evalEnergyExact(c.w),
            zf:evalZFBeamformer(c.h_JB,c.h_JE),
            bounds:evalTheoreticalBoundsExact(c.h_AB,c.h_AE,c.h_JB,c.h_JE,.1,3.5,.4,c.sigma)};
  })()`,context);
  assert(Math.abs(actual.cs-c.cs)<1e-12);
  assert(Math.abs(actual.ber-c.ber)<1e-7);
  assert(Math.abs(actual.energy-c.energy)<1e-12);
  assert(Math.abs(actual.bounds.cs_star-c.rate_upper)<1e-12);
  assert(Math.abs(actual.bounds.u_star-c.utility_upper)<1e-7);
  for(const db of [4,6,8,10,12,14,16,18,20]) {
    context.db=db;
    const sigma=vm.runInContext('noiseFromSnr(input.h_AB,db,.1)',context);
    const expected=2*c.h_AB**2*.1**2/(Math.PI*Math.E*10**(db/10));
    assert(Math.abs(sigma/expected-1)<1e-12);
  }
  const dot=(a,b)=>a.reduce((v,x,i)=>v+x*b[i],0);
  assert(Math.abs(dot(c.h_JE,actual.zf)-dot(c.h_JE,c.zf))<1e-15);
  assert(Math.abs(dot(c.h_JB,actual.zf))<1e-15);
}
context.record=reference.record;
const packed=vm.runInContext('attachPythonResult(record)',context);
assert.strictEqual(packed.pending,false);
assert.deepStrictEqual(Array.from(packed.rawDRL.cs),reference.record.histories.drl.secrecy_rate);
const missing=vm.runInContext('runLearningSimCached([1.8,1.6,.85],[3.2,3.4,.85],SIGMA_TABLE1,.1,3.5,.4)',context);
assert.strictEqual(missing.pending,true);
assert(missing.drl.cs.every(Number.isNaN));
fs.writeFileSync(path.join(__dirname,'browser_verification_current.json'),JSON.stringify({cases:reference.cases.length,
  physics_python_parity:true,eq4_snr_normalization:true,actual_python_history_decoding:true,missing_curves_are_not_fabricated:true,html_copies_identical:true},null,2));
console.log('Browser checks passed: physics parity, real history decoding and no synthetic fallback.');
