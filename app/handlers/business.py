from typing import Dict, Any
from fastapi import HTTPException
import requests
import json
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
import git
from ..utils.file_ops import read_file, write_file, read_json, write_json
from ..utils.llm import call_llm
from ..config import DATA_DIR

class BusinessHandler:
    @classmethod
    async def handle_api_fetch(cls, task_description: str) -> Dict[str, Any]:
        try:
            prompt = f"""Extract API details from this task as JSON:
            {{
                "url": "API endpoint URL",
                "method": "GET/POST",
                "headers": {},
                "output_file": "output filename"
            }}
            Task: {task_description}"""
            api_info = json.loads(await call_llm(prompt))

            response = requests.request(
                method=api_info['method'],
                url=api_info['url'],
                headers=api_info['headers']
            )

            output_path = DATA_DIR / api_info['output_file']
            if response.headers.get('content-type', '').startswith('application/json'):
                await write_json(output_path, response.json())
            else:
                await write_file(output_path, response.text)

            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_git_operations(cls, task_description: str) -> Dict[str, Any]:
        try:
            prompt = f"""Extract git operation details as JSON:
            {{
                "repo_url": "repository URL",
                "operation": "clone/commit",
                "branch": "branch name",
                "commit_message": "commit message if needed"
            }}
            Task: {task_description}"""
            git_info = json.loads(await call_llm(prompt))

            repo_path = DATA_DIR / "repo"

            if git_info['operation'] == 'clone':
                git.Repo.clone_from(git_info['repo_url'], repo_path)
            elif git_info['operation'] == 'commit':
                repo = git.Repo(repo_path)
                repo.git.add(A=True)
                repo.index.commit(git_info['commit_message'])
                origin = repo.remote('origin')
                origin.push()

            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_sql_query(cls, task_description: str) -> Dict[str, Any]:
        try:
            prompt = f"""Extract SQL query details as JSON:
            {{
                "database_file": "database filename",
                "query": "SQL query",
                "output_file": "output filename"
            }}
            Task: {task_description}"""
            query_info = json.loads(await call_llm(prompt))

            db_path = DATA_DIR / query_info['database_file']
            output_path = DATA_DIR / query_info['output_file']

            conn = sqlite3.connect(str(db_path))
            df = pd.read_sql_query(query_info['query'], conn)

            if output_path.suffix == '.json':
                await write_json(output_path, df.to_dict('records'))
            else:
                await write_file(output_path, df.to_csv(index=False))

            conn.close()
            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_web_scraping(cls, task_description: str) -> Dict[str, Any]:
        try:
            prompt = f"""Extract web scraping details as JSON:
            {{
                "url": "webpage URL",
                "selectors": ["CSS selectors to extract"],
                "output_file": "output filename"
            }}
            Task: {task_description}"""
            scrape_info = json.loads(await call_llm(prompt))

            response = requests.get(scrape_info['url'])
            soup = BeautifulSoup(response.text, 'html.parser')

            results = {}
            for selector in scrape_info['selectors']:
                elements = soup.select(selector)
                results[selector] = [elem.text.strip() for elem in elements]

            output_path = DATA_DIR / scrape_info['output_file']
            await write_json(output_path, results)

            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_image_processing(cls, task_description: str) -> Dict[str, Any]:
        try:
            prompt = f"""Extract image processing task details as JSON:
            {{
                "image_path": "path to the image",
                "operation": "resize/convert/filter",
                "output_path": "path to save the output image"
            }}
            Task: {task_description}"""
            image_info = json.loads(await call_llm(prompt))
            # Placeholder for image processing logic
            # Example: OpenCV, PIL or other libraries can be used here

            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_audio_transcription(cls, task_description: str) -> Dict[str, Any]:
        try:
            prompt = f"""Extract audio transcription task details as JSON:
            {{
                "audio_path": "path to the audio file",
                "output_path": "path to save the transcription"
            }}
            Task: {task_description}"""
            audio_info = json.loads(await call_llm(prompt))
            # Placeholder for audio transcription logic

            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_markdown_conversion(cls, task_description: str) -> Dict[str, Any]:
        try:
            prompt = f"""Extract markdown conversion task details as JSON:
            {{
                "input_path": "path to markdown file",
                "output_format": "html/pdf",
                "output_path": "path to save the converted file"
            }}
            Task: {task_description}"""
            markdown_info = json.loads(await call_llm(prompt))
            # Placeholder for markdown conversion logic

            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_csv_filtering(cls, task_description: str) -> Dict[str, Any]:
        try:
            prompt = f"""Extract CSV filtering task details as JSON:
            {{
                "csv_path": "path to csv file",
                "filter_conditions": {{"column_name": "value"}},
                "output_path": "path to save the filtered csv"
            }}
            Task: {task_description}"""
            csv_info = json.loads(await call_llm(prompt))
            # Placeholder for CSV filtering logic

            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
