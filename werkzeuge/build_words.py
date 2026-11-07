"""Baut app/words.json aus der offiziellen HSK-Liste (daten/hsk30_2025_vocabulary.csv)
und den deutschen Dateien daten/de_hsk*.txt (Format: Nr|Deutsch|Beispiel|Beispiel Deutsch).
Beispiel-Pinyin per pypinyin.  Aufruf: python build_words.py <projektordner>"""
import csv, json, re, sys, os
from pypinyin import lazy_pinyin, Style
P = sys.argv[1]
LV = {'一级':1,'二级':2,'三级':3,'四级':4,'五级':5,'六级':6,'七-':7}
words = {}
for x in csv.DictReader(open(os.path.join(P,'daten','hsk30_2025_vocabulary.csv'))):
    words[int(x['No.'])] = dict(id=int(x['No.']), l=LV[x['Level'][:2]],
        w=re.sub(r'\d+$','',x['Word']), p=x['Pinyin'], pos=x['PartOfSpeech'])
PUN = set('，。？！：；“”——、')
import unicodedata
from pypinyin import pinyin
def bare(x): return ''.join(c for c in unicodedata.normalize('NFD',x) if not unicodedata.combining(c))
def split_official(word, off):
    """Ordnet jedem Zeichen des Worts seine Silbe aus dem offiziellen Pinyin zu."""
    rest = re.sub(r"[\s'’\-/]", '', off.split('/')[0]).lower(); res=[]
    for c in word:
        cands = sorted(set(pinyin(c, style=Style.TONE, heteronym=True)[0]), key=len, reverse=True)
        hit=None
        for cand in cands:
            for k in range(len(cand)+1, 0, -1):
                seg=rest[:k]
                if bare(seg)==bare(cand) or seg==cand: hit=seg; break
            if hit: break
        if c=='儿' and rest.startswith('r'): hit='r'
        if not hit: return None
        res.append(hit); rest=rest[len(hit):]
    return res if not rest else None
FIX = {'的':'de','了':None,'着':None,'得':None,'地':None}
def py(s, word, off):
    syl = [t for t in lazy_pinyin(s, style=Style.TONE, errors=lambda c: list(c))]
    # lazy_pinyin liefert pro Zeichen eine Silbe (Satzzeichen einzeln)
    if len(syl)!=len(s): syl=[lazy_pinyin(c, style=Style.TONE)[0] for c in s]
    sp = split_official(word, off) if word in s else None
    i = s.find(word)
    if sp and i>=0:
        for k,v in enumerate(sp): syl[i+k]=v
    for k,c in enumerate(s):
        if sp and i<=k<i+len(word): continue
        nxt = s[k+1] if k+1<len(s) else ''
        if c=='的': syl[k]='de'
        elif c=='得' and k>0 and nxt not in '到分了' : syl[k]='de'
        elif c=='着' and k>0 and nxt!='急': syl[k]='zhe'
        elif c=='地' and k>0 and s[k-1] in '兴慢好真认努' : syl[k]='de'
        elif c=='儿' and k>0 and s[k-1] in '点会玩那这哪' : syl[k]='r'
    def tn(t):
        for i,grp in enumerate(['āēīōūǖ','áéíóúǘ','ǎěǐǒǔǚ','àèìòùǜ']):
            if any(ch in grp for ch in t): return i+1
        return 5
    for k,c in enumerate(s):
        if c!='一' or (sp and i<=k<i+len(word)): continue
        nxt = s[k+1] if k+1<len(s) else ''
        prv = s[k-1] if k>0 else ''
        if not nxt or nxt in '二三四五六七八九十零百千万' or prv in '第十' or nxt in PUN: continue
        syl[k] = 'yí' if tn(syl[k+1])==4 else 'yì'
    out=[]
    for c,t in zip(s,syl):
        if c in PUN:
            m={'，':',','。':'.','？':'?','！':'!','：':':','、':',','；':';','“':'“','”':'”','—':'–'}.get(c,c)
            if out and c not in '“': out[-1]+=m
            else: out.append(m); out[-1]+='\x00'
        else:
            if c=='儿' and t=='r' and out: out[-1]+='r'
            else: out.append(t)
    return ' '.join(out).replace('\x00 ','').replace('\x00','')
de = {}
for f in sorted(os.listdir(os.path.join(P,'daten'))):
    if f.startswith('de_hsk') and f.endswith('.txt'):
        for line in open(os.path.join(P,'daten',f)):
            if not line.strip(): continue
            n, d, ex, exde = line.rstrip('\n').split('|')
            de[int(n)] = (d, ex, exde)
out=[]; warn=[]; nosplit=[]
for n,wd in sorted(words.items()):
    if n not in de: continue
    d, ex, exde = de[n]
    sp = split_official(wd['w'], wd['p'])
    if not sp: nosplit.append((n, wd['w'], wd['p']))
    wd.update(de=d, ex=ex, exp=py(ex, wd['w'], wd['p']), exde=exde, ps=' '.join(sp) if sp else '')
    if wd['w'] not in ex and not (wd['w'] in '着子员园面' ): warn.append((n, wd['w'], ex))
    out.append(wd)

# ---- Unterricht: unterricht/unterricht_*.txt (Wort|Pinyin|Deutsch|Beispiel|Beispiel Deutsch) ----
byw = {}
for n,wd in sorted(words.items()):
    byw.setdefault(wd['w'], wd)
have = {wd['id']: wd for wd in out}
nid = 20001
udir = os.path.join(P,'unterricht')
for f in sorted(os.listdir(udir)) if os.path.isdir(udir) else []:
    if not (f.startswith('unterricht_') and f.endswith('.txt')): continue
    lesson = None
    for line in open(os.path.join(udir,f)):
        line=line.rstrip('\n')
        if line.startswith('# Lektion:'): lesson=line[len('# Lektion:'):].split('(')[0].strip(); continue
        if not line.strip() or line.startswith('#'): continue
        parts=line.split('|'); w=parts[0]
        h=byw.get(w)
        if h and h['id'] in have:            # schon in HSK 1–3: nur markieren
            have[h['id']].setdefault('u', lesson); continue
        if len(parts)<5: print('FEHLT Deutsch:', w); continue
        _, p, d, ex, exde = parts
        if h: wd=dict(h); p=h['p']           # HSK 4+ : offizielle Nummer und Stufe
        else: wd=dict(id=nid, l=0, w=w, p=p, pos=''); nid+=1
        sp=split_official(w,p)
        wd.update(de=d, ex=ex, exp=py(ex,w,p), exde=exde, ps=' '.join(sp) if sp else '', u=lesson)
        out.append(wd); have[wd['id']]=wd
print(sum(1 for x in out if x.get('u')), 'Unterrichtswörter')
json.dump(out, open(os.path.join(P,'app','words.json'),'w'), ensure_ascii=False, separators=(',',':'))
print(len(out), 'Wörter'); print('Wort fehlt im Beispiel:', warn); print('Silben nicht zuordenbar:', nosplit)
