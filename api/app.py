from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.initial_llm import LoadLLM
# from redis_client.redis_client import RedisClient
from utils.getAPI import getApiKey
from schema.model import * 
from mongoDB.db_initial import create_mongo_client

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

    client = create_mongo_client()
    app.state.mongo_client = client
    app.state.mongo_db = client[getApiKey("MONGO_DB")]
    print("MongoDB Connected!")

# Dependency: 요청마다 DB 핸들 제공
async def get_db():
    return app.state.mongo_db

# ---------------------------
# LLM을 활용하는 엔드포인트
# ---------------------------
#response_model_exclude_none => 기본값이 None인 필드에 값이 안들어가면 없이 response
@app.post("/generate", response_model=LLMResponse, response_model_exclude_none=True)
async def generate_text(query: LLMRequest):
    if app.state.load_llm is None:
        return JSONResponse(
            status_code=500,
            content={"error": "LLM is not loaded yet"}
        )
    prompt = query.prompt
    lora = query.lora

    try:
        output = await app.state.load_llm.process_requests("", prompt, lora)
        response = {
            "success": True,
            "status_code": 200,
            "text": output
        }
        return response
    except Exception as e:
        response = {
            "success": False,
            "status_code": 500,
            "error_msg": e
        }
        return response

# ---------------------------
# LLM을 활용하는 엔드포인트(streaming)
# ---------------------------
@app.post("/generate-stream")
async def generate_text_stream(query: LLMRequest):
    prompt = query.prompt
    lora = query.lora

    return StreamingResponse(app.state.load_llm.process_requests_stream("", prompt, lora))

@app.post("/chat")
async def chat_llm(query: LLMChatRequest, db=Depends(get_db)):
    prompt = query.prompt 
    chat_id = query.chat_id 
    place = query.chat_id 

    lora = "None"

@app.post("/get-etiquette", response_model=LLMResponse, response_model_exclude_none=True)
async def get_etiquette(query: EtiquetteRequest):
    prompt = query.prompt
    place = query.place

    try:
        query_result = await app.state.load_llm.get_etiquette_llm("", place, prompt)
        if query_result:
            response = {
                "success": True,
                "status_code": 200,
                "text": query_result
            }
            return response
    except Exception as e:
        response = {
            "success": False,
            "status_code": 500,
            "error_msg": e
        }
        return response



# deprecated
@app.post("/get-etiquette-choice")
async def get_etiquette_choice(query: EtiquetteChoiceRequest):
    prompt = query.prompt

    return StreamingResponse(app.state.load_llm.get_etiquette_llm("", prompt))

# ---------------------------
# 헬스체크 엔드포인트
# ---------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("shutdown")
async def cleanup_vllm():
    await app.state.load_llm.shutdown()