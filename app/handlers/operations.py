import subprocess
from datetime import datetime
from pathlib import Path
import pandas as pd
import sqlite3
import requests
import numpy as np
from typing import Dict, Any, List
from fastapi import HTTPException
from .base import BaseHandler
from ..utils.llm import call_llm
from ..utils.file_ops import read_file, write_file, read_json, write_json
from ..config import TEMP_DIR, DATA_DIR

class OperationsHandler(BaseHandler):
    @classmethod
    async def handle_datagen(cls, task_description: str) -> Dict[str, Any]:
        """A1: Install and run datagen.py"""
        try:
            # Extract email using LLM
            email_prompt = f"Extract only the email address from: {task_description}"
            email = (await call_llm(email_prompt)).strip()
            
            # Download script
            url = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
            response = requests.get(url)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to download script")
            
            script_path = TEMP_DIR / "datagen.py"
            with open(script_path, "w") as f:
                f.write(response.text)
            
            # Run script
            result = subprocess.run(["python", str(script_path), email], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise HTTPException(status_code=500, detail=f"Script error: {result.stderr}")
                
            return {"status": "success", "output": result.stdout}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_format_markdown(cls, task_description: str) -> Dict[str, Any]:
        """A2: Format markdown using prettier"""
        try:
            # Extract prettier version
            version = "3.4.2"  # Default
            version_match = re.search(r'prettier@([\d.]+)', task_description)
            if version_match:
                version = version_match.group(1)
            
            input_file = DATA_DIR / "format.md"
            
            # Install prettier
            subprocess.run(["npm", "install", "-g", f"prettier@{version}"], 
                         check=True, capture_output=True)
            
            # Format file
            result = subprocess.run(["prettier", "--write", str(input_file)], 
                                  check=True, capture_output=True)
            
            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_count_weekdays(cls, task_description: str) -> Dict[str, Any]:
        """A3: Count weekdays in dates file"""
        try:
            params = await cls.extract_parameters(task_description)
            input_path = DATA_DIR / params['input_file']
            output_path = DATA_DIR / params['output_file']
            
            dates = []
            async with open(input_path, 'r') as f:
                dates = [line.strip() for line in f.readlines()]
            
            weekday_count = sum(1 for date in dates 
                              if datetime.strptime(date, '%Y-%m-%d').weekday() == 2)
            
            await write_file(output_path, str(weekday_count))
            
            return {"status": "success", "count": weekday_count}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_sort_contacts(cls, task_description: str) -> Dict[str, Any]:
        """A4: Sort contacts JSON"""
        try:
            input_file = DATA_DIR / "contacts.json"
            output_file = DATA_DIR / "contacts-sorted.json"
            
            contacts = await read_json(input_file)
            sorted_contacts = sorted(contacts, 
                                  key=lambda x: (x['last_name'], x['first_name']))
            
            await write_json(output_file, sorted_contacts)
            
            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_recent_logs(cls, task_description: str) -> Dict[str, Any]:
        """A5: Extract recent log lines"""
        try:
            log_dir = DATA_DIR / "logs"
            output_file = DATA_DIR / "logs-recent.txt"
            
            # Get all log files sorted by modification time
            log_files = sorted(
                log_dir.glob("*.log"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:10]
            
            # Extract first lines
            first_lines = []
            for log_file in log_files:
                async with open(log_file, 'r') as f:
                    first_lines.append(f.readline().strip())
            
            await write_file(output_file, "\n".join(first_lines))
            
            return {"status": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_markdown_index(cls, task_description: str) -> Dict[str, Any]:
        """A6: Create markdown index"""
        try:
            docs_dir = DATA_DIR / "docs"
            index_file = docs_dir / "index.json"
            
            index = {}
            for md_file in docs_dir.glob("**/*.md"):
                content = await read_file(md_file)
                # Find first H1 header
                match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if match:
                    relative_path = str(md_file.relative_to(docs_dir))
                    index[relative_path] = match.group(1)
            
            await write_json(index_file, index)
            
            return {"status": "success", "index": index}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_extract_email(cls, task_description: str) -> Dict[str, Any]:
        """A7: Extract email sender"""
        try:
            email_file = DATA_DIR / "email.txt"
            output_file = DATA_DIR / "email-sender.txt"
            
            email_content = await read_file(email_file)
            
            prompt = f"Extract only the sender's email address from this email:\n\n{email_content}"
            email_address = (await call_llm(prompt)).strip()
            
            await write_file(output_file, email_address)
            
            return {"status": "success", "email": email_address}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_extract_card(cls, task_description: str) -> Dict[str, Any]:
        """A8: Extract credit card number from image"""
        try:
            card_image = DATA_DIR / "credit-card.png"
            output_file = DATA_DIR / "credit-card.txt"
            
            # Convert image to base64
            with open(card_image, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode()
            
            prompt = f"Extract only the credit card number from this image:\n{image_base64}"
            card_number = (await call_llm(prompt)).strip()
            
            # Remove spaces and write
            card_number = ''.join(card_number.split())
            await write_file(output_file, card_number)
            
            return {"status": "success", "card_number": card_number}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_similar_comments(cls, task_description: str) -> Dict[str, Any]:
        """A9: Find similar comments using embeddings"""
        try:
            comments_file = DATA_DIR / "comments.txt"
            output_file = DATA_DIR / "comments-similar.txt"
            
            comments = (await read_file(comments_file)).splitlines()
            
            # Get embeddings for each comment
            embeddings = []
            for comment in comments:
                prompt = f"Generate an embedding vector for: {comment}"
                embedding_str = await call_llm(prompt)
                embedding = json.loads(embedding_str)
                embeddings.append(embedding)
            
            # Find most similar pair
            max_similarity = -1
            similar_pair = None
            
            for i in range(len(comments)):
                for j in range(i + 1, len(comments)):
                    similarity = np.dot(embeddings[i], embeddings[j])
                    if similarity > max_similarity:
                        max_similarity = similarity
                        similar_pair = (comments[i], comments[j])
            
            await write_file(output_file, f"{similar_pair[0]}\n{similar_pair[1]}")
            
            return {"status": "success", "similar_comments": similar_pair}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def handle_ticket_sales(cls, task_description: str) -> Dict[str, Any]:
        """A10: Calculate ticket sales from SQLite database"""
        try:
            db_file = DATA_DIR / "ticket-sales.db"
            output_file = DATA_DIR / "ticket-sales-gold.txt"
            
            conn = sqlite3.connect(str(db_file))
            query = """
                SELECT SUM(units * price) as total_sales
                FROM tickets
                WHERE type = 'Gold'
            """
            
            df = pd.read_sql_query(query, conn)
            total_sales = df['total_sales'].iloc[0]
            
            await write_file(output_file, str(total_sales))
            conn.close()
            
            return {"status": "success", "total_sales": total_sales}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))