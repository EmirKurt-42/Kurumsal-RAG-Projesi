"""
Demo icin kucuk API sarmalayici: mevcut RAG use case'ini HTTP uzerinden acar.
(TAM ŞİFA SÜRÜMÜ: KALICI JSON VERİTABANI EKLENDİ)
"""
import uuid
import json
import os
from typing import Optional, List, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import chromadb
from datetime import datetime, timedelta

from container import Container

# === ANA SUNUCU TANIMI (Hatanın Çözüldüğü Yer) ===
app = FastAPI(title="Konya Veri - Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

container = Container()

# --- KALICI VERİTABANI (JSON) ---
DB_FILE = "chat_db.json"

def load_sessions() -> Dict[str, dict]:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_sessions():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(SESSIONS, f, ensure_ascii=False, indent=2)

SESSIONS: Dict[str, dict] = load_sessions()

class SoruIstek(BaseModel):
    soru: str
    session_id: Optional[str] = None

@app.get("/sessions")
def get_sessions():
    result = []
    for sid, data in reversed(list(SESSIONS.items())):
        result.append({"id": sid, "title": data["title"]})
    return result

@app.get("/sessions/{session_id}")
def get_session_history(session_id: str):
    if session_id not in SESSIONS:
        return {"history": []}
    return {"history": SESSIONS[session_id]["history"]}

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    if session_id in SESSIONS:
        del SESSIONS[session_id]
        save_sessions() 
    return {"status": "ok"}

@app.post("/ask")
def ask(istek: SoruIstek):
    session_id = istek.session_id
    if not session_id or session_id not in SESSIONS:
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {"title": "Yeni Sohbet", "history": []}
        is_first_message = True
    else:
        is_first_message = len(SESSIONS[session_id]["history"]) == 0

    history = SESSIONS[session_id]["history"]
    chunks, answer = container.answer_question.execute(istek.soru, history=history)

    new_message_user = {"rol": "kullanici", "metin": istek.soru}
    new_message_ai = {
        "rol": "asistan", 
        "metin": answer, 
        "kaynaklar": [
            {
                "kaynak": c["source"],
                "baslik": c["title"],
                "url": c["url"],
                "tarih": c.get("gosterim_tarihi"),
            }
            for c in chunks
        ],
    }
    
    SESSIONS[session_id]["history"].append(new_message_user)
    SESSIONS[session_id]["history"].append(new_message_ai)

    if is_first_message:
        try:
            ozet_prompt = f"Kullanıcı şu soruyu sordu: '{istek.soru}'. Bu sohbet için yan menüde görünecek 3 kelimelik kısa ve resmi bir başlık üret. Sadece başlığı yaz, tırnak veya açıklama kullanma.\nBaşlık:"
            title = container.llm_client.generate("Sen bir başlık üreticisisin. Sadece 3 kelime yaz.", ozet_prompt)
            SESSIONS[session_id]["title"] = title.replace('"', '').replace("'", "").strip()[:40]
        except:
            SESSIONS[session_id]["title"] = istek.soru[:30] + "..."

    save_sessions() 
    return {
        "session_id": session_id,
        "cevap": answer,
        "title": SESSIONS[session_id]["title"],
        "kaynaklar": new_message_ai["kaynaklar"],
    }

@app.get("/health")
def health():
    return {"status": "ok"}


# ==========================================
# AYARLAR HAFIZASI (ORTAK VERİ YOLU)
# ==========================================
CURRENT_SETTINGS = {
    "accentColor": "#0B3D62", 
    "threshold": 0.2,
    "timeLimit": "2_months"
}

@app.get("/admin/settings")
def get_settings():
    return CURRENT_SETTINGS

@app.post("/admin/settings")
def update_settings(new_settings: dict):
    global CURRENT_SETTINGS
    for key, value in new_settings.items():
        if value is not None:
            CURRENT_SETTINGS[key] = value
    return {"status": "ok", "settings": CURRENT_SETTINGS}


# ==========================================
# ADMIN PANELİ İÇİN ÖZEL TEST KANALI
# ==========================================
class AdminTestIstek(BaseModel):
    soru: str
    threshold: float
    time_limit: str

@app.post("/admin/test_rag")
def admin_test_rag(istek: AdminTestIstek):
    if istek.time_limit == "unlimited":
        sinir_tarihi_sayi = 0
    else:
        gunler = 60
        if istek.time_limit == "1_month": gunler = 30
        elif istek.time_limit == "2_months": gunler = 60
        elif istek.time_limit == "6_months": gunler = 180
        gecmis = datetime.now() - timedelta(days=gunler)
        sinir_tarihi_sayi = int(gecmis.strftime('%Y%m%d'))

    zaman_filtresi = {
        "$or": [
            {"is_haber": False}, 
            {
                "$and": [
                    {"is_haber": True}, 
                    {"yayin_tarihi": {"$gte": sinir_tarihi_sayi}}
                ]
            }
        ]
    }

    client = chromadb.PersistentClient(path="./chroma_db")
    koleksiyon_adi = client.list_collections()[0].name
    collection = client.get_collection(name=koleksiyon_adi)

    sonuc = collection.query(
        query_texts=[istek.soru],
        n_results=10, 
        where=zaman_filtresi 
    )

    formatli_sonuclar = []
    if sonuc['ids'] and len(sonuc['ids'][0]) > 0:
        for i in range(len(sonuc['ids'][0])):
            mesafe = sonuc['distances'][0][i]
            benzerlik_skoru = 1.0 - mesafe 
            
            if benzerlik_skoru < istek.threshold:
                continue

            belge_id = sonuc['ids'][0][i]
            meta = sonuc['metadatas'][0][i]
            
            formatli_sonuclar.append({
                "id": str(i) + belge_id,
                "title": meta.get("title", belge_id),
                "type": "HABER" if meta.get("is_haber") else "KALICI BELGE (Koski/Komek)",
                "date": meta.get("yayin_tarihi", "Sınır Yok"),
                "score": round(benzerlik_skoru, 2)
            })
            
    return {"sonuclar": formatli_sonuclar}