#!/usr/bin/env python3
"""Deterministic force and reference-outline tables; runtime physics is PDP-1."""
from pathlib import Path
import math
ROOT=Path(__file__).resolve().parents[1]
def generate():
    lines=['// Q17 factor dt^2/r^3; dt=1/16; index=floor(128*r^2).',
           'bank 2','0000/','force_table,']
    for i in range(1024):
        r2=max(i+.5,8)/128
        lines.append(f'        0d{round(512/r2**1.5)}')
    lines+=['bank 0']
    (ROOT/'generated/force.ac').write_text('\n'.join(lines)+'\n')
    lines=['// Screen-space closed outlines, reference circle and central body.']
    for name,r,n in [('planet',40,16)]:
        points=[(round(512+r*math.cos(2*math.pi*k/n)),round(530+r*math.sin(2*math.pi*k/n))) for k in range(n+1)]
        lines += [name+'_outline,']
        for (x,y),(u,v) in zip(points,points[1:]):lines.append(f'        0d{x}; 0d{y}; 0d{u}; 0d{v}')
    (ROOT/'generated/outlines.ac').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':generate()
