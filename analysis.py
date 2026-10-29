"""감정 데이터 분석 (별 위치, 비슷한 날, 전환점, 월간 비교)

streamlit 없이도 돌아가는 순수 계산 코드라서 따로 테스트하기 쉬워요.
"""
import numpy as np

EMO = ["기쁨", "설렘", "평온", "지침", "슬픔", "불안", "분노"]


def effective(entry: dict) -> np.ndarray:
    """화면에 쓸 감정 비율. 사용자가 고친 감정이 있으면 AI 결과와 반반 섞어요."""
    p = np.asarray(entry["probs"], dtype=float)
    if entry.get("corrected") in EMO:
        one = np.zeros(len(EMO))
        one[EMO.index(entry["corrected"])] = 1.0
        p = 0.5 * p + 0.5 * one
    return p / p.sum()


def matrix(entries: list[dict]) -> np.ndarray:
    return np.array([effective(e) for e in entries]) if entries else np.zeros((0, len(EMO)))


def cosine_matrix(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True)
    Y = X / np.clip(n, 1e-9, None)
    return Y @ Y.T


def layout(X: np.ndarray, seed: int = 7) -> np.ndarray:
    """감정 비율(7차원)을 PCA로 2차원 지도 좌표(0~1)로 바꿔요.
    감정 구성이 비슷한 날은 지도에서 가깝게 놓여요."""
    n = len(X)
    if n == 0:
        return np.zeros((0, 2))
    rng = np.random.default_rng(seed)
    if n < 3:
        pts = 0.5 + rng.uniform(-0.15, 0.15, size=(n, 2))
        return pts
    Xc = X - X.mean(axis=0)
    _, _, vt = np.linalg.svd(Xc, full_matrices=False)
    P = Xc @ vt[:2].T
    # 완전히 같은 감정인 날이 한 점에 겹치지 않도록 살짝 흩뿌리기
    P = P + rng.normal(0, 0.06, size=P.shape) * (P.std(axis=0) + 1e-6)
    lo, hi = P.min(axis=0), P.max(axis=0)
    P = (P - lo) / np.where(hi - lo < 1e-9, 1, hi - lo)
    return 0.08 + P * 0.84


def links(X: np.ndarray, threshold: float = 0.9, k: int = 2) -> list[tuple[int, int, float]]:
    """비슷한 날끼리 연결선. 각 별마다 유사도 threshold 이상인 가장 비슷한 별 k개까지."""
    if len(X) < 2:
        return []
    S = cosine_matrix(X)
    np.fill_diagonal(S, -1)
    out = set()
    for i in range(len(X)):
        for j in np.argsort(-S[i])[:k]:
            if S[i, j] >= threshold:
                out.add((min(i, j), max(i, j)))
    return [(int(i), int(j), float(S[i, j])) for i, j in sorted(out)]


def similar_days(X: np.ndarray, dates: list[str], top: int = 3) -> list[list[dict]]:
    """각 날짜마다 감정이 가장 비슷했던 다른 날 top개"""
    if len(X) < 2:
        return [[] for _ in range(len(X))]
    S = cosine_matrix(X)
    np.fill_diagonal(S, -1)
    return [[{"date": dates[j], "score": round(float(S[i, j]), 3)} for j in np.argsort(-S[i])[:top]]
            for i in range(len(X))]


def jsd(p: np.ndarray, q: np.ndarray) -> float:
    """두 감정 비율이 얼마나 다른지 (0 = 똑같음, 1에 가까울수록 다름)"""
    m = (p + q) / 2
    kl = lambda a, b: float(np.sum(a * (np.log2(a + 1e-12) - np.log2(b + 1e-12))))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def turning_points(entries: list[dict], top: int = 3, min_jsd: float = 0.25) -> list[dict]:
    """바로 이전 기록과 감정 구성이 크게 달라진 날 (전환점)"""
    X = matrix(entries)
    pts = []
    for i in range(1, len(X)):
        d = jsd(X[i - 1], X[i])
        if d >= min_jsd:
            pts.append({"date": entries[i]["date"], "from": EMO[int(X[i - 1].argmax())],
                        "to": EMO[int(X[i].argmax())], "jsd": round(d, 3)})
    return sorted(pts, key=lambda x: -x["jsd"])[:top]


def month_mean(entries: list[dict]) -> np.ndarray:
    X = matrix(entries)
    return X.mean(axis=0) if len(X) else np.zeros(len(EMO))


def co_occurring(entries: list[dict], min_share: float = 0.2) -> list[tuple[str, str, int]]:
    """두 감정이 함께 20% 이상 나타난 날 세기 (예: 설렘 + 불안)"""
    count: dict[tuple[str, str], int] = {}
    for p in matrix(entries):
        idx = [i for i in np.argsort(-p)[:2] if p[i] >= min_share]
        if len(idx) == 2:
            key = tuple(sorted((EMO[idx[0]], EMO[idx[1]])))
            count[key] = count.get(key, 0) + 1
    return sorted(((a, b, n) for (a, b), n in count.items()), key=lambda t: -t[2])


POSITIVE = ["기쁨", "설렘", "평온"]


def positive_share(entries: list[dict]) -> float | None:
    """긍정 감정(기쁨+설렘+평온) 평균 비율(%). 기록이 없으면 None"""
    if not entries:
        return None
    m = month_mean(entries)
    return float(sum(m[EMO.index(e)] for e in POSITIVE) * 100)


def layout3(X: np.ndarray, seed: int = 7) -> np.ndarray:
    """3D 감정 지도용: 주성분 3개를 -1~1로 맞춘 좌표 (2D/3D 전환에서 3D에 씀)"""
    n = len(X)
    rng = np.random.default_rng(seed)
    if n < 4:
        return rng.uniform(-.4, .4, size=(n, 3))
    Xc = X - X.mean(axis=0)
    _, _, vt = np.linalg.svd(Xc, full_matrices=False)
    P = Xc @ vt[:3].T
    P = P + rng.normal(0, 0.04, size=P.shape) * (P.std(axis=0) + 1e-6)
    m = np.abs(P).max(axis=0)
    return P / np.where(m < 1e-9, 1, m)
