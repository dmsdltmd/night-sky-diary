-- Supabase > SQL Editor 에 붙여넣고 Run
create table if not exists diaries (
  id          bigint generated always as identity primary key,
  nickname    text not null,
  entry_date  date not null,
  content     text not null,
  joy         real, flutter real, calm real, tired real,
  sad         real, anxious real, angry real,
  corrected   text,                       -- 사용자가 고친 감정 (없으면 null)
  kind        text default 'diary',       -- diary = 일기, quick = 10초 기록
  reply       text,                       -- 타임캡슐: 지금의 내가 남긴 답장
  reply_at    date,                       -- 답장한 날
  created_at  timestamptz default now(),
  unique (nickname, entry_date)           -- 한 사람은 하루에 일기 1개
);

-- 졸업작품 시연용 설정: 앱 키(anon)로 읽고 쓸 수 있게 허용
-- 주의: 키를 아는 사람은 누구나 읽고 쓸 수 있어요. 실제 서비스라면 로그인 기능을 붙여야 해요.
alter table diaries enable row level security;
create policy "demo all" on diaries for all using (true) with check (true);

-- 이미 표를 만들었다면 아래 3줄만 실행하면 돼요
alter table diaries add column if not exists kind text default 'diary';
alter table diaries add column if not exists reply text;
alter table diaries add column if not exists reply_at date;
