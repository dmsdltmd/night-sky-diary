# 감정 별자리 (Night Sky Diary)

일기를 쓰면 AI가 섞인 감정을 7가지 비율로 읽고, 하루하루가 별이 되어 나만의 밤하늘을 만드는 웹 서비스.

- 감정 모델: KLUE-RoBERTa를 KOTE 데이터(평가자 5명의 투표 비율)로 학습 → https://huggingface.co/dmsdltmd/night-sky-emotion
- 감정 7종: 기쁨, 설렘, 평온, 지침, 슬픔, 불안, 분노

## 화면
| 화면 | 하는 일 |
|---|---|
| 오늘의 별 | 일기 쓰기 → AI 감정 비율 → 틀리면 수정 → 저장 |
| 별자리 지도 | 감정이 비슷한 날은 가깝게 놓이고 선으로 연결. 별을 누르면 그날 일기 |
| 이달의 하늘 | 한 달 별자리 포스터, 지난달 비교, 분위기가 바뀐 날 |

## 파일
| 파일 | 역할 |
|---|---|
| `app.py` | 화면 3개 (Streamlit) |
| `model.py` | Hugging Face에서 모델 불러오기, 감정 예측 |
| `db.py` | Supabase에 일기 저장/불러오기 (키가 없으면 체험 모드) |
| `analysis.py` | 별 위치(PCA), 비슷한 날(코사인 유사도), 전환점(JSD), 월간 비교 |
| `sky.py` + `templates/sky.html` | 밤하늘 그림 (HTML/JS) |
| `supabase_schema.sql` | Supabase 표 만드는 SQL |

## 내 컴퓨터에서 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```
`.streamlit/secrets.toml`이 없으면 체험 모드로 실행돼요 (기록이 브라우저 창에만 잠깐 저장).

## 배포 (GitHub + Streamlit Cloud)
1. Supabase: 새 프로젝트 → SQL Editor에 `supabase_schema.sql` 붙여넣고 Run → Project Settings > API에서 URL과 anon key 복사
2. GitHub: 이 폴더를 저장소로 올리기 (`secrets.toml`은 올리지 않기, `.gitignore`에 들어 있음)
3. share.streamlit.io → Create app → 저장소 / 브랜치 `main` / 파일 `app.py` 선택
4. Advanced settings → Secrets 칸에 아래 붙여넣기 → Deploy
   ```toml
   SUPABASE_URL = "https://xxxx.supabase.co"
   SUPABASE_KEY = "eyJ..."
   ```
5. 이후 GitHub에 올리면 웹이 자동으로 업데이트돼요.

## 참고
- 감정 결과는 글에서 보이는 감정의 비율이에요. 심리 상태를 진단하지 않아요.
- 시연용 설정이라 Supabase 키를 아는 사람은 누구나 읽고 쓸 수 있어요.
