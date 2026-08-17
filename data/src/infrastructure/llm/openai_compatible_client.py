"""
Adapter: ILLMClient'in kurumun kendi LLM sunucusuna (OpenAI-uyumlu API)
baglanan gerceklestirimi.
"""
from openai import OpenAI
from src.application.interfaces import ILLMClient


class OpenAICompatibleClient(ILLMClient):
    def __init__(self, base_url, api_key, model_name, temperature=0.3, max_tokens=500, timeout=90.0):
        self._client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout)
        self._model_name = model_name
        self._temperature = temperature
        self._max_tokens = max_tokens

    def generate(self, system_prompt, user_prompt):
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        return response.choices[0].message.content