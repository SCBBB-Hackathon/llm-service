from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from src.initial_llm import LoadLLM
# from redis_client.redis_client import RedisClient
from utils.getAPI import getApiKey

from middleware.middleware import AuthMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware)
app.add_middleware(AuthMiddleware)

# ---------------------------
# Startup에서 LLM 로드
# ---------------------------
@app.on_event("startup")
async def load_startup():
    print("Loading LLM model on startup...")
    app.state.load_llm = LoadLLM()
    app.state.load_llm.initialize_engine(getApiKey("LLM_BASE_MODEL_PATH"), "bitsandbytes")  # 원하는 모델로 변경 가능
    print("LLM Loaded!")

    # print("Loading Redis on startup")
    # app.state.redis_client = RedisClient(config={
    #     "host": getApiKey("REDIS_HOST"),
    #     "port": getApiKey("REDIS_PORT"),
    #     "db": getApiKey("REDIS_DB")
    # })
    # print("Redis Loaded!")

# ---------------------------
# Pydantic 모델
# ---------------------------
class Query(BaseModel):
    prompt: str
    lora: str = None


# ---------------------------
# LLM을 활용하는 엔드포인트
# ---------------------------
@app.post("/generate")
async def generate_text(query: Query):
    if app.state.load_llm is None:
        return JSONResponse(
            status_code=500,
            content={"error": "LLM is not loaded yet"}
        )
    prompt = query.prompt
    lora = query.lora

    output = await app.state.load_llm.process_requests("", prompt, lora, stream=False)

    return JSONResponse(
        status_code=200,
        content={"text":output}
    )

# ---------------------------
# LLM을 활용하는 엔드포인트(streaming)
# ---------------------------
@app.post("/generate-stream")
async def generate_text_stream(query: Query):
    prompt = query.prompt
    lora = query.lora

    return StreamingResponse(app.state.load_llm.process_requests("", prompt, lora, stream=True))


# ---------------------------
# 헬스체크 엔드포인트
# ---------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("shutdown")
async def cleanup_vllm():
    await app.state.load_llm.shutdown()