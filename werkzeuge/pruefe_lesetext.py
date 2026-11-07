"""Prüft einen Lesetext gegen den Wortschatz des Nutzers.

Aufruf: python3 pruefe_lesetext.py <text.json> <woerter.json> <stats_woerter.json>
  text.json          {"datum","titel","titelDe","neu":[...],"saetze":[{"w":[[zh,py,de],...],"de":...}]}
                     Satzzeichen als [zh,"",""], Eigennamen als [zh,py,de,"name"].
  woerter.json       app/words.json
  stats_woerter.json Inhalt von stats/woerter (bekannt, lernend, naechsteNeue)

Regeln: jedes Wort-Token ist bekannt/lernend, ein Eigenname, eine Zahl oder steht in "neu".
"neu" darf höchstens 3 Wörter haben, alle aus der Wortliste. Mindestens 90 % der Wort-Tokens bekannt.
Schreibt bei Erfolg "abdeckung" in text.json und gibt OK aus, sonst FEHLER mit Liste.
"""
import json, sys, unicodedata

def bare(p):
    return ''.join(c for c in unicodedata.normalize('NFD', p) if not unicodedata.combining(c)).replace(' ', '').replace("'", '').replace('’', '').lower()

tf, wf, sf = sys.argv[1:4]
text = json.load(open(tf)); words = json.load(open(wf)); st = json.load(open(sf))
byid = {w['id']: w for w in words}
byw = {}
for w in words: byw.setdefault(w['w'], w)
known = {byid[i]['w'] for i in st.get('bekannt', []) + st.get('lernend', []) if i in byid}
neu = list(dict.fromkeys(text.get('neu', [])))
NUM = set('零一二三四五六七八九十百千万两0123456789')
err, warn = [], []
if len(neu) > 3: err.append(f'zu viele neue Wörter: {neu}')
for n in neu:
    if n not in byw: err.append(f'neues Wort {n} steht nicht in der Wortliste')
    elif n in known: warn.append(f'{n} ist schon bekannt, muss nicht als neu markiert werden')
tok_known = tok_all = 0
for si, s in enumerate(text.get('saetze', [])):
    if not s.get('de'): err.append(f'Satz {si+1}: Übersetzung fehlt')
    for t in s.get('w', []):
        if len(t) < 3: err.append(f'Satz {si+1}: Token {t} unvollständig'); continue
        zh, py, de = t[:3]
        if not py: continue  # Satzzeichen
        tok_all += 1
        if len(t) > 3 and t[3] == 'name': tok_known += 1; continue
        if all(c in NUM for c in zh): tok_known += 1; continue
        if zh in known:
            tok_known += 1
            w = byw[zh]
            if bare(w['p'].split('/')[0]) != bare(py): warn.append(f'{zh}: Pinyin {py} weicht von {w["p"]} ab')
            continue
        if zh in neu: continue
        err.append(f'Satz {si+1}: „{zh}“ ist nicht bekannt und nicht als neu markiert')
cov = tok_known / tok_all if tok_all else 0
if tok_all < 25: err.append(f'Text zu kurz ({tok_all} Wörter)')
if cov < 0.9: err.append(f'Abdeckung nur {cov:.0%}')
for w in warn: print('Hinweis:', w)
if err:
    print('FEHLER'); [print(' -', e) for e in dict.fromkeys(err)]; sys.exit(1)
text['abdeckung'] = f'{round(cov*100)} %'
json.dump(text, open(tf, 'w'), ensure_ascii=False, indent=1)
print(f'OK: {tok_all} Wörter, {cov:.0%} bekannt, neu: {neu or "keine"}')
