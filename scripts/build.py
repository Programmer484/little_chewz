#!/usr/bin/env python3
"""Generate from editable JSON. Never write an output back into content/."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'exports';OUT.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('what',choices=['teacher','companions']);p.add_argument('--lesson')
a=p.parse_args()
if a.what=='teacher':
 if not a.lesson: p.error('--lesson path required for teacher output')
 src=(ROOT/a.lesson).resolve()
 if not src.exists():p.error(f'missing lesson {src}')
 cmd=[sys.executable,str(ROOT/'scripts/renderers/teacher_guide.py'),'--root',str(ROOT),'--content',str(src),'--output',str(OUT/f'{src.parent.name}-teacher-guide.pdf')]
 subprocess.run(cmd,check=True)
else:
 for src in sorted(ROOT.glob('content/**/resources/teacher_companion/*.json')):
  cmd=[sys.executable,str(ROOT/'scripts/renderers/teacher_companion.py'),str(src),'-o',str(OUT/f'{src.stem}.pdf'),'--registry',str(ROOT/'catalog/resources.json')]
  subprocess.run(cmd,check=True)
