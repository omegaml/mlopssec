import os
import requests
from flask import Flask, render_template, request, redirect
from .llm import ask_llm
from .rag import retrieve, extend_prompt

app = Flask(__name__)

# kleine Chat-History im Speicher
chat_history = []

# simple RAG to upload documents
UPLOAD_FOLDER = "playground/data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if prompt:
            extended_prompt = extend_prompt(prompt)
            response = ask_llm(chat_history, extended_prompt)
            chat_history.append({
                "role": "user",
                "content": prompt
            })
            chat_history.append({
                "role": "assistant",
                "content": response
            })
            # History begrenzen
            max_messages = 10
            if len(chat_history) > max_messages:
                del chat_history[:-max_messages]

    return render_template(
        "index.html",
        history=chat_history
    )

@app.route("/reset", methods=["POST"])
def reset():
    global chat_history
    chat_history = []
    return redirect("/")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if file and file.filename.endswith(".txt"):
        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)
    return redirect("/")

