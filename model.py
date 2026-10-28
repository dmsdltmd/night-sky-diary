"""감정 모델 불러오기 + 예측

Hugging Face에 올린 모델을 한 번만 불러오고(cache_resource) 계속 재사용해요.
"""
import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_ID = "dmsdltmd/night-sky-emotion"
EMO = ["기쁨", "설렘", "평온", "지침", "슬픔", "불안", "분노"]

# 화면에 보여줄 때 비율을 얼마나 부드럽게 펼지 정하는 값.
# 1.0 = 모델 결과 그대로. 1.3~1.5로 올리면 한 감정에 쏠린 결과가 펴져서 섞인 감정이 더 잘 보여요.
DISPLAY_T = 1.0


@st.cache_resource(show_spinner="감정 모델을 불러오는 중이에요... (처음 한 번만 1~2분)")
def load_model():
    tok = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
    model.eval()
    return tok, model


@torch.no_grad()
def predict(text: str) -> list[float]:
    """일기 글 -> 7감정 비율 리스트 (EMO 순서, 합 = 1)"""
    tok, model = load_model()
    enc = tok(text, truncation=True, max_length=128, return_tensors="pt")
    logits = model(**enc).logits[0] / DISPLAY_T
    return torch.softmax(logits, -1).tolist()
