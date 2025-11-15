from dotenv import load_dotenv
import os

# 환경 값 가져오기 (k8s에서는 이미 ENV 변수 주입됨)
envStatus = os.getenv("ENV")
print(envStatus)

# prod 환경: K8s Secret을 통해 이미 환경 변수가 주입되므로 .env 로드 X
if envStatus == "prod":
    print("Running in PROD using Kubernetes Secrets (no dotenv load).")

# dev 환경: .env_dev 로드
elif envStatus == "dev":
    print("Running in DEV loading .env")
    load_dotenv(dotenv_path=".env", override=True, verbose=True)

else:
    raise Exception("Wrong Env")


def getApiKey(apiName: str):
    key = os.getenv(apiName)
    if key is None:
        raise Exception(f"No Api Key: {apiName}")
    return key