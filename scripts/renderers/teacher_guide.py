#!/usr/bin/env python3
"""Little Chewz: the approved PDF-native teacher-guide system.

No image generation. Teacher pages use the established Lato type, measured text,
vector rules, the original column geometry, and aligned action labels. Covers are
provided PDFs. Each lesson folder holds its own content JSON and cover PDF.
Edit lesson JSON rather than the design. Font files are not distributed.

Requires Python 3.10+, PyMuPDF, and a locally installed Lato family. Use --font-dir
to point to your own installed fonts. Runs outside /mnt/data without code edits.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from typing import Any
import fitz

A4_W,A4_H=595.28,841.89
L,R,TOP,BOTTOM=44.,551.,36.,807.
PAGE_W=R-L
BG=(.988,.981,.971);BLACK=(.118,.122,.126);MID=(.39,.40,.405)
SOFT=(.77,.77,.77);CORAL=(.91,.405,.33);DEEP=(.77,.31,.255)
ACTIONS_X=L+61;CONTENT_X=L+109;CONTENT_WIDTH=R-CONTENT_X
# Linked resources (including MORE) and ordinary DO instructions share body sizing.
FLOW_BODY_SIZE=11.1
FLOW_ASK_SIZE=11.5
FONT_FILES={};FONTMETRICS={};FONTNAMES={}
AUDIT=[]

# Editable section palette (sRGB hex). Light colors are intentionally deepened
# so fine rules, step numbers and action labels remain legible when printed.
SECTION_COLOR_HEX = {
    'activate': '#E66654',
    'p1': '#C6548F',  # Pink: Set the Table
    'p2': '#8C5EBD',  # Purple: Secret Ingredients
    'p3': '#B0851F',  # Dark gold: The Showdown
    'p4': '#59874C',  # Green: Chew on This
    'p5': '#478FB0',  # Blue: Plate It Forward
    'celebrate': '#E66654',
    'next': '#E66654',
}
def section_accent(key):
    value = SECTION_COLOR_HEX.get(key, '#E66654').lstrip('#')
    if len(value) != 6: raise ValueError(f'Invalid accent color for {key}: {value}')
    return tuple(int(value[i:i+2], 16)/255. for i in (0, 2, 4))

class LayoutError(ValueError):pass

def configure_fonts(directory:Path|None=None):
    global FONT_FILES,FONTMETRICS,FONTNAMES
    candidates=[directory,Path(os.environ.get('LITTLE_CHEWZ_FONT_DIR','/usr/share/fonts/truetype/lato')),Path('/Library/Fonts'),Path('C:/Windows/Fonts')]
    family={'regular':'Regular','medium':'Medium','semibold':'Semibold','bold':'Bold','heavy':'Heavy','italic':'Italic'}
    for root in candidates:
        if root and all((root/f'Lato-{s}.ttf').is_file() for s in family.values()):
            FONT_FILES={k:root/f'Lato-{s}.ttf' for k,s in family.items()};break
    else:raise FileNotFoundError('Lato fonts not found. Install Lato and pass --font-dir; no fonts are bundled.')
    FONTNAMES={k:'LC'+k.title() for k in FONT_FILES}
    FONTMETRICS={k:fitz.Font(fontfile=str(v)) for k,v in FONT_FILES.items()}

def tw(s,size=11.,font='regular'):return FONTMETRICS[font].text_length(str(s),fontsize=size)

def wrap(s,w,size=11.,font='regular'):
    if w<=0:raise LayoutError(f'Non-positive text width {w}')
    lines=[]
    for paragraph in str(s).split('\n'):
        if not paragraph.strip():lines.append('');continue
        line=''
        for word in paragraph.split():
            if tw(word,size,font)>w+.01:raise LayoutError(f'Unbreakable word exceeds width: {word!r}')
            trial=(line+' '+word).strip()
            if tw(trial,size,font)<=w+.01:line=trial
            else:lines.append(line);line=word
        if line:lines.append(line)
    return lines

def newp(doc):
    p=doc.new_page(width=A4_W,height=A4_H);p.draw_rect(p.rect,color=None,fill=BG)
    for k,v in FONT_FILES.items():p.insert_font(fontfile=str(v),fontname=FONTNAMES[k])
    return p

def txt(p,s,x,y,size=11.,font='regular',color=BLACK,max_right=R):
    s=str(s);width=tw(s,size,font)
    if x+width>max_right+.15:raise LayoutError(f'Page {p.number+1 if p is not None else "?"}: text exceeds right bound: {s!r} ({x+width:.1f}>{max_right:.1f})')
    if y+size>816:raise LayoutError(f'Text exceeds bottom margin: {s[:70]!r} at {y:.1f}')
    if p is not None:
        p.insert_text((x,y+size),s,fontname=FONTNAMES[font],fontsize=size,color=color)
        AUDIT.append({'page':p.number,'x':x,'y':y,'right':x+width,'bottom':y+size,'text':s})
    return y+size

def para(p,s,x,y,w,size=11.,lh=None,font='regular',color=BLACK):
    lh=lh or size*1.48
    for value in wrap(s,w,size,font):
        if value:txt(p,value,x,y,size,font,color,max_right=x+w)
        y+=lh
    return y

def line(p,y,x=L,x2=R,c=SOFT,thick=.63):
    if p is not None:p.draw_line((x,y),(x2,y),color=c,width=thick)

def section(p,title,x,y,accent=CORAL):
    txt(p,title,x,y,13.4,'bold')
    line(p,y+19.7,x,x+32,accent,2.)
    return y+34

def label(p,title,x,y,color=DEEP):return txt(p,title,x,y,9.1,'heavy',color)

def hdr(p,eyebrow,title,sub=None,accent=CORAL):
    label(p,eyebrow.upper(),L,29,MID)
    size=min(24.,(PAGE_W-86)/tw(title,24.,'heavy')*24.)
    if size<16:raise LayoutError(f'Header is too long: {title}')
    txt(p,title,L,46,size,'heavy',max_right=R-86)
    line(p,90,c=accent,thick=1.17)
    if sub:txt(p,sub,L,106,10.6,'regular',MID)

def resolve(item,registry):
    record=dict(registry.get(item.get('ref'),{}));record.update(item)
    if not record.get('title'):raise ValueError(f'Resource has no title: {item}')
    return record

def annotate(p,rec,rect):
    if p is None:return
    if rec.get('url'):
        if not rec['url'].startswith(('https://','http://')):raise ValueError('Unsupported URL scheme')
        p.insert_link({'kind':fitz.LINK_URI,'from':rect,'uri':rec['url']})
    elif rec.get('file'):
        p.insert_link({'kind':fitz.LINK_GOTOR,'from':rect,'file':rec['file'],'page':int(rec.get('page',0)),'to':fitz.Point(0,0),'zoom':0.})
    else:raise ValueError(f'Unresolved resource; do not invent a link: {rec}')

def resource_line(p,item,reg,x,y,w,size=10.5,strict=False,description_size=None):
    """Measured mixed-style resource name — description. Underline only linked text.

    Page-2 rows are deliberately single-line and fail rather than wrapping a dash.
    Flow descriptions can wrap naturally while the full resource label stays intact.
    """
    rec=resolve(item,reg);name=rec['title'];desc=rec.get('description','')
    name_w=tw(name,size,'semibold');ds=description_size or size-.5
    if name_w>w:raise LayoutError(f'Resource title too long: {name}')
    suffix=' — '+desc if desc else ''
    if strict and name_w+tw(suffix,ds)>w+.01:
        raise LayoutError(f'Page-2 resource must stay on one line ({name_w+tw(suffix,ds):.1f}>{w:.1f} pt): {name} — {desc}. Shorten the description.')
    txt(p,name,x,y,size,'semibold',max_right=x+w)
    line(p,y+size+2.1,x,x+name_w,BLACK,.52)
    annotate(p,rec,fitz.Rect(x,y-1,x+name_w,y+size+4))
    if not suffix:return y+15.2
    remaining=w-name_w
    if tw(suffix,ds)<=remaining:
        txt(p,suffix,x+name_w,y,ds,'regular',MID,max_right=x+w);return y+15.2
    # Put as much of the description as possible beside the label; never leave
    # an em dash alone on a line. Continuations start on the same content grid.
    words=desc.split();first=' —'
    used=0
    for word in words:
        trial=first+' '+word
        if tw(trial,ds)>remaining:break
        first=trial;used+=1
    if used:
        txt(p,first,x+name_w,y,ds,'regular',MID,max_right=x+w)
        return para(p,' '.join(words[used:]),x,y+16,w,size=ds,lh=15.,color=MID) if used<len(words) else y+16
    return para(p,'— '+desc,x,y+17,w,size=ds,lh=15.,color=MID)

def heading(p,title,x,y):
    txt(p,title,x,y,11.9,'heavy',BLACK);return y+30

def normalized_assessment(value):
    """Optional: omit/null/blank/empty list hides section; text or bullet list shows it."""
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, list):
        if not all(isinstance(item, str) for item in value):
            raise ValueError('Assessment list items must all be strings')
        entries=[item.strip() for item in value if item.strip()]
        return entries or None
    raise ValueError('Assessment must be a string, list of strings, null, or omitted')


def render_assessment(p,assessment,x,y,width):
    """Use existing lesson evidence; optional resource-by-resource checks may be bullets."""
    if isinstance(assessment, str):
        return para(p,assessment,x,y,width,size=11.15,lh=17.2)
    for item in assessment:
        y=para(p,'•  '+item,x,y,width,size=9.95,lh=14.35)+3.4
    return y


def overview(doc,d,reg):
    p=newp(doc)
    accent=section_accent(d["key"])
    if d['key'].startswith('p') and d['key'][1:].isdigit():
        part,topic=d['title'].split(' / ',1)
        hdr(p,part+' / TEACHER GUIDE',topic+' / AT A GLANCE')
    else:hdr(p,'TEACHER GUIDE',d['title']+' / AT A GLANCE')
    meta=f"GRADES {d['grade']}    |    {d['duration'].upper()}    |    {d['print_note']}"
    para(p,meta,L,107,PAGE_W,size=9.55,lh=13.,font='bold',color=MID)
    line(p,144)
    y=section(p,'Learning goal',L,168,accent)
    y=para(p,d['goal'],L,y,PAGE_W,size=11.6,lh=17.5)+25
    line(p,y);top=y+28
    x2=319.;left_w=x2-L-27;right_w=R-x2
    ly=section(p,'Learning outcomes',L,top,accent)
    for i,value in enumerate(d['outcomes'],1):
        txt(p,f'{i:02d}',L,ly,10.7,'bold',accent)
        ly=para(p,value,L+30,ly,left_w-32,size=11.2,lh=17)+21
    ry=section(p,'Preparation',x2,top,accent)
    ry=heading(p,'CORE RESOURCES',x2,ry)
    for it in d['core']:
        resource_line(p,it,reg,x2,ry,right_w,size=10.4,strict=True,description_size=9.55);ry+=26
    ry+=4
    ry=heading(p,d.get('prep_heading','OPTIONAL PREPARATION'),x2,ry)
    for it in d['optional_prep']:
        resource_line(p,it,reg,x2,ry,right_w,size=10.4,strict=True,description_size=9.55);ry+=26
    if d.get('prep_note'):
        ry=para(p,d['prep_note'],x2,ry,right_w,size=9.2,lh=13.4,font='italic',color=MID)+7
    line(p,max(ly,ry)+6,x2-19,x2-19) if False else None
    p.draw_line((x2-19,top-2),(x2-19,max(ly,ry)+6),color=SOFT,width=.55)
    below=max(ly,ry)+28;line(p,below)
    y=section(p,'Teaching focus',L,below+23,accent)
    assessment=normalized_assessment(d.get('assessment'))
    # Assessment is entirely optional; it never adds a Teaching Flow activity.
    # When present, it describes evidence already available in chosen activities.
    bullet_mode=isinstance(assessment,list)
    y=para(p,d['focus'],L,y,PAGE_W,size=11.15,lh=17.2)+(8 if bullet_mode else 17 if assessment else 26)
    line(p,y)
    if assessment:
        y=section(p,'Assessment',L,y+(10 if bullet_mode else 17),accent)
        y=render_assessment(p,assessment,L,y,PAGE_W)+(5 if bullet_mode else 15)
        line(p,y)
        y+=(8 if bullet_mode else 19)
    else:
        y+=27
    label(p,'CURRICULUM CONNECTIONS',L,y,MID);y+=21
    y=para(p,' · '.join(d['curriculum']),L,y,PAGE_W,size=11.2,lh=17.5)
    if y>812:raise LayoutError(f'{d["key"]} overview exceeds page at y={y:.1f}')
    return p

def step_begin(p,step,y,accent=CORAL,separator=False):
    if separator:line(p,y)
    txt(p,f"{step['id']:02d}",L,y+16,17.5,'heavy',accent)
    value=str(step['mins']);time=value.upper() if value.upper()=='OPTIONAL' else value+' MIN'
    time_w=tw(time,9.4,'bold')
    title_w=R-ACTIONS_X-time_w-18
    title_lines=wrap(step['title'],title_w,15.5,'bold')
    for i,ln in enumerate(title_lines):txt(p,ln,ACTIONS_X,y+15+i*20,15.5,'bold',max_right=ACTIONS_X+title_w)
    txt(p,time,R-time_w,y+21,9.4,'bold',MID)
    return y+62+max(0,len(title_lines)-1)*20

def draw_step(p,step,y,reg,accent=CORAL,separator=False):
    y=step_begin(p,step,y,accent,separator)
    for row in step['rows']:
        kind=row['kind'].upper()
        if row.get('links') is not None:
            label(p,kind,ACTIONS_X,y,accent)
            for it in row['links']:
                y=resource_line(p,it,reg,CONTENT_X,y,CONTENT_WIDTH)+7.5
            y+=6
        elif kind=='QUOTE':
            # A single READ label and a continuous rule frame the entire speech.
            label(p,'READ',ACTIONS_X,y,accent);start=y
            for paragraph in row['text'].split('\n\n'):
                font='bold' if paragraph.strip()==row.get('bold_text','') else 'regular'
                y=para(p,paragraph,CONTENT_X+14,y,CONTENT_WIDTH-20,size=10.85,lh=16.8,font=font)+8.4
            if p is not None:p.draw_line((CONTENT_X-2,start),(CONTENT_X-2,y-8),color=accent,width=1.65)
            y+=6
        elif row.get('ref'):
            label(p,kind,ACTIONS_X,y,accent)
            y=resource_line(p,row,reg,CONTENT_X,y,CONTENT_WIDTH,size=FLOW_BODY_SIZE,description_size=FLOW_BODY_SIZE)+12
        else:
            label(p,kind,ACTIONS_X,y,accent)
            y=para(p,row.get('text',''),CONTENT_X,y,CONTENT_WIDTH,size=FLOW_ASK_SIZE if kind=='ASK' else FLOW_BODY_SIZE,lh=17 if kind=='ASK' else 16.,font='semibold' if kind=='ASK' else 'regular')+12
    return y+17

def bonuses(p,items,y,reg,title='MORE TIME?  YOU CHEWZ!'):
    if not items:return y
    line(p,y,thick=.65);y+=10
    txt(p,title,L,y,11.2,'bold');y+=23
    gap=20.;w=(PAGE_W-gap)/2;max_y=y
    if len(items)>2:raise LayoutError('Bonus section holds two purposeful items at most; use a separate resource for more.')
    for j,it in enumerate(items):
        x=L+j*(w+gap);rec=resolve(it,reg);title_item=dict(it);title_item['description']=''
        resource_line(p,title_item,reg,x,y,w,size=10.3)
        end=para(p,it['description'],x,y+18,w,size=9.55,lh=13.5,color=MID)
        max_y=max(max_y,end)
    return max_y

def flow(doc,d,reg):
    """Flow as many complete steps as fit, with reserved bottom padding."""
    accent=section_accent(d['key'])
    p=None; y=127.; no=0; count_on_page=0
    limit=751.
    if d['key'].startswith('p') and d['key'][1:].isdigit():
        part,topic=d['title'].split(' / ',1)
        eyebrow=(part+' · '+topic).upper()
    else:eyebrow=d['title'].upper()
    def finish_continuation():
        if p is not None:
            cue='CONTINUED ON NEXT PAGE  →'
            txt(p,cue,R-tw(cue,9.2,'semibold'),780,9.2,'semibold',MID)
    def next_page():
        nonlocal p,y,no,count_on_page
        if p is not None:finish_continuation()
        p=newp(doc);no+=1;hdr(p,eyebrow,'Teaching Flow',accent=accent)
        y=127.;count_on_page=0
    for st in d['steps']:
        if p is None:next_page()
        h=draw_step(None,st,0,reg,accent)
        if h>limit-127:raise LayoutError(f'Step too large for flow page: {st["title"]}')
        if y+h>limit:next_page()
        y=draw_step(p,st,y,reg,accent,separator=count_on_page>0)
        count_on_page+=1
    its=d.get('bonuses',[])
    if its:
        title=d.get('bonus_heading','MORE TIME?  YOU CHEWZ!')
        h=bonuses(None,its,0,reg,title)
        if y+h>801.:next_page()
        y=bonuses(p,its,y,reg,title)
    return no

def build(content:Path,registry:dict,output:Path|None=None):
    global AUDIT
    AUDIT=[];d=json.loads(content.read_text(encoding='utf8'))
    # Paths in lesson JSON are relative to that lesson's own directory.
    out=output or content.parent/d['output'];out.parent.mkdir(parents=True,exist_ok=True)
    cover=content.parent/d['cover']
    if not cover.exists():raise FileNotFoundError(cover)
    doc=fitz.open()
    if cover.suffix.lower() in {'.png','.jpg','.jpeg'}:
        # A real image asset is source; we generate the cover PDF page in memory.
        with fitz.open(cover) as pic:
            r=pic[0].rect
        page=doc.new_page(width=A4_W,height=A4_H)
        page.insert_image(page.rect,filename=str(cover),keep_proportion=False)
    else:
        with fitz.open(cover) as c:doc.insert_pdf(c,from_page=0,to_page=0,links=False)
    overview(doc,d,registry);flow(doc,d,registry)
    for pn in range(1,len(doc)):
        p=doc[pn];counter=f'{pn+1:02d} / {len(doc):02d}'
        txt(p,counter,R-tw(counter,9.,'semibold'),49,9.,'semibold',MID)
    doc.set_metadata({'title':'Little Chewz | '+d['title'],'creator':'Little Chewz reusable PyMuPDF teacher template'})
    doc.subset_fonts()
    doc.save(out,garbage=4,deflate=True)
    # Verify all relative-file destinations exist. External URLs are copied, not fetched.
    with fitz.open(out) as check:
        for p in check:
            for ln in p.get_links():
                if ln.get('kind')==fitz.LINK_GOTOR:
                    target=(content.parent/ln['file']).resolve()
                    if not target.exists() and target.name not in {v.get('file') for v in registry.values()}:
                        raise FileNotFoundError(f'Unresolved local resource: {ln["file"]}')
    return {'section':d['title'],'key':d['key'],'file':str(out),'pages':len(doc)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--content',type=Path,help='Lesson JSON path under content/<school>/<quest>/lessons/<stage>/')
    ap.add_argument('--output',type=Path,help='Optional output path for a single lesson')
    ap.add_argument('--font-dir',type=Path)
    args=ap.parse_args()
    configure_fonts(args.font_dir)
    root=args.root.resolve()
    registry=json.loads((root/'catalog/resources.json').read_text(encoding='utf-8'))
    if args.content:
        paths=[(args.content if args.content.is_absolute() else root/args.content).resolve()]
    else:
        # New lessons can be added as sibling folders without changing the generator.
        paths=sorted(root.glob('content/**/lessons/**/lesson.json'))
    if not paths:
        ap.error('No lesson JSON found; provide --content with the lesson.json path')
    if args.output and len(paths)!=1:
        ap.error('--output can only be used with a single --content')
    for content in paths:
        output=((args.output if args.output.is_absolute() else root/args.output).resolve()
                if args.output else None)
        info=build(content,registry,output)
        print(info['file'],info['pages'],'pages')

if __name__=='__main__':main()
