"""
Jarwin LLM Engine
Supports Ollama (free, local) and OpenAI (optional, paid).
Falls back gracefully if no LLM is available.
"""

import os
import json
import requests
from typing import Optional


class LLMEngine:
    """Unified LLM interface supporting multiple providers."""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if any LLM provider is available."""
        if self.provider == "openai" and self.openai_key:
            return True
        if self.provider == "ollama":
            try:
                r = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
                return r.status_code == 200
            except:
                return False
        return False
    
    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> Optional[str]:
        """Generate a response from the LLM."""
        if not self.available:
            return None
        
        if self.provider == "openai" and self.openai_key:
            return self._call_openai(prompt, system_prompt, temperature)
        elif self.provider == "ollama":
            return self._call_ollama(prompt, system_prompt, temperature)
        return None
    
    def _call_ollama(self, prompt: str, system_prompt: str, temperature: float) -> Optional[str]:
        """Call Ollama local LLM."""
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {"temperature": temperature}
            }
            r = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            if r.status_code == 200:
                return r.json().get("response", "")
            return None
        except:
            return None
    
    def _call_openai(self, prompt: str, system_prompt: str, temperature: float) -> Optional[str]:
        """Call OpenAI API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature
            }
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            return None
        except:
            return None


# Singleton instance
_engine = None

def get_llm() -> LLMEngine:
    """Get or create the LLM engine singleton."""
    global _engine
    if _engine is None:
        _engine = LLMEngine()
    return _engine
