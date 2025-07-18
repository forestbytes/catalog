from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chat_app_gpt_example import backend

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_input = req.message.strip()
    results = backend.search_catalog(user_input, top_k=5)
    answer = None
    if user_input.endswith("?"):
        answer = backend.answer_question(user_input, results)
    return {
        "results": results,
        "answer": answer,
    }

@app.get("/", response_class=HTMLResponse)
async def index():
    # Minimal chat UI
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Catalog Chat</title>
        <style>
            body { font-family: sans-serif; margin: 2em; }
            #chat { width: 100%; max-width: 700px; margin: auto; }
            .msg { margin-bottom: 1em; }
            .user { color: #1a237e; }
            .bot { color: #00695c; }
            .entry { background: #f1f8e9; padding: 0.5em; margin: 0.5em 0; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div id="chat">
            <h2>Data Catalog Chat</h2>
            <div id="messages"></div>
            <form id="chatForm">
                <input type="text" id="userInput" autocomplete="off" style="width:80%;" placeholder="Type your query or question..." />
                <button type="submit">Send</button>
            </form>
        </div>
        <script>
            const form = document.getElementById('chatForm');
            const input = document.getElementById('userInput');
            const messages = document.getElementById('messages');
            form.onsubmit = async (e) => {
                e.preventDefault();
                const msg = input.value.trim();
                if (!msg) return;
                messages.innerHTML += `<div class="msg user"><b>You:</b> ${msg}</div>`;
                input.value = '';
                messages.innerHTML += `<div class="msg bot"><i>Searching...</i></div>`;
                const resp = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await resp.json();
                messages.innerHTML = messages.innerHTML.replace('<div class="msg bot"><i>Searching...</i></div>', '');
                if (data.results && data.results.length) {
                    data.results.forEach((entry, idx) => {
                        messages.innerHTML += `<div class="entry">
                            <b>[${idx+1}] ${entry.title || '(No Title)'}</b><br>
                            <i>${entry.description || ''}</i><br>
                            <b>Authors:</b> ${(entry.authors || []).join(', ')}<br>
                            <b>Keywords:</b> ${(entry.keywords || []).join(', ')}<br>
                            <b>Data Source:</b> ${entry.data_source || ''}<br>
                            <b>Chunk Index:</b> ${entry.chunk_index}<br>
                            <b>Distance:</b> ${entry.distance.toFixed(4)}<br>
                            <b>Chunk Text:</b> ${entry.chunk_text ? entry.chunk_text.slice(0, 300) + (entry.chunk_text.length > 300 ? '...' : '') : ''}
                        </div>`;
                    });
                } else {
                    messages.innerHTML += `<div class="msg bot">No relevant catalog entries found.</div>`;
                }
                if (data.answer) {
                    messages.innerHTML += `<div class="msg bot"><b>Q&A:</b> ${data.answer}</div>`;
                }
                messages.scrollTop = messages.scrollHeight;
            };
        </script>
    </body>
    </html>
    """
