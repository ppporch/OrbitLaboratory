#!/usr/bin/env python3
"""Bill's actual PENMENU, polled pen input and production action dispatch."""
import json,os,subprocess
from test_orbit import B,run,symbols,dec
from rim import tape_memory

def main():
    report=[]
    cases=[('pause',0,0o40,1,0,1020,False),('run',0,0,7,0o40,None,False),
           ('step',1,0,1,0,1020,False),('slower',2,0,0,0,896,False),
           ('faster',3,0,0,0,1152,False),('circle',4,0,0,0,1024,True),
           ('ellipse',5,0,0,0,768,False),('off_menu',7,0,0,0,1024,False)]
    for name,column,ss,steps,enabled,vy,ellipse in cases:
        flags=['-DORBIT_FRAME_TEST','-DORBIT_FRAME_COUNT=0d8']+(['-DORBIT_ELLIPSE'] if ellipse else [])
        subprocess.run([os.environ['AM1'],'-d','-S',*flags,'../src/orbit.am1'],cwd=B,check=True,capture_output=True)
        memory,entry=tape_memory(B/'orbit.rim');s=symbols(B/'orbit.sym')
        out=run(memory,entry,ss=ss,env_extra={'ORBIT_TEST_PEN_COLUMN':str(column)})
        assert out[s['frames']]==8 and out[s['steps']]==steps,(name,out[s['steps']])
        assert out[s['run_enabled']]==enabled and out[s['gf_fault']]==0
        if vy is not None:assert dec(out[s['vy']])==vy,(name,dec(out[s['vy']]))
        report.append(dict(case=name,steps=steps,held_pen_fires_once=True,frames=8))
    subprocess.run([os.environ['AM1'],'-d','-S','../src/orbit.am1'],cwd=B,check=True,capture_output=True)
    (B/'menu-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
