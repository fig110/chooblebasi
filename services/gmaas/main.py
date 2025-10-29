from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time, uuid

app = FastAPI(title="GMaaS Stub")

class MediaRequest(BaseModel):
    correlation_id: str
    user_id: str
    session_id: str
    prompt: str

@app.get("/healthz")
def healthz():
    return JSONResponse({"ok": True})

@app.post("/media/request")
def media_request(req: MediaRequest):
    # Pretend to queue a job and return a signed URL later
    job_id = str(uuid.uuid4())
    return {"job_id": job_id, "status": "queued"}
