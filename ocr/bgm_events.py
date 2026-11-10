"""Export the existing quartet as timed events, repeating its final 8 bars if needed."""
import argparse
import json
from pathlib import Path
import make_bgm as b

p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('--seconds',type=float,default=52)
a=p.parse_args();parts=b.build();b.check(parts)
events=[]
beat=60/b.BPM
for ch, notes in enumerate(parts):
    expanded=list(notes)
    repeat_start=11*b.BAR
    repeat_length=8*b.BAR
    cursor=19*b.BAR
    while (cursor+b.LEAD)/b.TPB*beat < a.seconds:
        expanded += [(cursor+t-repeat_start,n,p,v) for t,n,p,v in notes if t>=repeat_start]
        cursor+=repeat_length
    for t,n,note,vel in expanded:
        start=(t+b.LEAD)/b.TPB*beat; end=(t+n+b.LEAD)/b.TPB*beat
        if start<a.seconds:
            events.extend([(start,ch,note,vel),(min(end,a.seconds),ch,note,0)])
Path(a.output).write_text(json.dumps({'seconds':a.seconds,'parts':b.PARTS,'events':sorted(events)}),encoding='utf-8')
print(len(events),'note events')
