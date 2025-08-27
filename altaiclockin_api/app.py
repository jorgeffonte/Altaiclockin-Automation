from fastapi import FastAPI, HTTPException
import subprocess

app = FastAPI()

@app.post("/checkin")
def checkin():
    try:
        subprocess.check_call(["python3", "altaiclockin.py", "checkin"])
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/checkout")
def checkout():
    try:
        subprocess.check_call(["python3", "altaiclockin.py", "checkout"])
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def status():
    return {"alive": True}
