"""Train a public-data NeuroGravity-style baseline.

The implementation reuses only the model ideas/classes from resources/NeuroGravity:
learned gravity G/alpha terms, node context fusion and a link predictor.  It
consumes the prepared public DeepGravity New York data and never loads the
NeuroGravity repository's data or checkpoints.
"""
from __future__ import annotations
import argparse, json, random, time
from pathlib import Path
import numpy as np
import torch
from torch import nn

from mapagents.data import load_dataset
from mapagents.training import ODStore, raw_inputs
from mapagents.programs import SpatialCompiler, default_program
from mapagents.model import FeatureTransform
from mapagents.metrics import matrix_metrics, aggregate_metrics

class NeuroGravityPublic(nn.Module):
    def __init__(self, d: int, hidden=128):
        super().__init__()
        # G and alpha networks mirror metaGravity; the final head is the
        # NeuroGravity link predictor that fuses physics and pair context.
        self.g_net = nn.Sequential(nn.Linear(d, hidden), nn.SiLU(), nn.Linear(hidden, hidden//2), nn.SiLU(), nn.Linear(hidden//2,1))
        self.a_net = nn.Sequential(nn.Linear(d, hidden), nn.SiLU(), nn.Linear(hidden, hidden//2), nn.SiLU(), nn.Linear(hidden//2,1))
        self.link = nn.Sequential(nn.Linear(d+2, hidden), nn.SiLU(), nn.Linear(hidden, hidden//2), nn.SiLU(), nn.Linear(hidden//2,1))
    def forward(self, z):
        g = self.g_net(z).squeeze(-1)
        alpha = torch.nn.functional.softplus(self.a_net(z).squeeze(-1))
        # distance is the final raw input column in raw_inputs (before the
        # pair compiler columns); its transformed value is still a stable
        # monotone proxy, and physics is learned jointly from all inputs.
        phys = g - alpha * z[:, 2]
        return phys + self.link(torch.cat([z, phys[:,None]], dim=-1)).squeeze(-1)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data',default='data/processed/new_york'); ap.add_argument('--out',default='runs/new_york_baselines/neurogravity'); ap.add_argument('--epochs',type=int,default=20); ap.add_argument('--seed',type=int,default=1234); ap.add_argument('--device',default='cuda'); ap.add_argument('--sample-destinations',type=int,default=512)
    a=ap.parse_args(); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
    if a.device.startswith('cuda') and not torch.cuda.is_available(): raise RuntimeError('CUDA unavailable; run in my-neuro')
    device=torch.device(a.device)
    data=load_dataset(Path(a.data)); store=ODStore(data)
    compiler=SpatialCompiler(data,None,out/'spatial_cache'); bundle=compiler.compile(default_program(data))
    tf=FeatureTransform.fit(np.concatenate([raw_inputs(bundle,store.regions[r],np.array([i]),np.arange(len(store.regions[r].zone_ids))) for r,i in store.examples('train',True)[:200]]),bundle.input_ids)
    model=NeuroGravityPublic(len(bundle.input_ids)).to(device); opt=torch.optim.AdamW(model.parameters(),lr=2e-4,weight_decay=1e-5)
    examples=store.examples('train',True); started=time.perf_counter(); history=[]
    for ep in range(a.epochs):
        rng=np.random.default_rng(a.seed+ep); rng.shuffle(examples); model.train(); loss_sum=mass=0.
        for r,i in examples:
            reg=store.regions[r]; dest=rng.choice(len(reg.zone_ids),size=min(a.sample_destinations,len(reg.zone_ids)),replace=False); y=reg.flows[i,dest]
            if y.sum()<=0: continue
            x=torch.as_tensor(tf.transform(raw_inputs(bundle,reg,np.full(len(dest),i),dest)),device=device)
            yt=torch.as_tensor(y,dtype=torch.float32,device=device); logits=model(x); logp=torch.log_softmax(logits,0); loss=-(yt*logp).sum()/yt.sum(); opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),5.); opt.step(); loss_sum+=float(loss.detach())*float(yt.sum()); mass+=float(yt.sum())
        rec={'epoch':ep+1,'nll_per_trip':loss_sum/max(mass,1.),'elapsed_seconds':time.perf_counter()-started}; history.append(rec); print(f'epoch {ep+1}/{a.epochs} nll={rec["nll_per_trip"]:.5f}',flush=True)
    def evaluate(split):
        model.eval(); records=[]
        with torch.inference_mode():
            for r,rows in store.rows_by_region(split).items():
                reg=store.regions[r]; pred=[]
                for i in rows:
                    x=torch.as_tensor(tf.transform(raw_inputs(bundle,reg,np.full(len(reg.zone_ids),i),np.arange(len(reg.zone_ids)))),device=device); p=torch.softmax(model(x),0).cpu().numpy()*reg.flows[i].sum(); pred.append(p)
                pred=np.asarray(pred); truth=reg.flows[rows]; records.append({'region_id':r,**matrix_metrics(truth,pred,reg.distances[rows],reg.zone_ids[rows],reg.zone_ids)})
        return aggregate_metrics(records)
    result={'model':'NeuroGravity-public-reimplementation','data':str(Path(a.data).resolve()),'seed':a.seed,'training':{'epochs':a.epochs,'elapsed_seconds':time.perf_counter()-started},'validation':evaluate('validation'),'held_out':evaluate('test'),'input_columns':len(bundle.input_ids)}
    (out/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8'); (out/'training.json').write_text(json.dumps(history,indent=2),encoding='utf-8'); torch.save(model.state_dict(),out/'model.pt'); print(json.dumps(result['held_out'],indent=2))
if __name__=='__main__': main()
