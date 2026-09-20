import os
from typing import Optional

def classify_task(modality: str, prompt: str, file_name: Optional[str] = None) -> str:
    """
    Deterministic router based on Phase 1 hackathon heuristics.
    Returns one of: 'vision_pipeline', 'calc_pipeline', 'memo_pipeline'
    """
    prompt_lower = prompt.lower()
    modality_lower = modality.lower()
    
    # 1. Vision Pipeline: Triggered if a file is present and it's an image/PDF, or if modality mentions vision/scan
    if file_name:
        ext = os.path.splitext(file_name)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.pdf']:
            return "vision_pipeline"
            
    if "vision" in modality_lower or "scan" in modality_lower or "inspection" in modality_lower:
        return "vision_pipeline"
        
    # 2. Calc Pipeline: Triggered by keywords related to math/calculations
    calc_keywords = ["calculate", "pressure", "corrosion", "math", "formula", "rate"]
    if any(kw in prompt_lower for kw in calc_keywords) or any(kw in modality_lower for kw in calc_keywords):
        return "calc_pipeline"
        
    # 3. Default fallback is Memo / Reasoning Pipeline
    return "memo_pipeline"
