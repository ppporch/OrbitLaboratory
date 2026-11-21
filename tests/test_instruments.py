#!/usr/bin/env python3
"""Panel formatting, leapfrog velocity correction and energy classification."""
import json,math,os,subprocess
from pathlib import Path
from test_orbit import ROOT,B,symbols,run,enc,dec
from rim import tape_memory

def text_at(out,a):
    return ''.join(chr((out[a+n//2]>>(9 if n%2==0 else 0))&511) for n in range(30))

def main():
    memory,_=tape_memory(B/'orbit.rim');s=symbols(B/'orbit.sym')
    (B/'panel-driver.am1').write_text(f'''Instrument test driver
7730/
lem
lsm
cbs
jsp {s['render']:o}
hlt
start 07730:0
''')
    subprocess.run([os.environ['AM1'],'-d','panel-driver.am1'],cwd=B,check=True,capture_output=True)
    driver,entry=tape_memory(B/'panel-driver.rim');image=dict(memory);image.update({a:w for a,w in driver.items() if a<0o7751})
    def glyphs_match(out):
        text=text_at(out,s['instrument_text']);base=out[s['instrument_start']]
        for n,c in enumerate(text):
            assert out[base+5*n+3]==memory[s['gt_char_map']+2*(ord(c)-32)],('stale reading glyph',n,c)
    report=[]
    cases=[('circle',16384,0,-32,1024,64,0,'1.00','1.00','BOUND'),
           ('ellipse',16384,0,-32,768,64,0,'1.00','0.75','BOUND'),
           ('escape',16384,0,-32,1536,64,0,'1.00','1.50','ESCAPING'),
           ('near_escape',16384,0,-32,1448,64,0,'1.00','1.41','NEAR ESC'),
           ('double_radius',32768,0,-8,1024,16,0,'2.00','1.00','NEAR ESC')]
    for name,x,y,vx,vy,ax,ay,rt,vt,kind in cases:
        patch={s[k]:enc(v) for k,v in dict(px=x,py=y,vx=vx,vy=vy,ax=ax,ay=ay,screen_x=512,screen_y=530).items()}
        out=run(image,entry,patch)
        text=text_at(out,s['instrument_text'])
        assert text[5:9]==rt and text[16:20]==vt and text[22:].strip()==kind,(name,text)
        assert out[s['gf_fault']]==0
        glyphs_match(out)
        for k in ('px','py','vx','vy','ax','ay'):assert out[s[k]]==patch[s[k]],('instrument changed physics',k)
        report.append(dict(case=name,text=text))
    # Independent physical-value checks away from the launch axes.
    import random
    rng=random.Random(340)
    for n in range(24):
        radius=rng.uniform(.35,2.25);theta=rng.uniform(-math.pi,math.pi)
        x=round(16384*radius*math.cos(theta));y=round(16384*radius*math.sin(theta))
        vx=rng.randint(-2000,2000);vy=rng.randint(-2000,2000)
        patch={s[k]:enc(v) for k,v in dict(px=x,py=y,vx=vx,vy=vy,ax=0,ay=0,screen_x=512,screen_y=530).items()}
        out=run(image,entry,patch);text=text_at(out,s['instrument_text'])
        assert abs(float(text[5:9])-math.hypot(x,y)/16384)<.016,(n,text,radius)
        assert abs(float(text[16:20])-math.hypot(vx,vy)/1024)<.025,(n,text,vx,vy)
    report.append(dict(case='quadrant_accuracy',cases=24,radius_error_below=.016,speed_error_below=.025))
    # Sampling is throttled: a second render after a speed change retains the
    # previous text until the next sample, while the display continues updating.
    first=run(image,entry,{s['px']:16384,s['vy']:1024,s['screen_x']:512,s['screen_y']:530})
    before=text_at(first,s['instrument_text'])
    second=dict(first);second[s['vy']]=1536
    out=run(second,entry)
    assert text_at(out,s['instrument_text'])==before
    second[s['i_countdown']]=0
    out=run(second,entry)
    assert 'ESCAPING' in text_at(out,s['instrument_text'])
    glyphs_match(out)
    base=out[s['instrument_start']]
    changed={a for a in range(base,base+150) if out[a]!=first[a]}
    assert changed and all((a-base)%5==3 for a in changed), 'panel layout was rebuilt or corrupted'
    report.append(dict(case='throttled_updates',frames_per_sample=5,physics_unchanged=True))
    (B/'instrument-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
