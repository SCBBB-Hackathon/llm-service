# (산채비빔밥) 서울 도슨트 PYTHON API 서비스

fastAPI와 vllm을 이용하여 reference하는 API 서비스이다.  
vllm을 이용하여 기존 transformer라이브러리보다 더 빠른 속도의 추론능력을 제공하고 구조화된 출력이나 도구 사용 등 여러 기능들이 내장되어 있어, langchain없이도 구조적인 출력이 가능하다.  

---

## WorkFlow
사용자 요청에 따른 동작구조 워크플로우는 다음과 같다.  
### 관광지 LLM 요청  
![img1](https://github.com/SCBBB-Hackathon/llm-service/blob/main/readme_imgs/qr_llm.png?raw=true)  
### 대중교통 LLM 요청  
![img2](https://github.com/SCBBB-Hackathon/llm-service/blob/main/readme_imgs/trans_llm.png?raw=true)  
--- 

## Main Librarys
- fastAPI
- vllm 
- redis-python
- transformers
- bitsandbytes
- peft
- unsloth

## Using APIs
- Kakaomap API
- Googlemap API
- Tavily API