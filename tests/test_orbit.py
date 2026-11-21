#!/usr/bin/env python3
"""Execute actual PDP-1 dynamics and P1GL display lists in an isolated CPU."""
import json,math,os,re,subprocess
from pathlib import Path
from rim import tape_memory,write_mem,read_mem
from type340_model import read_lists,decode
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'build';MASK=(1<<18)-1

def enc(v):return v if v>=0 else MASK^-v
def dec(v):return v if v<1<<17 else -(MASK^v)
def trunc(v,d):return (abs(v)//d)*(-1 if v<0 else 1)
def symbols(p):return {f[2]:int(f[0],8) for l in p.read_text().splitlines() if len(f:=l.split())==4 and re.fullmatch('[0-7]{6}',f[0])}
def run(mem,entry,patch=None,ss=0,env_extra=None):
    write_mem(B/'code.mem',mem);write_mem(B/'patch.mem',patch or {})
    r=subprocess.run([str(B/'runner'),'code.mem','patch.mem','out.mem',f'{entry:o}'],cwd=B,env=dict(os.environ,ORBIT_SENSE_SWITCHES=str(ss),**(env_extra or {})),text=True,capture_output=True,check=True)
    assert 'overflow=0' in r.stdout,r.stdout
    return read_mem(B/'out.mem')
def model(vy,n):
    x,y,vx=16384,0,-32;status=0;rows=[]
    for _ in range(n):
        if not status:
            x+=vx;y+=vy
            i=((x*x//131072)+(y*y//131072))//16
            if i<8:status=1
            elif i>=648:status=2
            else:
                k=round(512/((i+.5)/128)**1.5)
                vx-=trunc((abs(x*k)+65536)*(1 if x>=0 else -1),131072);vy-=trunc((abs(y*k)+65536)*(1 if y>=0 else -1),131072)
        rows.append((x,y))
    return rows,status

def main():
    report=[];circular_out=None
    for name,vy in [('circle',1024),('ellipse',768),('escape',1536),('impact',200)]:
        subprocess.run([os.environ['AM1'],'-d','-S','-DORBIT_TEST','-DORBIT_STEPS=0d2000',f'-DORBIT_VY=0d{vy}','../src/orbit.am1'],cwd=B,check=True,capture_output=True)
        mem,entry=tape_memory(B/'orbit.rim');sy=symbols(B/'orbit.sym');out=run(mem,entry)
        expected,state=model(vy,2000)
        trace=[(dec(out[0o30000+2*i]),dec(out[0o30001+2*i])) for i in range(2000)]
        assert trace==expected,(name,next((i,a,b) for i,(a,b) in enumerate(zip(trace,expected)) if a!=b))
        assert out[sy['status']]==state
        radii=[math.hypot(x,y)/16384 for x,y in trace]
        if name=='circle':assert state==0 and max(abs(r-1) for r in radii)<.06
        if name=='ellipse':assert state==0 and min(radii)<.5 and max(radii)<1.05
        if name=='escape':assert state==2
        if name=='impact':assert state==1
        report.append(dict(case=name,steps=out[sy['steps']],min_radius=min(radii),max_radius=max(radii),status=state,cpu_matches_integer_model=True))
    # Reassemble the production program before executing controls and rendering.
    subprocess.run([os.environ['AM1'],'-d','-S','../src/orbit.am1'],cwd=B,check=True,capture_output=True)
    mem,entry=tape_memory(B/'orbit.rim');sy=symbols(B/'orbit.sym')
    def driver(body,patch=None,ss=0):
        (B/'driver.am1').write_text(f'Orbit test driver\n7730/\nlem\nlsm\ncbs\njsp {sy["menu_init"]:o}\n'+body+'\nhlt\nconstants\nstart 07730:0\n')
        subprocess.run([os.environ['AM1'],'-d','driver.am1'],cwd=B,check=True,capture_output=True)
        image=dict(mem);d,go=tape_memory(B/'driver.rim');image.update({a:w for a,w in d.items() if a<0o7751})
        return run(image,go,patch,ss)
    for ss,expected in [(0,1024),(0o10,896),(0o4,1152),(0o1,768),(0o2,1024)]:
        out=driver(f"jsp {sy['reset_circle']:o}\njsp {sy['controls']:o}\njsp {sy['controls']:o}",ss=ss)
        assert dec(out[sy['vy']])==expected,(ss,dec(out[sy['vy']])) # held switch acts once
    out=driver(f"jsp {sy['reset_circle']:o}\njsp {sy['render']:o}\njsp {sy['gframe_refresh']:o}")
    assert out[sy['gf_fault']]==0 and out[sy['buffer_guard']]==0o123456
    lists=read_lists(B/'lists.trace');assert len(lists)==1
    scene=decode(lists[0]);vector_count=len(scene['vectors'])
    assert vector_count>100
    for a,w in mem.items():
        if (sy['gv_font_index']<=a<sy['gv_font_index']+1759 or 0o20000<=a<0o22000):assert out[a]==w,('font/force mutation',a)
    for state in (1,2):
        out=driver(f"jsp {sy['reset_circle']:o}\nlaw {state}\ndac {sy['status']:o}\njsp {sy['render']:o}\njsp {sy['gframe_refresh']:o}")
        assert out[sy['gf_fault']]==0
    for ss,count in ((0,0),(0o40,3)):
        subprocess.run([os.environ['AM1'],'-d','-S','-DORBIT_FRAME_TEST','../src/orbit.am1'],cwd=B,check=True,capture_output=True)
        m,e=tape_memory(B/'orbit.rim');s=symbols(B/'orbit.sym');o=run(m,e,ss=ss)
        assert o[s['frames']]==3 and o[s['steps']]==count and o[s['gf_fault']]==0
    subprocess.run([os.environ['AM1'],'-d','-S','-DORBIT_FRAME_TEST','-DORBIT_FRAME_COUNT=0d140','../src/orbit.am1'],cwd=B,check=True,capture_output=True)
    m,e=tape_memory(B/'orbit.rim');s=symbols(B/'orbit.sym');o=run(m,e,ss=0o40)
    assert o[s['frames']]==140 and o[s['steps']]==140
    assert o[s['gf_fault']]==0 and o[s['buffer_guard']]==0o123456
    assert 'trail_x' not in s and 'fade_update' not in s
    lists=read_lists(B/'lists.trace');assert len(lists)==140
    expected,_=model(1024,140)
    for words,(x,y) in zip(lists,expected):
        d=decode(words);assert len(d['vectors'])==vector_count, 'software trail geometry accumulated'
        sx=512+trunc(x,128)+trunc(x,512);syy=530+trunc(y,128)+trunc(y,512)
        assert d['vectors'][-2:]==[((sx-4,syy),(sx+4,syy)),((sx,syy-4),(sx,syy+4))]
        assert all(0<=v<=1023 for edge in d['vectors'] for p in edge for v in p)
    report.append(dict(case='phosphor_only_animation',frames=140,marker_positions_checked=140,fixed_vector_count=vector_count,capacity=1540,max_words=max(map(len,lists)),fault=0))
    report.append(dict(case='production_loop',paused_steps=0,running_steps=3,frames_each=3))
    subprocess.run([os.environ['AM1'],'-d','-S','../src/orbit.am1'],cwd=B,check=True,capture_output=True)
    (B/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
