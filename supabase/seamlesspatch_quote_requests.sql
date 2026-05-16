-- Seamless Patch quote intake schema
-- Applied to Supabase via Management API on 2026-05-16.
-- This table is designed so Lettera can later poll pending rows and send follow-up emails.

create table if not exists public.seamlesspatch_quote_requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  source text not null default 'seamlesspatch.com',
  name text not null,
  phone text not null,
  email text,
  zip text not null,
  damage_description text,
  photo_paths text[] not null default '{}',
  status text not null default 'new',
  follow_up_status text not null default 'pending',
  lettera_notes jsonb not null default '{}'::jsonb,
  user_agent text,
  page_url text
);

alter table public.seamlesspatch_quote_requests enable row level security;

create index if not exists idx_seamlesspatch_quote_requests_created_at
  on public.seamlesspatch_quote_requests (created_at desc);
create index if not exists idx_seamlesspatch_quote_requests_status
  on public.seamlesspatch_quote_requests (status, created_at desc);
create index if not exists idx_seamlesspatch_quote_requests_follow_up
  on public.seamlesspatch_quote_requests (follow_up_status, created_at desc);

drop policy if exists seamlesspatch_public_quote_insert on public.seamlesspatch_quote_requests;
create policy seamlesspatch_public_quote_insert
  on public.seamlesspatch_quote_requests
  for insert
  to anon
  with check (source = 'seamlesspatch.com');

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'seamlesspatch-quote-photos',
  'seamlesspatch-quote-photos',
  false,
  10485760,
  array['image/jpeg','image/png','image/webp','image/gif','image/heic','image/heif']
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists seamlesspatch_public_photo_upload on storage.objects;
create policy seamlesspatch_public_photo_upload
  on storage.objects
  for insert
  to anon
  with check (
    bucket_id = 'seamlesspatch-quote-photos'
    and (storage.foldername(name))[1] = 'quote-uploads'
  );
