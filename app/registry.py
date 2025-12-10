from typing import Callable, Dict, Any, List

class ToolRegistry:
    _tools: Dict[str, Callable] = {}
    _conditions: Dict[str, Callable] = {}

    @classmethod
    def register_tool(cls, name: str = None):
        def decorator(func: Callable):
            tool_name = name or func.__name__
            cls._tools[tool_name] = func
            return func
        return decorator

    @classmethod
    def register_condition(cls, name: str = None):
        def decorator(func: Callable):
            cond_name = name or func.__name__
            cls._conditions[cond_name] = func
            return func
        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Callable:
        return cls._tools.get(name)

    @classmethod
    def get_condition(cls, name: str) -> Callable:
        return cls._conditions.get(name)



@ToolRegistry.register_tool()
def split_text_to_chunks(state: Dict[str, Any]) -> Dict[str, Any]:
    text = state.get("text", "")
    max_chars = state.get("_node_config", {}).get("max_chunk_chars", 1000)
    
    chunks = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
    return {"chunks": chunks}

@ToolRegistry.register_tool()
def summarize_chunk_rule_based(state: Dict[str, Any]) -> Dict[str, Any]:

    
    chunks = state.get("chunks", [])
    summaries = []
    for chunk in chunks:
        # Simple heuristic: First sentence
        summary = chunk.split('.')[0] + "."
        summaries.append(summary)
    
    return {"summaries": summaries}

@ToolRegistry.register_tool()
def merge_summaries(state: Dict[str, Any]) -> Dict[str, Any]:
    summaries = state.get("summaries", [])
    merged = " ".join(summaries)
    return {"merged_summary": merged}

@ToolRegistry.register_tool()
def refine_summary(state: Dict[str, Any]) -> Dict[str, Any]:
   
    current_summary = state.get("final_summary") or state.get("merged_summary", "")
    max_length = state.get("max_length", 100) # Global config or state param
    
    if len(current_summary) <= max_length:
        return {"final_summary": current_summary}
    
    sentences = current_summary.split('.')
    if len(sentences) > 1:
      
        real_sentences = [s for s in sentences if s.strip()]
        if len(real_sentences) > 1:
             refined = ".".join(real_sentences[:-1]) + "."
        else:
             refined = current_summary[:max_length]
    else:
        
        refined = current_summary[:max_length]
    
    
    if len(refined) > max_length:
        refined = refined[:max_length]

    return {"final_summary": refined}



@ToolRegistry.register_condition()
def summary_length_below_limit(state: Dict[str, Any]) -> bool:
    summary = state.get("final_summary", "")
    max_length = state.get("max_length", 100)
    return len(summary) <= max_length

@ToolRegistry.register_condition()
def summary_length_above_limit(state: Dict[str, Any]) -> bool:
    return not summary_length_below_limit(state)
