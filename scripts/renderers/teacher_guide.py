#!/usr/bin/env python3
"""Little Chewz: the approved PDF-native teacher-guide system.

No image generation. Teacher pages use the established Lato type, measured text,
vector rules, one shared baseline-aligned grid, and aligned action labels. Covers are
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

# ---------------------------------------------------------------------------
# Layout system
#
# Every vertical position below is a text BASELINE or a rule position, never a
# text "top". Gaps are measured optically: rule -> cap height of the next line,
# and last baseline -> next rule, so space reads equal above and below dividers.
#
# Horizontal grid (pt), shared by every page and every lesson:
#   44  margin: step numbers
#   ~63 option letters, right-aligned OPT_LETTER_GAP before their option title
#       (the same marker->title relationship as the step heading)
#   ~72 step titles, set just past the widest two-digit number so the
#       number and title read as one heading and every title lines up
#   82  option titles and action labels: indented under the step title,
#       identical in every step so the label column never moves
#   129 instruction text
#   551 right margin: step times, page counter
# Overview and bonus columns share one two-column grid with a 40 pt gutter.
# ---------------------------------------------------------------------------
CAP=.7165                      # Lato cap height / em
BOX_MID=.387                   # Lato text-box middle above baseline / em ((0.987-0.213)/2)
COL_NUM,COL_ACT,COL_TXT=L,82.,129.
NUM_TITLE_GAP=7.5
GUTTER=40.
COL_W=(PAGE_W-GUTTER)/2
COL2_X=L+COL_W+GUTTER
GAP=24.                        # rule <-> neighbouring text on flow pages
OV_GAP=27.                     # the same on the overview, which has room to breathe
HDR_EYEBROW,HDR_TITLE,HDR_RULE=38.,70.,88.

# Type scale
SEC_SIZE=13.4;BAR_W=28.
BODY,BODY_LH=11.2,17.2          # overview prose
FLOW_BODY,FLOW_ASK,FLOW_LH=10.9,11.2,16.   # every Teaching Flow row, in or out of options
ROW_STEP=25.                   # baseline -> baseline between consecutive rows
LABEL_SIZE=8.9
STEP_NUM,STEP_TITLE,STEP_TITLE_LH=17.5,15.5,19.
# Options mirror the step heading one level down: a heavy accent marker
# ~13% larger than a bold black title (17.5/15.5 at step level).
OPT_TITLE=12.2
OPT_LETTER=round(OPT_TITLE*STEP_NUM/STEP_TITLE,1)
OPT_LETTER_GAP=10.
TIME_SIZE=9.2
OPTION_RULE=(.87,.85,.83)
FLOW_FIRST_CAP=HDR_RULE+30.    # cap-top of the first step on a flow page
FLOW_LIMIT=772.                # last allowed content baseline on a flow page
CUE_BASELINE=800.

def line(p,y,x=L,x2=R,c=SOFT,thick=.6):
    if p is not None:p.draw_line((x,y),(x2,y),color=c,width=thick)

def vline(p,x,y1,y2,c=SOFT,thick=.6):
    if p is not None:p.draw_line((x,y1),(x,y2),color=c,width=thick)

def at(p,s,x,baseline,size,font='regular',color=BLACK,max_right=R):
    """Draw one line by baseline; returns the baseline."""
    txt(p,s,x,baseline-size,size,font,color,max_right);return baseline

def cap_to_base(cap_top,size):return cap_top+size*CAP

def lines(p,s,x,baseline,w,size,lh,font='regular',color=BLACK):
    """Wrapped text starting at `baseline`; returns the LAST baseline drawn."""
    b=baseline
    for i,value in enumerate(wrap(s,w,size,font)):
        if i:b+=lh
        if value:at(p,value,x,b,size,font,color,max_right=x+w)
    return b

def label(p,title,x,baseline,color=DEEP,size=LABEL_SIZE):
    return at(p,title,x,baseline,size,'heavy',color)

def section(p,title,x,cap_top,accent):
    """Section title with a short accent bar. Returns the cap-top for body text."""
    b=at(p,title,x,cap_to_base(cap_top,SEC_SIZE),SEC_SIZE,'bold')
    bar=b+7.5
    line(p,bar,x,x+BAR_W,accent,2.)
    return bar+15.

def hdr(p,eyebrow,title,accent=CORAL):
    label(p,eyebrow.upper(),L,HDR_EYEBROW,MID,9.1)
    size=min(24.,PAGE_W/tw(title,24.,'heavy')*24.)
    if size<16:raise LayoutError(f'Header is too long: {title}')
    at(p,title,L,HDR_TITLE,size,'heavy')
    line(p,HDR_RULE,c=accent,thick=1.3)
    return HDR_RULE

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

def resource_line(p,item,reg,x,baseline,w,size=10.5,strict=False,description_size=None,lh=None,show_description=True):
    """Linked resource name (underlined) + ' — description'. Returns the last baseline.

    Strict rows (overview) must fit one line. Flow rows may wrap the description,
    never leaving an em dash alone; continuations return to the content edge.
    """
    rec=resolve(item,reg);name=rec['title'];desc=rec.get('description','') if show_description else ''
    ds=description_size or size-.5;lh=lh or FLOW_LH
    name_w=tw(name,size,'semibold')
    if name_w>w:raise LayoutError(f'Resource title too long: {name}')
    suffix=' — '+desc if desc else ''
    if strict and name_w+tw(suffix,ds)>w+.01:
        raise LayoutError(f'Overview resource must stay on one line ({name_w+tw(suffix,ds):.1f}>{w:.1f} pt): {name} — {desc}. Shorten the description.')
    at(p,name,x,baseline,size,'semibold',max_right=x+w)
    line(p,baseline+2.2,x,x+name_w,BLACK,.5)
    annotate(p,rec,fitz.Rect(x,baseline-size,x+name_w,baseline+4))
    if not suffix:return baseline
    remaining=w-name_w
    if tw(suffix,ds)<=remaining:
        at(p,suffix,x+name_w,baseline,ds,'regular',MID,max_right=x+w);return baseline
    words=desc.split();first=' —';used=0
    for word in words:
        if tw(first+' '+word,ds)>remaining:break
        first+=' '+word;used+=1
    if used:
        at(p,first,x+name_w,baseline,ds,'regular',MID,max_right=x+w)
        return lines(p,' '.join(words[used:]),x,baseline+lh,w,ds,lh,color=MID) if used<len(words) else baseline
    return lines(p,'— '+desc,x,baseline+lh,w,ds,lh,color=MID)

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

def prose_section(p,title,text,cap_top,accent):
    """Full-width section; returns the last baseline."""
    c=section(p,title,L,cap_top,accent)
    return lines(p,text,L,cap_to_base(c,BODY),PAGE_W,BODY,BODY_LH)

def meta_row(p,items,baseline):
    """Grade / duration / print note, separated by short vertical ticks."""
    size,gap=9.3,12.;x=L
    for i,item in enumerate(items):
        if i:
            vline(p,x+gap,baseline-size*CAP,baseline+.6,SOFT,.8);x+=2*gap
        at(p,item,x,baseline,size,'bold',MID);x+=tw(item,size,'bold')
    if x>R:raise LayoutError('Overview meta row is too long')

def overview(doc,d,reg):
    p=newp(doc);accent=section_accent(d['key'])
    if d['key'].startswith('p') and d['key'][1:].isdigit():
        part,topic=d['title'].split(' / ',1)
        rule=hdr(p,part+' / TEACHER GUIDE',topic+' / AT A GLANCE',accent)
    else:rule=hdr(p,'TEACHER GUIDE',d['title']+' / AT A GLANCE',accent)

    # Meta band: equal optical space above and below the line.
    meta_b=cap_to_base(rule+17,9.3)
    meta_row(p,[f"GRADES {d['grade']}",d['duration'].upper(),d['print_note'].upper()],meta_b)
    rule=meta_b+17;line(p,rule)

    b=prose_section(p,'Learning goal',d['goal'],rule+OV_GAP,accent)
    rule=b+OV_GAP;line(p,rule);top=rule

    # Two equal columns joined to the rules above and below by a vertical divider.
    c=section(p,'Learning outcomes',L,top+OV_GAP,accent)
    lb=cap_to_base(c,BODY)-FLOW_LH-9
    for i,value in enumerate(d['outcomes'],1):
        lb+=FLOW_LH+9
        at(p,f'{i:02d}',L,lb,10.4,'bold',accent)
        lb=lines(p,value,L+26,lb,COL_W-26,10.9,FLOW_LH)

    c=section(p,'Preparation',COL2_X,top+OV_GAP,accent)
    rb=label(p,'CORE RESOURCES',COL2_X,cap_to_base(c,LABEL_SIZE),MID)
    for it in d['core']:
        rb=resource_line(p,it,reg,COL2_X,rb+19,COL_W,size=10.4,strict=True,description_size=9.6)
    if d['optional_prep'] or d.get('prep_note'):
        rb=label(p,d.get('prep_heading','OPTIONAL PREPARATION'),COL2_X,rb+29,MID)
        for it in d['optional_prep']:
            rb=resource_line(p,it,reg,COL2_X,rb+19,COL_W,size=10.4,strict=True,description_size=9.6)
        if d.get('prep_note'):
            rb=lines(p,d['prep_note'],COL2_X,rb+(19 if d['optional_prep'] else 17),COL_W,9.6,14.4,'italic',MID)
    bottom=max(lb,rb)+OV_GAP
    vline(p,L+COL_W+GUTTER/2,top,bottom)
    line(p,bottom)

    b=prose_section(p,'Teaching focus',d['focus'],bottom+OV_GAP,accent)
    assessment=normalized_assessment(d.get('assessment'))
    # Assessment is optional and never adds a Teaching Flow activity.
    if assessment:
        rule=b+OV_GAP;line(p,rule)
        if isinstance(assessment,str):
            b=prose_section(p,'Assessment',assessment,rule+OV_GAP,accent)
        else:
            c=section(p,'Assessment',L,rule+OV_GAP,accent);b=cap_to_base(c,10.6)-15.2-5
            for item in assessment:
                b+=15.2+5
                at(p,'•',L,b,10.6,'bold',accent)
                b=lines(p,item,L+14,b,PAGE_W-14,10.6,15.2)
    rule=b+OV_GAP;line(p,rule)
    b=prose_section(p,'Curriculum connections',' · '.join(d['curriculum']),rule+OV_GAP,accent)
    if b>806:raise LayoutError(f'{d["key"]} overview exceeds page at baseline {b:.1f}')
    return p

# ---------------------------------------------------------------------------
# Teaching Flow
# ---------------------------------------------------------------------------
def draw_row(p,row,b,reg,accent):
    """One action row whose first baseline is `b`. Label and text share that baseline."""
    kind=row['kind'].upper();x,w=COL_TXT,R-COL_TXT
    label(p,'READ' if kind=='QUOTE' else kind,COL_ACT,b,accent)
    if row.get('links') is not None:
        for i,item in enumerate(row['links']):
            if i:b+=FLOW_LH+5
            b=resource_line(p,item,reg,x,b,w,size=FLOW_BODY,description_size=FLOW_BODY)
        return b
    if kind=='QUOTE':
        # Indented passage framed by a single accent rule; no quotation marks.
        start=b-FLOW_BODY*CAP-1.5;first=True
        for paragraph in row['text'].split('\n\n'):
            if not first:b+=FLOW_LH+6
            first=False
            font='bold' if paragraph.strip()==row.get('bold_text','') else 'regular'
            b=lines(p,paragraph,x+14,b,w-14,FLOW_BODY,FLOW_LH,font)
        vline(p,x+1,start,b+4,accent,1.6)
        return b
    if row.get('ref'):
        return resource_line(p,row,reg,x,b,w,size=FLOW_BODY,description_size=FLOW_BODY)
    ask=kind=='ASK'
    return lines(p,row.get('text',''),x,b,w,FLOW_ASK if ask else FLOW_BODY,FLOW_LH,'semibold' if ask else 'regular')

def marker_baseline(title_baseline,marker_size,title_size):
    """Baseline that centres the marker's text box on the title's text box."""
    return title_baseline+(marker_size-title_size)*BOX_MID

def step_title_x():
    """Fixed title x: just past the widest possible step number (Lato digits vary)."""
    return COL_NUM+max(tw(f'{i:02d}',STEP_NUM,'heavy') for i in range(100))+NUM_TITLE_GAP

def grouped_more_rows(rows):
    """Render one MORE block per activity, preserving resource order and links."""
    more_items=[]
    first_more=None
    for i,row in enumerate(rows):
        if row['kind'].upper()=='MORE':
            if first_more is None:first_more=i
            if row.get('links') is not None:
                more_items.extend(row['links'])
            elif row.get('ref'):
                more_items.append({k:v for k,v in row.items() if k!='kind'})
            else:
                raise ValueError('MORE rows must contain linked resources')
    if first_more is None:return rows
    result=[]
    for i,row in enumerate(rows):
        if i==first_more:
            result.append({'kind':'MORE','links':more_items})
        if row['kind'].upper()!='MORE':
            result.append(row)
    return result

def draw_step(p,step,cap_top,reg,accent=CORAL):
    """Draw a step whose title cap-top is `cap_top`; returns the last baseline."""
    value=str(step['mins']);time=value.upper() if value.upper()=='OPTIONAL' else value+' MIN'
    time_w=tw(time,TIME_SIZE,'bold')
    title_x=step_title_x();title_w=R-title_x-time_w-16
    b=cap_to_base(cap_top,STEP_TITLE)
    num=f"{step['id']:02d}"
    # Markers are vertically centred on their title: the middle of the marker's
    # text box lines up with the middle of the title's text box (within 0.05 pt
    # of centring the visible capitals and digits).
    at(p,num,COL_NUM,marker_baseline(b,STEP_NUM,STEP_TITLE),STEP_NUM,'heavy',accent)
    at(p,time,R-time_w,b,TIME_SIZE,'bold',MID)
    for i,ln in enumerate(wrap(step['title'],title_w,STEP_TITLE,'bold')):
        at(p,ln,title_x,b+i*STEP_TITLE_LH,STEP_TITLE,'bold',max_right=title_x+title_w)
    b+=i*STEP_TITLE_LH
    rows=grouped_more_rows(step.get('rows',[]));options=step.get('options',[])
    for n,row in enumerate(rows):
        b=draw_row(p,row,b+(28 if n==0 else ROW_STEP),reg,accent)
    for n,option in enumerate(options):
        if n:
            sep=b+19;line(p,sep,COL_ACT,R,OPTION_RULE,.5)
            b=cap_to_base(sep+19,OPT_TITLE)
        else:
            b+=30 if not rows else ROW_STEP+8
        letter=option['label']
        at(p,letter,COL_ACT-OPT_LETTER_GAP-tw(letter,OPT_LETTER,'heavy'),marker_baseline(b,OPT_LETTER,OPT_TITLE),OPT_LETTER,'heavy',accent)
        at(p,option['title'],COL_ACT,b,OPT_TITLE,'bold')
        for m,row in enumerate(grouped_more_rows(option['rows'])):
            b=draw_row(p,row,b+(23 if m==0 else ROW_STEP),reg,accent)
    return b

def bonuses(p,items,cap_top,reg,title):
    """Two-column extension block on the overview's column grid; returns last baseline."""
    if len(items)>2:raise LayoutError('Bonus section holds two purposeful items at most; use a separate resource for more.')
    hb=at(p,title,L,cap_to_base(cap_top,11.2),11.2,'bold')
    last=hb
    for j,it in enumerate(items):
        x=L+j*(COL_W+GUTTER)
        b=resource_line(p,it,reg,x,hb+24,COL_W,size=10.4,show_description=False)
        desc=it.get('description','').strip().lstrip('—').strip()
        if desc:b=lines(p,desc,x,b+17,COL_W,9.6,14.2,color=MID)
        last=max(last,b)
    return last

def flow(doc,d,reg):
    """Flow complete steps onto pages; never split a step."""
    accent=section_accent(d['key'])
    if d.get('flow_style') not in (None,'compact') :
        raise LayoutError(f"Unknown flow_style {d.get('flow_style')!r}")
    if d['key'].startswith('p') and d['key'][1:].isdigit():
        part,topic=d['title'].split(' / ',1)
        eyebrow=(part+' · '+topic).upper()
    else:eyebrow=d['title'].upper()
    p=None;last=None;pages=0
    def next_page():
        nonlocal p,last,pages
        if p is not None:
            cue='CONTINUED ON NEXT PAGE  →'
            at(p,cue,R-tw(cue,9.,'semibold'),CUE_BASELINE,9.,'semibold',MID)
        p=newp(doc);pages+=1;hdr(p,eyebrow,'Teaching Flow',accent);last=None
    def place(height_fn,draw_fn,sep_gap):
        """Put a block below the previous one (rule between), or on a new page."""
        nonlocal last
        h=height_fn()
        if h>FLOW_LIMIT-FLOW_FIRST_CAP:raise LayoutError('Block too large for a flow page')
        if p is None or (last is not None and last+2*GAP+sep_gap+h>FLOW_LIMIT):next_page()
        if last is None:cap=FLOW_FIRST_CAP
        else:
            rule=last+GAP+sep_gap;line(p,rule);cap=rule+GAP
        last=draw_fn(cap)
    for st in d['steps']:
        place(lambda:draw_step(None,st,0,reg,accent),lambda c:draw_step(p,st,c,reg,accent),2)
    its=d.get('bonuses',[])
    if its:
        title=d.get('bonus_heading','MORE TIME?  YOU CHEWZ!')
        place(lambda:bonuses(None,its,0,reg,title),lambda c:bonuses(p,its,c,reg,title),2)
    return pages

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
        at(p,counter,R-tw(counter,9.1,'semibold'),HDR_EYEBROW,9.1,'semibold',MID)
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
