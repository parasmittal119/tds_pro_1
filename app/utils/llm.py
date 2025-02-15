import aiohttp
from typing import Dict, Any
from fastapi import HTTPException
from ..config import AIPROXY_TOKEN, AIPROXY_URL, LLM_MODEL

async def call_llm(prompt: str) -> str:
    """Make API call to LLM through AI Proxy"""
    if not AIPROXY_TOKEN:
        raise ValueError("AIPROXY_TOKEN environment variable not set")

    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {AIPROXY_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "model": LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            async with session.post(AIPROXY_URL, headers=headers, json=data, verify=False) as response:
                if response.status != 200:
                    raise HTTPException(status_code=500, detail="LLM API call failed")
                result = await response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM API error: {str(e)}")

async def classify_task(task_description: str) -> str:
    """Classify task into predefined categories"""
    prompt = f"""Classify this task into one of these categories:
    A1: datagen.py installation/running
    A2: markdown formatting
    A3: counting weekdays
    A4: sorting contacts
    A5: log file processing
    A6: markdown indexing
    A7: email extraction
    A8: credit card extraction
    A9: comment similarity
    A10: ticket sales calculation
    B3-B10: custom business tasks
    
    Task: {task_description}
    
    Return only the category (e.g. 'A1', 'B3')."""
    
    return (await call_llm(prompt)).strip()
