from celery import Celery
from decimal import Decimal, getcontext
from time import sleep
from config import Config

config = Config()

# Celery app using Redis from environment variables
app = Celery("tasks", broker=config.redis_url, backend=config.redis_url)


@app.task(bind=True)
def calculate_pi(self, n: int):
    """
    Calculates Pi to n decimal digits using Chudnovsky algorithm with progress updates.
    """
    getcontext().prec = n + 10

    C = 426880 * Decimal(10005).sqrt()
    M = Decimal(1)
    L = Decimal(13591409)
    X = Decimal(1)
    K = Decimal(6)
    S = L

    total_steps = n
    for i in range(1, total_steps):
        M = M * (K**3 - 16*K) / (i**3)
        L += 545140134
        X *= -262537412640768000
        S += Decimal(M * L) / X
        K += 12

        # Update task progress
        self.update_state(state="PROGRESS", meta={"progress": round(i / total_steps, 4)})
        sleep(1) 
        
    pi = C / S
    return str(+pi.quantize(Decimal(10) ** -n))
