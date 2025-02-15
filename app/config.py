import os
from pathlib import Path

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# LLM Configuration
AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")
AIPROXY_URL = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
LLM_MODEL = "gpt-4o-mini"

# File System Configuration
DATA_DIR = Path("/data")
TEMP_DIR = Path("/tmp")

# Security Configuration
ALLOWED_DIRS = [DATA_DIR]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Task Categories
TASK_CATEGORIES = {
    "A1": "datagen",
    "A2": "format_markdown",
    "A3": "count_weekdays",
    "A4": "sort_contacts",
    "A5": "recent_logs",
    "A6": "markdown_index",
    "A7": "extract_email",
    "A8": "extract_card",
    "A9": "similar_comments",
    "A10": "ticket_sales",
    "B3": "api_fetch",
    "B4": "git_operations",
    "B5": "sql_query",
    "B6": "web_scraping",
    "B7": "image_processing",
    "B8": "audio_transcription",
    "B9": "markdown_to_html",
    "B10": "csv_filter"
}