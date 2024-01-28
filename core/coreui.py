from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from brotli_asgi import BrotliMiddleware
import os

from controllers import secure, public, socket
from shared import setup, tracing

app = FastAPI()

origins = []

origins.append(setup.get_www_client_domain_name())
origins.append(setup.get_client_domain_name())
if os.getenv("ENVIRONMENT") != "production":
  origins.append("http://localhost:4200")
  origins.append("http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(BrotliMiddleware)
app.add_middleware(tracing.OpentracingMiddleware)

@app.on_event("startup")
async def startup():
  tracing.init_tracer(app)


app.include_router(secure.router)
app.include_router(public.router)
app.include_router(socket.router)
