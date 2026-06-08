-- Lime MVP — initial schema
-- Run this in the Supabase Dashboard: SQL Editor -> New query -> paste -> Run.
-- Idempotent-ish: re-running will error on "already exists" — that's expected
-- and safe to ignore if you're re-applying after a partial run.

-- ============================================================
-- profiles — extends auth.users with app-specific data
-- ============================================================
create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;

create policy "Users can view their own profile"
  on public.profiles for select
  using (auth.uid() = id);

create policy "Users can update their own profile"
  on public.profiles for update
  using (auth.uid() = id);

-- Auto-create a profile row whenever someone signs up via Supabase Auth.
create function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id) values (new.id);
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();


-- ============================================================
-- items — one row per clothing item (the PRD's "Wardrobe Grid" data)
-- ============================================================
create type public.item_category as enum ('top', 'bottom', 'shoes');

create table public.items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  category public.item_category not null,
  image_url text not null,
  tags jsonb not null,       -- validated VLM output: { silhouette, palette, texture, aesthetic }
  embedding_id text,          -- pointer to the matching vector in Pinecone
  created_at timestamptz not null default now()
);

create index items_user_id_idx on public.items (user_id);
create index items_category_idx on public.items (category);
create index items_tags_gin_idx on public.items using gin (tags);

alter table public.items enable row level security;

create policy "Users can view their own items"
  on public.items for select
  using (auth.uid() = user_id);

create policy "Users can insert their own items"
  on public.items for insert
  with check (auth.uid() = user_id);

create policy "Users can update their own items"
  on public.items for update
  using (auth.uid() = user_id);

create policy "Users can delete their own items"
  on public.items for delete
  using (auth.uid() = user_id);


-- ============================================================
-- outfits — locked outfit configurations from the swiping deck
-- (backs the PRD success metric: "3 outfit configs locked per user weekly")
-- ============================================================
create table public.outfits (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  top_item_id uuid references public.items (id) on delete set null,
  bottom_item_id uuid references public.items (id) on delete set null,
  shoes_item_id uuid references public.items (id) on delete set null,
  weather_snapshot jsonb,     -- optional: temperature/conditions at the moment of locking
  locked_at timestamptz not null default now()
);

create index outfits_user_id_idx on public.outfits (user_id);

alter table public.outfits enable row level security;

create policy "Users can view their own outfits"
  on public.outfits for select
  using (auth.uid() = user_id);

create policy "Users can insert their own outfits"
  on public.outfits for insert
  with check (auth.uid() = user_id);

create policy "Users can delete their own outfits"
  on public.outfits for delete
  using (auth.uid() = user_id);


-- ============================================================
-- Storage — private bucket for clothing photos, folder-scoped per user
-- Expected object path convention: clothing-photos/{user_id}/{filename}
-- ============================================================
insert into storage.buckets (id, name, public)
values ('clothing-photos', 'clothing-photos', false);

create policy "Users can upload to their own folder"
  on storage.objects for insert
  with check (
    bucket_id = 'clothing-photos'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

create policy "Users can view their own folder"
  on storage.objects for select
  using (
    bucket_id = 'clothing-photos'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

create policy "Users can delete from their own folder"
  on storage.objects for delete
  using (
    bucket_id = 'clothing-photos'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- ============================================================
-- Table-level grants for `authenticated` and `service_role`
-- RLS policies govern *row*-level access, but Postgres still requires base
-- table-level GRANTs before policies are even evaluated — tables created via
-- the SQL Editor (as above) don't automatically receive the grants that the
-- Supabase dashboard's table editor (or its default-ACL setup) applies.
-- Without this, every signed-in user gets "permission denied for table X"
-- (SQLSTATE 42501) the moment the app tries to read or write — even though
-- the RLS policies are correct — and admin/backend operations using the
-- service-role key fail the same way (service_role bypasses RLS, but still
-- needs the base table grant to get past the permission check).
-- `anon` doesn't need access — every route in this app requires a session.
-- ============================================================
grant usage on schema public to authenticated, service_role;
grant select, insert, update, delete on public.profiles, public.items, public.outfits
  to authenticated, service_role;
