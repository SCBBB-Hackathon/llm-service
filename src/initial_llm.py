from transformers import AutoTokenizer 
from vllm import SamplingParams 
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs 
from vllm.lora.request import LoRARequest 
from vllm.sampling_params import RequestOutputKind
from vllm.sampling_params import StructuredOutputsParams
from utils.getAPI import getApiKey
from src.tools.etiquette_tool import Etiquette_Tool
from src.tools.websearch_tool import WebSearchTool
import asyncio 


class LoadLLM():
    def __init__(self):
        _culture_lora_path = getApiKey("CULTURE_LORA_PATH")
        _language_lora_path = getApiKey("LANG_LORA_PATH")
        self.lora_list = {
            "culture": LoRARequest("culture", 1, _culture_lora_path),
            "lang": LoRARequest("language", 2, _language_lora_path),
            "None": None
        }

        #tool 로드
        self.etiquette = Etiquette_Tool()
        self.websearch = WebSearchTool()


        
    async def _run_llm(self, request_id, messages, lora_req):
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        try:
            async for output in self.engine.generate(
                request_id=request_id,
                prompt=prompt,
                sampling_params=self.sampling_params,
                lora_request=self.lora_list[lora_req]
            ):
                for completion in output.outputs:
                    new_text = completion.text
                    if new_text:
                        yield new_text


                # if output.finished:

        except asyncio.CancelledError:
            await self.engine.abort(request_id)
            raise

        except Exception as e:
            raise RuntimeError(f"Error during LLM streaming: {e}") from e


    async def process_requests_stream(self, request_id: str, query: str, lora_req: str):
        if self.websearch.check_place(query):
            messages = [
                {"role": "user", "content": f"{query}에 대해 알려주세요"}
            ]

            async for chunk in self._run_llm(request_id, messages, lora_req):
                yield chunk

        else:
            yield "잘 모르는 내용이라 웹에서 검색한 뒤 알려드리겠습니다...\n"
            search_result = await self.websearch.search_query(query)
            lora_req = "None"

            if search_result:
                messages = [
                    {"role": "user",
                    "content": f"{query}에 대해 검색한 결과는 {search_result}입니다. "
                                f"이 내용을 잘 정리해서 대화처럼 설명해주세요."}
                ]


                async for chunk in self._run_llm(request_id, messages, lora_req):
                    yield chunk
            else:
                yield "웹 검색에서 문제가 발생했습니다."


    async def process_requests(self, request_id: str, query: str, lora_req: str):
        chunks = [] 
        if self._check_place(query):
            messages = [
                {"role": "user", "content": f"{query}에 대해 알려주세요"}
            ]

            # JSON(dict) return
            async for chunk in self._run_llm(request_id, messages, lora_req):
                chunks.append(chunk)
            full_text = "".join(chunks).strip()
            return {"result": full_text}

        else:
            search_result = await self.websearch.search_query(query)
            lora_req = "None"

            if search_result:
                messages = [
                    {"role": "user",
                    "content": f"""{query}에 대해 검색한 결과는 {search_result}입니다. 
                                    이 내용을 잘 정리해서 대화처럼 설명해주세요."""}
                ]

                async for chunk in self._run_llm(request_id, messages, lora_req):
                    chunks.append(chunk)
                full_text = "".join(chunks).strip()
                return {"result": full_text}

            else:
                return {"error": "웹 검색에서 문제가 발생했습니다."}


    async def get_etiquette_llm(self, request_id: str, place: str, category: str)-> AsyncLLMEngine:
        chunks = []
        search_result = self.etiquette.get_etiquette(category)
        lora_req = "None"

        if search_result == None:
            return 

        messages = [
            {"role": "user",
            "content": f"""{place}에 대한 공공예절은 {search_result}입니다. 
                        이 내용을 잘 정리해서 대화처럼 설명해주세요."""}
        ]

        async for chunk in self._run_llm(request_id, messages, lora_req):
            chunks.append(chunk)
        full_text = "".join(chunks).strip()
        return {"result": full_text}




    # 카테고리 가져오고 그걸 정리하는 llm까지 연계하도록 수정
    async def get_etiquette_category(self, request_id: str,query: str)-> AsyncLLMEngine:
        """Continuously process a list of prompts and handle the outputs."""
        buffer = ""
        prompt = f"당신은 특정 장소를 받고 그 장소에 맞는 예절 종류를 골라야합니다. 장소명: {query}"

        try:
            # Stream tokens from AsyncLLM
            async for output in self.engine.generate(
                request_id=request_id, 
                prompt=prompt, 
                sampling_params=self.etiquette_sampling_params
            ):
                # Process each completion in the output
                for completion in output.outputs:
                    # In DELTA mode, we get only new tokens generated since last iteration
                    new_text = completion.text
                    if new_text:
                        buffer += new_text

                if output.finished:
                    yield buffer.strip()

        except asyncio.CancelledError:
            await self.engine.abort(request_id)

        except Exception as e:
            yield f"\nError during streaming: {e}"




    def initialize_engine(
        self, model: str, quantization: str
    ) -> AsyncLLMEngine:
        """Initialize the LLMEngine."""

        tokenizer = AutoTokenizer.from_pretrained(getApiKey("LLM_BASE_MODEL_PATH"))
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = 'right'

        structured_outputs_params = StructuredOutputsParams(choice=["지하철", "버스", "에스컬레이터", "식당"])

        eos_token_id = [tokenizer.eos_token_id,  tokenizer.convert_tokens_to_ids("<|eot_id|>")]
        self.sampling_params = SamplingParams(
            temperature=0.5, 
            top_p=0.9, 
            stop_token_ids=eos_token_id, 
            logprobs=1, 
            prompt_logprobs=1, 
            max_tokens=512, 
            repetition_penalty=1.2,   # 반복 억제 핵심
            output_kind=RequestOutputKind.DELTA
        )

        self.etiquette_sampling_params = SamplingParams(
            temperature=0.2, 
            top_p=0.9, 
            stop_token_ids=eos_token_id, 
            logprobs=1, 
            prompt_logprobs=1, 
            max_tokens=20, 
            repetition_penalty=1.2,   # 반복 억제 핵심
            output_kind=RequestOutputKind.DELTA,
            structured_outputs=structured_outputs_params
        )

        engine_args = AsyncEngineArgs(
            model=model,
            quantization=quantization,
            enable_lora=True,
            max_lora_rank=64,
            max_loras=4,
            max_model_len=2048,
            gpu_memory_utilization=0.8  # GPU 메모리 활용 비율 상향
        )
        
        self.tokenizer = tokenizer
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    def shutdown(self):
        self.engine.shutdown()