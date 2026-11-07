#!/bin/sh
# Liest die Übersicht aller Konten aus Supabase (Tabelle hsk_stats, öffentlicher Schlüssel) als JSON.
# Aufruf: sh stats_holen.sh            -> alle Konten
#         sh stats_holen.sh keanu      -> nur Konten, deren Name so beginnt (ohne Groß/klein)
URL="https://pgppnghqbuslucvfotaa.supabase.co/rest/v1/hsk_stats"
KEY="sb_publishable_-WktLPprHHIvsZf8Xl1zUg_cGS8nMj-"
Q="select=user_id,name,stats,known,updated_at"
[ -n "$1" ] && Q="$Q&name=ilike.$1*"
curl -s "$URL?$Q" -H "apikey: $KEY" -H "Authorization: Bearer $KEY"
