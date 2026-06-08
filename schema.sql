-- ============================================================
-- Cione Leads — Supabase schema
-- Paste this into your Supabase project's SQL Editor and run it.
-- ============================================================

-- 1. The leads table -----------------------------------------
create table if not exists public.leads (
  id              uuid primary key default gen_random_uuid(),
  owner_id        uuid references auth.users(id) default auth.uid(),

  -- Core business info (from Google Places)
  name            text not null,
  category        text,
  phone           text,
  website         text,
  address         text,
  rating          numeric,
  review_count    integer,

  -- Outreach signals (from website audit)
  signal_count    integer default 0,
  signal_flags    text,            -- semicolon-separated
  suggested_opener text,

  -- Contact enrichment (from Apollo, optional)
  contact_name    text,
  contact_title   text,
  contact_email   text,
  contact_linkedin text,

  -- Pipeline tracking (edited in the dashboard)
  status          text default 'new'
                  check (status in ('new','contacted','replied','meeting','won','dead')),
  note            text default '',

  -- Dedupe key so re-running the script updates instead of duplicating
  dedupe_key      text,

  created_at      timestamptz default now(),
  updated_at      timestamptz default now()
);

-- 2. Helpful indexes -----------------------------------------
create index if not exists leads_owner_idx   on public.leads(owner_id);
create index if not exists leads_status_idx  on public.leads(status);
create index if not exists leads_signal_idx  on public.leads(signal_count desc);
create unique index if not exists leads_dedupe_idx
  on public.leads(owner_id, dedupe_key);

-- 3. Auto-update updated_at ----------------------------------
create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end; $$;

drop trigger if exists leads_touch on public.leads;
create trigger leads_touch
  before update on public.leads
  for each row execute function public.touch_updated_at();

-- 4. Row Level Security --------------------------------------
-- Each user only sees and edits their own leads.
alter table public.leads enable row level security;

drop policy if exists "own leads select" on public.leads;
create policy "own leads select" on public.leads
  for select using (auth.uid() = owner_id);

drop policy if exists "own leads insert" on public.leads;
create policy "own leads insert" on public.leads
  for insert with check (auth.uid() = owner_id);

drop policy if exists "own leads update" on public.leads;
create policy "own leads update" on public.leads
  for update using (auth.uid() = owner_id);

drop policy if exists "own leads delete" on public.leads;
create policy "own leads delete" on public.leads
  for delete using (auth.uid() = owner_id);

-- 5. Realtime ------------------------------------------------
-- Lets the dashboard sync live across devices.
alter publication supabase_realtime add table public.leads;
