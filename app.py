from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
from tasks import calculate_pi

app = FastAPI(
    title="Pi Calculation API",
    description="Calculate Pi to arbitrary precision using Celery background tasks",
    version="1.0"
)

# Start Pi calculation task
@app.get("/calculate_pi")
async def start_calculate_pi(n: int = Query(10, description="Number of decimal digits")):
    task = calculate_pi.delay(n)
    return {"task_id": task.id}

# Check progress of a task
@app.get("/check_progress/{task_id}")
async def check_progress(task_id: str):
    task = AsyncResult(task_id, app=calculate_pi.app)

    if task.state == "PENDING":
        return JSONResponse({"state": "PROGRESS", "progress": 0.0, "result": None}, status_code=202)
    elif task.state == "PROGRESS":
        return {"state": "PROGRESS", "progress": task.info.get("progress", 0.0), "result": None}
    elif task.state == "SUCCESS":
        return {"state": "FINISHED", "progress": 1.0, "result": task.result}
    elif task.state == "FAILURE":
        return {"state": "FAILURE", "progress": 1.0, "result": None, "error": str(task.info)}
