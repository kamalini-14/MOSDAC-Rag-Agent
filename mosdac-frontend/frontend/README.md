# MOSDAC AI Help Bot – Frontend (React + Vite)

## Windows + VS Code setup
1. Install Node.js LTS from https://nodejs.org (check: `node -v`, `npm -v` in a new terminal).
2. Open the `frontend` folder in VS Code (File > Open Folder). Open a terminal (Ctrl+`).
3. Copy the env file: `copy .env.example .env`
4. Install: `npm install`
5. Start your backend in its own terminal (project root): `python -m uvicorn backend.main:app --reload`
6. Start the frontend: `npm run dev` then open http://localhost:5173

## CORS (required)
Your FastAPI app must allow the frontend origin. If it does not already, add to `backend/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
```
(This is the one small backend edit you may need; the frontend itself changes nothing.)

## Test checklist
- [ ] Landing page animates; Launch goes to login
- [ ] Register (8+ chars, matching passwords) -> auto login, or "Account created. Please log in."
- [ ] Wrong password shows an error; correct login opens the chat
- [ ] DevTools > Network: `/auth/me` and later requests send `Authorization: Bearer ...`
- [ ] Ask a question: conversation created (`POST /conversations/`), answer from `POST /chat/ask`
- [ ] Sidebar lists conversations; clicking one loads history; you can continue it
- [ ] Refresh the page: session persists (tab only); Logout returns to login
- [ ] Stop the backend: sidebar shows "Backend unreachable" and sends show a clear error

## Troubleshooting
- **"Cannot reach the backend"**: backend not running, wrong `VITE_API_BASE_URL` (restart `npm run dev` after editing `.env`), or CORS missing (browser console shows a CORS error).
- **401/403**: token missing/expired; you are returned to login. Check `/auth/login` returns `access_token`.
- **Sidebar empty / messages blank**: response shape differs. Compare the JSON in http://127.0.0.1:8000/docs with the field names in `ChatLayout.jsx` (`chat_id`, `question`, `answer`, `sources`) and adjust there.
- **422 errors**: shown as `field: message`; fix the request body in `src/api.js`.
