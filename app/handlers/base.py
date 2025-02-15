from typing import Dict, Any
from fastapi import HTTPException
from ..utils.llm import call_llm, classify_task

class BaseHandler:
    """Base class for task handlers"""
    
    @classmethod
    async def handle(cls, task_description: str) -> Dict[str, Any]:
        """Main handler method to be implemented by subclasses"""
        raise NotImplementedError
    
    @classmethod
    async def validate_task(cls, task_description: str) -> None:
        """Validate task description"""
        if not task_description or not isinstance(task_description, str):
            raise HTTPException(status_code=400, detail="Invalid task description")
    
    @classmethod
    async def extract_parameters(cls, task_description: str) -> Dict[str, Any]:
        """Extract parameters from task description using LLM"""
        prompt = f"""Extract parameters from this task:
        {task_description}
        
        Return as JSON with these fields:
        - input_file: input file path if any
        - output_file: output file path if any
        - parameters: any other task-specific parameters
        """
        
        try:
            result = await call_llm(prompt)
            return json.loads(result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting parameters: {str(e)}")
