from fastapi import FastAPI, HTTPException
import os
from pathlib import Path
import aiohttp
import json
from datetime import datetime
import sqlite3
import pandas as pd
from PIL import Image
import subprocess
import base64
import re
import numpy as np
import markdown
from bs4 import BeautifulSoup
import requests
from typing import Dict, Any, Optional

app = FastAPI()

class TaskHandler:
    def __init__(self):
        self.llm_token = os.environ.get("AIPROXY_TOKEN")
        if not self.llm_token:
            raise ValueError("AIPROXY_TOKEN environment variable not set")

    async def call_llm(self, prompt: str) -> str:
        """Call GPT-4-mini through AI Proxy"""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.llm_token}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            }
            async with session.post("https://api.aiproxy.x/v1/chat/completions", 
                                  headers=headers, json=data) as response:
                result = await response.json()
                return result["choices"][0]["message"]["content"]

    async def classify_task(self, task_description: str) -> str:
        """Use LLM to classify the task into predefined categories"""
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
        
        return (await self.call_llm(prompt)).strip()

    async def handle_task(self, task_description: str) -> Dict[str, Any]:
        """Main task handling function"""
        try:
            # Ensure we only access /data directory
            if '..' in task_description or not task_description.startswith('/data'):
                raise HTTPException(status_code=400, detail="Invalid path access")

            task_type = await self.classify_task(task_description)
            
            # Map task types to handler functions
            handlers = {
                'A1': self.handle_datagen,
                'A2': self.handle_format_markdown,
                'A3': self.handle_count_weekdays,
                'A4': self.handle_sort_contacts,
                'A5': self.handle_recent_logs,
                'A6': self.handle_markdown_index,
                'A7': self.handle_extract_email,
                'A8': self.handle_extract_card,
                'A9': self.handle_similar_comments,
                'A10': self.handle_ticket_sales
            }
            
            handler = handlers.get(task_type)
            if handler:
                return await handler(task_description)
            else:
                # Handle custom business tasks (B3-B10)
                return await self.handle_custom_task(task_description)

    async def handle_datagen(self, task: str) -> Dict[str, Any]:
        """Handle A1: Install and run datagen.py"""
        # Extract email using LLM
        email = await self.call_llm(f"Extract email from: {task}")
        
        # Download and run script
        url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to download script")

        with open("/tmp/datagen.py", "w") as f:
            f.write(response.text)

        result = subprocess.run(["python", "/tmp/datagen.py", email], capture_output=True, text=True)
        
        return {"status": "success", "output": result.stdout}

    async def handle_format_markdown(self, task: str) -> Dict[str, Any]:
        """Handle A2: Format markdown using prettier"""
        try:
            version = "3.4.2"  # Default version
            version_match = re.search(r'prettier@([\d.]+)', task)
            if version_match:
                version = version_match.group(1)

            subprocess.run(["npm", "install", "-g", f"prettier@{version}"])
            subprocess.run(["prettier", "--write", "/data/format.md"])
            
            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def handle_count_weekdays(self, task: str) -> Dict[str, Any]:
        """Handle A3: Count weekdays in dates file"""
        # Get input and output files from task using LLM
        files_info = await self.call_llm(f"""Extract input and output files from: {task}
        Return as JSON: {{"input": "path", "output": "path"}}""")
        files = json.loads(files_info)

        with open(files['input'], 'r') as f:
            dates = [line.strip() for line in f.readlines()]

        count = sum(1 for date in dates 
                   if datetime.strptime(date, '%Y-%m-%d').weekday() == 2)  # Wednesday = 2

        with open(files['output'], 'w') as f:
            f.write(str(count))

        return {"status": "success", "count": count}

    # ... Additional handlers for A4-A10 would go here ...

    async def handle_custom_task(self, task: str) -> Dict[str, Any]:
        """Handle custom business tasks (B3-B10)"""
        # Use LLM to understand task requirements
        task_info = await self.call_llm(f"""Analyze this task and return:
        {{
            "type": "api_fetch|git|sql|scraping|image|audio|markdown|csv",
            "parameters": {{...task specific parameters...}}
        }}
        
        Task: {task}""")
        
        task_info = json.loads(task_info)
        
        # Handle different types of custom tasks
        handlers = {
            'api_fetch': self.handle_api_fetch,
            'git': self.handle_git_operations,
            'sql': self.handle_sql_query,
            'scraping': self.handle_web_scraping,
            'image': self.handle_image_processing,
            'audio': self.handle_audio_transcription,
            'markdown': self.handle_markdown_conversion,
            'csv': self.handle_csv_filtering
        }
        
        handler = handlers.get(task_info['type'])
        if not handler:
            raise HTTPException(status_code=400, detail="Unsupported task type")
            
        return await handler(task_info['parameters'])

@app.post("/run")
async def run_task(task: str):
    """Execute a task described in plain English"""
    try:
        handler = TaskHandler()
        result = await handler.handle_task(task)
        return {"status": "success", "result": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
async def read_file(path: str):
    """Read and return file contents"""
    try:
        # Security check: only allow access to /data directory
        if not path.startswith("/data/"):
            raise HTTPException(status_code=400, detail="Access denied")
            
        file_path = Path(path)
        if not file_path.exists():
            raise HTTPException(status_code=404)
            
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))