-- HSK Vokabeltrainer: Tabellen für Lernstand und Übersicht.
-- Einmal im Supabase SQL Editor ausführen (Dashboard › SQL Editor › New query › einfügen › Run).

-- Lernstand: eine Zeile pro Konto, nur das eigene Konto darf lesen und schreiben.
create table if not exists public.hsk_progress (
  user_id uuid primary key references auth.users on delete cascade,
  data jsonb not null,
  updated_at timestamptz not null default now()
);
alter table public.hsk_progress enable row level security;
create policy "HSK: eigenen Stand lesen"   on public.hsk_progress for select to authenticated using (auth.uid() = user_id);
create policy "HSK: eigenen Stand anlegen" on public.hsk_progress for insert to authenticated with check (auth.uid() = user_id);
create policy "HSK: eigenen Stand ändern"  on public.hsk_progress for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
grant select, insert, update on public.hsk_progress to authenticated;

-- Kurze Übersicht pro Konto (Name, Tageszahlen, bekannte Wort-Nummern).
-- Lesbar mit dem öffentlichen Schlüssel, damit Claude abends Lesetexte schreiben und erinnern kann.
create table if not exists public.hsk_stats (
  user_id uuid primary key references auth.users on delete cascade,
  name text not null default '',
  stats jsonb,
  known jsonb,
  updated_at timestamptz not null default now()
);
alter table public.hsk_stats enable row level security;
create policy "HSK: Übersicht lesen"           on public.hsk_stats for select to anon, authenticated using (true);
create policy "HSK: eigene Übersicht anlegen"  on public.hsk_stats for insert to authenticated with check (auth.uid() = user_id);
create policy "HSK: eigene Übersicht ändern"   on public.hsk_stats for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
grant select on public.hsk_stats to anon, authenticated;
grant insert, update on public.hsk_stats to authenticated;
