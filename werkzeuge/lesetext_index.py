"""Schreibt app/lesetexte/<user_id>/index.json (Liste aller Texte: datum, titel, titelDe), neueste zuerst.
Aufruf: python3 -I lesetext_index.py <ordner app/lesetexte/<user_id>>"""
import json, os, sys
d = sys.argv[1]
items = []
for f in sorted(os.listdir(d)):
    if f.endswith('.json') and f != 'index.json':
        t = json.load(open(os.path.join(d, f)))
        items.append({'datum': t['datum'], 'titel': t.get('titel', ''), 'titelDe': t.get('titelDe', '')})
items.sort(key=lambda x: x['datum'], reverse=True)
json.dump(items, open(os.path.join(d, 'index.json'), 'w'), ensure_ascii=False, indent=1)
print(len(items), 'Texte im Index')
