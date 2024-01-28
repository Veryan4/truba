from fastapi import FastAPI

from shared import tracing
from controllers import private

app = FastAPI()
app.add_middleware(tracing.OpentracingMiddleware)


@app.on_event('startup')
async def startup():
  tracing.init_tracer(app)


app.include_router(private.router)
