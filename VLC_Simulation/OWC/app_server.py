"""Loopback-only browser/desktop bridge to the actual Python CNN/DND agents."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import uuid
import webbrowser
import tempfile
import numpy as np
from vlc.config import VLCConfig
from vlc.experiments import json_value, run_learning_experiment

ROOT = Path(__file__).resolve().parent


def validate_request(data):
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    allowed = {"bob", "eve", "sigma", "alpha", "delta1", "delta2", "seed", "slots", "energy_model", "snr_definition",
               "model", "receiver_resistance_ohm", "jammer_resistance_ohm", "slot_duration_s"}
    if set(data) - allowed:
        raise ValueError("Unknown simulation parameters")
    bob = np.asarray(data.get("bob", [1.8, 1.6, .85]), dtype=float)
    eve = np.asarray(data.get("eve", [3.2, 3.4, .85]), dtype=float)
    for node in (bob, eve):
        if node.shape != (3,) or not np.all(np.isfinite(node)) or np.any(node < 0) or np.any(node > [5, 5, 2.5]):
            raise ValueError("Receivers must lie inside the room below 2.5 m")
    slots = data.get("slots", 2000)
    seed = data.get("seed", 42)
    if type(slots) is not int or not 1 <= slots <= 2000 or type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("slots must be 1..2000; seed must be an unsigned 32-bit integer")
    c = VLCConfig(model=data.get('model','paper'),
                  receiver_resistance_ohm=float(data.get('receiver_resistance_ohm',1.)),
                  jammer_resistance_ohm=float(data.get('jammer_resistance_ohm',1.)),
                  slot_duration_s=float(data.get('slot_duration_s',1.)),
                  modulation_index=float(data.get("alpha", .1)),
                  delta1=float(data.get("delta1", 3.5)), delta2=float(data.get("delta2", .4)),
                  seed=seed, energy_model=data.get("energy_model"),
                  snr_definition=data.get("snr_definition"))
    if not np.all(np.isfinite([c.delta1, c.delta2])):
        raise ValueError("Utility weights must be finite")
    sigma = float(data.get("sigma", c.noise_variance))
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("Noise variance must be finite and positive")
    return c, bob, eve, sigma, slots


def validate_ris_request(data):
    from vlc.ris import OpticalRISConfig
    if not isinstance(data,dict):
        raise ValueError('Expected a JSON object')
    allowed={'bob','eve','sigma','alpha','delta1','delta2','seed','seeds','slots',
             'energy_model','snr_definition','model','beamformer','ris_index','ris_config',
             'qos_ber_max','qos_penalty','secrecy_target'}
    if set(data)-allowed:
        raise ValueError('Unknown RIS experiment parameters')
    if data.get('model','paper')!='paper':
        raise ValueError('RIS experiments preserve the 2024 paper-mode baseline')
    seeds=data.get('seeds',[data.get('seed',42)])
    if not isinstance(seeds,list) or not 1<=len(seeds)<=5 or len(set(seeds))!=len(seeds) or any(type(s)is not int or not 0<=s<2**32 for s in seeds):
        raise ValueError('Select 1..5 distinct unsigned 32-bit integer seeds')
    base={key:value for key,value in data.items() if key in
          {'bob','eve','sigma','alpha','delta1','delta2','seed','slots','energy_model','snr_definition','model'}}
    base['energy_model']=data.get('energy_model','paper_signed')
    if base['energy_model'] not in {'paper_signed','l1'}:
        raise ValueError('Select a documented paper energy interpretation')
    base['seed']=seeds[0]
    c,bob,eve,sigma,slots=validate_request(base)
    settings=data.get('ris_config',{})
    if not isinstance(settings,dict):
        raise ValueError('RIS settings must be an object')
    fields={'enabled','panel_center','panel_width_m','panel_height_m','rows','cols','reflectivity','max_tilt_deg'}
    if set(settings)-fields:
        raise ValueError('Unknown optical RIS settings')
    ris=OpticalRISConfig(**settings)
    if ris.rows*ris.cols>64:
        raise ValueError('The interactive service supports at most 64 mirror elements')
    target=data.get('qos_ber_max')
    penalty=float(data.get('qos_penalty',0.))
    secrecy=float(data.get('secrecy_target',.1))
    if target is not None and (not isinstance(target,(int,float)) or not np.isfinite(target) or not 0<target<=.75):
        raise ValueError('Bob BER threshold must lie in (0,.75]')
    if not np.isfinite(penalty) or penalty<0 or (penalty>0 and target is None) or not np.isfinite(secrecy) or secrecy<0:
        raise ValueError('Invalid QoS penalty or secrecy target')
    return c,bob,eve,sigma,slots,seeds,ris,target,penalty,secrecy


def ris_metrics(data):
    from vlc.ris_environment import RISEnvironment
    c,bob,eve,sigma,_,_,ris,target,penalty,_=validate_ris_request(data)
    env=RISEnvironment(c,ris,bob,eve,sigma,control_mode='joint',qos_ber_max=target,qos_penalty=penalty)
    w=np.asarray(data.get('beamformer',[-.5,1.,0.,1.]),dtype=float)
    index=data.get('ris_index',1 if env.num_ris_configurations>1 else 0)
    if type(index)is not int:
        raise ValueError('RIS index must be an integer')
    selected=env.evaluate_action(env.encode_action(w,index))
    baseline=env.evaluate_action(env.encode_action(w,0))
    return {'selected':selected,'baseline':baseline,'ris':env.ris_metadata(),
            'configuration_names':list(env.ris.configuration_names),
            'geometry':{'alice':c.alice_pos,'jammers':c.jammer_positions,'bob':bob,'eve':eve},
            'paper_reproduction_verified':False}


class SimulationServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address=("127.0.0.1", 0)):
        if address[0] != "127.0.0.1":
            raise ValueError("The simulation service binds only to IPv4 loopback")
        super().__init__(address, Handler)
        self.jobs = {}
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="vlc-simulation")

    def server_close(self):
        super().server_close()
        self.executor.shutdown(wait=True, cancel_futures=True)

    def submit(self, payload):
        args = validate_request(payload)
        key = json.dumps(payload, sort_keys=True, allow_nan=False)
        with self.lock:
            for job_id, job in self.jobs.items():
                if job["key"] == key and job["status"] != "error":
                    return job_id
            if sum(j["status"] in {"queued", "running"} for j in self.jobs.values()) >= 3:
                raise OverflowError("Training queue is full; wait for an existing run")
            for job_id in list(self.jobs):
                if len(self.jobs) >= 20 and self.jobs[job_id]["status"] in {"complete", "error"}:
                    del self.jobs[job_id]
            job_id = uuid.uuid4().hex
            self.jobs[job_id] = {"key": key, "status": "queued"}

        def execute():
            with self.lock:
                self.jobs[job_id]["status"] = "running"
            try:
                result = run_learning_experiment(*args)
                with self.lock:
                    self.jobs[job_id].update(status="complete", result=result)
            except Exception as exc:
                with self.lock:
                    self.jobs[job_id].update(status="error", error=str(exc))
        self.executor.submit(execute)
        return job_id

    def submit_ris(self,payload):
        args=validate_ris_request(payload)
        key='ris:'+json.dumps(payload,sort_keys=True,allow_nan=False)
        with self.lock:
            for job_id,job in self.jobs.items():
                if job['key']==key and job['status']!='error':return job_id
            if sum(j['status'] in {'queued','running'} for j in self.jobs.values())>=3:
                raise OverflowError('Training queue is full; wait for a current run')
            for old in list(self.jobs):
                if len(self.jobs)>=20 and self.jobs[old]['status'] in {'complete','error'}:
                    del self.jobs[old]
            job_id=uuid.uuid4().hex
            self.jobs[job_id]={'key':key,'status':'queued','progress':'Waiting for Python worker'}
        def execute():
            from vlc.ris_experiments import run_ris_study
            c,bob,eve,sigma,slots,seeds,ris,target,penalty,secrecy=args
            def progress(message):
                with self.lock:self.jobs[job_id]['progress']=message
            try:
                with self.lock:self.jobs[job_id]['status']='running'
                # Each browser study gets isolated checkpoint files. Its exact
                # noise override is passed unchanged to all comparison schemes.
                with tempfile.TemporaryDirectory(prefix='owc-ris-study-') as folder:
                    scenarios=[{'name':'interactive','bob':bob.tolist(),'eve':eve.tolist(),
                                'sigma_B_sq':sigma}]
                    result=run_ris_study(config=c,ris_config=ris,slots=slots,seeds=seeds,
                        scenarios=scenarios,output_dir=folder,qos_ber_max=target,qos_penalty=penalty,
                        secrecy_target=secrecy,progress=progress)
                with self.lock:self.jobs[job_id].update(status='complete',result=result)
            except Exception as error:
                with self.lock:self.jobs[job_id].update(status='error',error=str(error))
        self.executor.submit(execute)
        return job_id


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def reply(self, status, body):
        raw = json.dumps(body, default=json_value, allow_nan=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def valid_origin(self):
        port = self.server.server_port
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        origin = self.headers.get("Origin")
        return self.headers.get("Host") in hosts and (origin is None or origin in {f"http://{h}" for h in hosts})

    def do_GET(self):
        if not self.valid_origin():
            return self.reply(403, {"error": "Use the local simulation address"})
        if self.path == "/api/status":
            return self.reply(200, {"engine": "Python CNN + DND", "paper_reproduction_verified": False})
        if self.path.startswith("/api/jobs/"):
            with self.server.lock:
                job = self.server.jobs.get(self.path.split("/")[-1])
                result = {k: v for k, v in job.items() if k != "key"} if job else None
            return self.reply(200 if result else 404, result or {"error": "Unknown job"})
        name = "index.html" if self.path in {"/", "/index.html"} else "visualizer.html" if self.path == "/visualizer.html" else 'ris.html' if self.path in {'/ris','/ris.html'} else None
        if name is None:
            return self.reply(404, {"error": "Not found"})
        raw = (ROOT / name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        if not self.valid_origin():
            return self.reply(403, {"error": "Cross-origin simulation requests are not allowed"})
        if self.path not in {"/api/experiment",'/api/ris/experiment','/api/ris/metrics'}:
            return self.reply(404, {"error": "Not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16384:
                raise ValueError("Request body must be 1..16384 bytes")
            payload = json.loads(self.rfile.read(length))
            if self.path=='/api/ris/metrics':
                return self.reply(200,ris_metrics(payload))
            job_id = self.server.submit_ris(payload) if self.path=='/api/ris/experiment' else self.server.submit(payload)
            self.reply(202, {"job_id": job_id})
        except OverflowError as exc:
            self.reply(429, {"error": str(exc)})
        except (ValueError, TypeError) as exc:
            self.reply(400, {"error": str(exc)})


def start_server():
    server = SimulationServer()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_port}/"


def serve(open_browser=True):
    server, url = start_server()
    print(f"VLC simulation: {url}\nPress Ctrl+C to stop. Published curves are not certified.", flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    serve()
