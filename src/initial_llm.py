from transformers import AutoTokenizer 
from vllm import SamplingParams 
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.engine.arg_utils import AsyncEngineArgs 
from vllm.lora.request import LoRARequest 
from vllm.sampling_params import RequestOutputKind
from utils.getAPI import getApiKey
import asyncio 


class LoadLLM():
    def __init__(self):
        _culture_lora_path = getApiKey("LLM_MODEL_PATH")
        self.lora_list = {
            "culture": LoRARequest("culture", 1, _culture_lora_path)
        }

    async def process_requests(
        self,
        request_id: str,
        query: list,
        lora_req: str,
        stream: bool = False
    ):
        messages = [
            {"role": "user", "content": query}
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False,
            add_generation_prompt=True # inference 때는 True 로 assistant 자리 생성함
        )
        buffer = ""
        """Continuously process a list of prompts and handle the outputs."""
        try:
            # Stream tokens from AsyncLLM
            async for output in self.engine.generate(
                request_id=request_id, 
                prompt=prompt, 
                sampling_params=self.sampling_params, 
                lora_request=self.lora_list[lora_req]
            ):
                # Process each completion in the output
                for completion in output.outputs:
                    # In DELTA mode, we get only new tokens generated since last iteration
                    new_text = completion.text
                    if new_text:
                        if stream:
                            yield new_text
                        else:
                            buffer += new_text

                # Check if generation is finished
                if output.finished:
                    if not stream:
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