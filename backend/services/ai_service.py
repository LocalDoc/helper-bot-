import httpx
import openai
from ..config import settings
from ..models.enums import AIProviderType
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.openai_client = None
            logger.warning("OpenAI API key not configured")
        
    async def process_message(
        self, 
        message: str, 
        provider: AIProviderType = AIProviderType.CHATGPT,
        model: str = "gpt-3.5-turbo"
    ) -> str:
        """Process message through selected AI provider. Returns AI response as string."""
        
        if provider == AIProviderType.CHATGPT:
            return await self._process_chatgpt(message, model)
        elif provider == AIProviderType.DEEPSEEK:
            return await self._process_deepseek(message, model)
        elif provider == AIProviderType.PERPLEXITY:
            return await self._process_perplexity(message, model)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    async def _process_chatgpt(self, message: str, model: str) -> str:
        """Process message using OpenAI ChatGPT"""
        try:
            if not self.openai_client:
                raise Exception("OpenAI API key not configured")
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if content is None:
                logger.warning("ChatGPT returned empty content")
                return "I received your message but couldn't generate a response. Please try again."
            
            return content
            
        except Exception as e:
            logger.error(f"ChatGPT error: {e}")
            raise Exception(f"ChatGPT processing failed: {str(e)}")
    
    async def _process_deepseek(self, message: str, model: str) -> str:
        """Process message using DeepSeek API"""
        try:
            if not settings.DEEPSEEK_API_KEY:
                raise Exception("DeepSeek API key not configured")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": message}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    if content is None:
                        logger.warning("DeepSeek returned empty content")
                        return "I received your message but couldn't generate a response. Please try again."
                    
                    return content
                else:
                    error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.error(f"DeepSeek error: {e}")
            raise Exception(f"DeepSeek processing failed: {str(e)}")
    
    async def _process_perplexity(self, message: str, model: str) -> str:
        """Process message using Perplexity API"""
        try:
            if not settings.PERPLEXITY_API_KEY:
                raise Exception("Perplexity API key not configured")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant. Be precise and concise."},
                            {"role": "user", "content": message}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    if content is None:
                        logger.warning("Perplexity returned empty content")
                        return "I received your message but couldn't generate a response. Please try again."
                    
                    return content
                else:
                    error_msg = f"Perplexity API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
            raise Exception(f"Perplexity processing failed: {str(e)}")

ai_service = AIService()