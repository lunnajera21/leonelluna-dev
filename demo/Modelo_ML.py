# demo/Modelo_ML.py
import os
import json
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression,SGDClassifier
import numpy as np
from transformers import BertTokenizer, BertModel
import torch
# ==========================
# FastAPI app
# ==========================
app = FastAPI()

# ==========================
# Archivos
# ==========================
DATA_FILE = "comentarios.json"
FEEDBACK_FILE = "feedback.json"

for file in [DATA_FILE, FEEDBACK_FILE]:
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump([], f)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# ==========================
# Normalizar tipo
# ==========================
tipo_map = {
    "bueno": "Bueno", "bien": "Bueno", "positivo": "Bueno", "satisfactorio": "Bueno",
    "malo": "Malo", "mal": "Malo", "deficiente": "Malo", "negativo": "Malo"
}
for item in data:
    item["tipo"] = tipo_map.get(item["tipo"].lower(), item["tipo"])

# ==========================
# LabelEncoder
# ==========================
tipos = [item["tipo"] for item in data] if data else ["Bueno", "Malo"]
palabras = [item["palabra_clave"] for item in data] if data else ["general"]

tipo_encoder = LabelEncoder()
tipo_encoder.fit(tipos)

palabra_encoder = LabelEncoder()
palabra_encoder.fit(palabras)

# ==========================
# BETO como vectorizador
# ==========================
MODEL_NAME = "dccuchile/bert-base-spanish-wwm-cased"
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
beto_model = BertModel.from_pretrained(MODEL_NAME)
beto_model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
beto_model.to(device)

def embed_texts(texts):
    embeddings = []
    with torch.no_grad():
        for text in texts:
            encoded = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128).to(device)
            output = beto_model(**encoded)
            cls_emb = output.last_hidden_state[:,0,:].cpu().numpy()
            embeddings.append(cls_emb.flatten())
    return np.array(embeddings)

# ==========================
# Clasificadores ligeros
# ==========================
if data:
    X_tipo = embed_texts([d["comentario"] for d in data])
    y_tipo = tipo_encoder.transform([d["tipo"] for d in data])
    tipo_clf = SGDClassifier(loss="log_loss", max_iter=1000)
    tipo_clf.fit(X_tipo, y_tipo)

    X_palabra = embed_texts([d["comentario"] for d in data])
    y_palabra = palabra_encoder.transform([d["palabra_clave"] for d in data])
    palabra_clf = SGDClassifier(loss="log_loss", max_iter=1000)
    palabra_clf.fit(X_palabra, y_palabra)
else:
    tipo_clf = SGDClassifier(loss="log_loss", max_iter=1000)
    palabra_clf = SGDClassifier(loss="log_loss", max_iter=1000)

# ==========================
# Predicción
# ==========================
def predecir_tipo_palabra(texto):
    X = embed_texts([texto])
    tipo_pred = tipo_encoder.inverse_transform(tipo_clf.predict(X))[0]
    palabra_pred = palabra_encoder.inverse_transform(palabra_clf.predict(X))[0]
    return tipo_pred, palabra_pred

# ==========================
# Fine-tuning incremental
# ==========================
def fine_tune_incremental(comentario, tipo_real, palabra_real):
    # Guardar feedback
    with open(FEEDBACK_FILE, "r+", encoding="utf-8") as f:
        fb = json.load(f)
        fb.append({"comentario": comentario, "tipo": tipo_real, "palabra_clave": palabra_real})
        f.seek(0)
        json.dump(fb, f, ensure_ascii=False, indent=2)

    global tipo_encoder, palabra_encoder, tipo_clf, palabra_clf

    if tipo_real not in tipo_encoder.classes_:
        tipos_nuevos = list(tipo_encoder.classes_) + [tipo_real]
        tipo_encoder.fit(tipos_nuevos)
    if palabra_real not in palabra_encoder.classes_:
        palabras_nuevas = list(palabra_encoder.classes_) + [palabra_real]
        palabra_encoder.fit(palabras_nuevas)

    X = embed_texts([comentario])
    tipo_clf.partial_fit(X, tipo_encoder.transform([tipo_real]), classes=np.arange(len(tipo_encoder.classes_)))
    palabra_clf.partial_fit(X, palabra_encoder.transform([palabra_real]), classes=np.arange(len(palabra_encoder.classes_)))

# ==========================
# Requests
# ==========================
class PrediccionRequest(BaseModel):
    comentario: str

class FeedbackRequest(BaseModel):
    comentario: str
    tipo_real: str
    palabra_real: str
    feedback: Optional[str] = None

# ==========================
# HTML
# ==========================
HTML_CONTENT = """<html>
<head>
    <title>Predicción de Comentarios</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; }
        h1 { color: #2F4F4F; }
        textarea, select, input { width: 100%; padding: 10px; margin-bottom: 10px; font-size: 1rem; }
        button { padding: 10px 20px; font-size: 1rem; margin-right: 10px; margin-top:5px; }
        .resultado { background: #f0f0f0; padding: 10px; border-radius: 5px; margin-top:10px; }
        label { font-weight: bold; }
        .disabled { background: #e0e0e0; }
    </style>
</head>
<body>
<h1>Predicción de Comentarios</h1>
<label>Escribe tu comentario:</label>
<textarea id="comentario_input" rows="4" placeholder="Escribe tu comentario aquí"></textarea><br>
<button onclick="predecir()">Predecir</button>
<div class="resultado">
    <label>Comentario:</label>
    <input type="text" id="comentario" class="disabled" disabled><br>
    <label>Tipo de comentario:</label>
    <input type="text" id="tipo" class="disabled" disabled><br>
    <label>Palabra clave:</label>
    <input type="text" id="palabra" class="disabled" disabled><br>
    <button onclick="feedback('bien')">Correcto</button>
    <button onclick="mostrarDropdown()">Incorrecto</button>
</div>
<div id="feedback_div" style="margin-top:10px;"></div>
<script>
let lastComentario = "";
async function predecir() {
    let comentario = document.getElementById('comentario_input').value.trim();
    if (!comentario) return alert("Escribe un comentario primero");
    let response = await fetch('/demo/predecir/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({comentario: comentario})
    });
    let data = await response.json();
    document.getElementById('comentario_input').value = "";
    lastComentario = comentario;
    document.getElementById('comentario').value = comentario;
    document.getElementById('tipo').value = data.resultado.tipo_estimado;
    document.getElementById('palabra').value = data.resultado.palabra_clave_estimado;
    document.getElementById('feedback_div').innerHTML = "";
}
function mostrarDropdown() {
    if (!lastComentario) return alert("Primero predice un comentario.");
    let tipoOptions = ["Bueno", "Malo"];
    let html = '<label>Selecciona tipo real:</label>';
    html += '<select id="tipo_real">';
    tipoOptions.forEach(opt => html += `<option value="${opt}">${opt}</option>`);
    html += '</select><br>';
    html += '<label>Ingresa palabra clave real:</label>';
    html += '<input type="text" id="palabra_real" placeholder="Ej: servicio"><br>';
    html += '<button onclick="feedback('+"'mal'"+')">Enviar Feedback</button>';
    document.getElementById('feedback_div').innerHTML = html;
}
async function feedback(feedback_value) {
    if (!lastComentario) return alert("Primero predice un comentario.");
    let tipo_real = "";
    let palabra_real = "";
    if (feedback_value === "mal") {
        tipo_real = document.getElementById('tipo_real').value;
        palabra_real = document.getElementById('palabra_real').value.trim();
        if (!tipo_real || !palabra_real) return alert("Completa todos los campos");
    } else {
        tipo_real = document.getElementById('tipo').value;
        palabra_real = document.getElementById('palabra').value;
    }
    let response = await fetch('/demo/retroalimentacion/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            comentario: lastComentario,
            tipo_real: tipo_real,
            palabra_real: palabra_real,
            feedback: feedback_value
        })
    });
    let data = await response.json();
    document.getElementById('tipo').value = tipo_real;
    document.getElementById('palabra').value = palabra_real;
    document.getElementById('feedback_div').innerHTML = "Feedback registrado: " + data.feedback_recibido;
    lastComentario = "";
}
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_CONTENT

@app.post("/predecir/")
def predecir_endpoint(request: PrediccionRequest):
    tipo_pred, palabra_pred = predecir_tipo_palabra(request.comentario)
    return {"resultado": {"tipo_estimado": tipo_pred, "palabra_clave_estimado": palabra_pred}}

@app.post("/retroalimentacion/")
def feedback_endpoint(request: FeedbackRequest):
    fine_tune_incremental(request.comentario, request.tipo_real, request.palabra_real)
    return {"feedback_recibido": "OK"}
