from app.models.api_models import GraphDefinition, NodeDefinition, EdgeDefinition

def create_summarization_workflow() -> GraphDefinition:
    nodes = [
        NodeDefinition(id="split_text", action_name="split_text_to_chunks", config={"max_chunk_chars": 50}),
        NodeDefinition(id="summarize_chunks", action_name="summarize_chunk_rule_based"),
        NodeDefinition(id="merge_summaries", action_name="merge_summaries"),
        NodeDefinition(id="refine_final_summary", action_name="refine_summary")
    ]

    edges = [
        # split -> summarize
        EdgeDefinition(source_id="split_text", target_id="summarize_chunks"),
        # summarize -> merge
        EdgeDefinition(source_id="summarize_chunks", target_id="merge_summaries"),
        # merge -> refine
        EdgeDefinition(source_id="merge_summaries", target_id="refine_final_summary"),
        
        # Loop: refine -> refine (if too long)
        EdgeDefinition(
            source_id="refine_final_summary", 
            target_id="refine_final_summary", 
            condition_name="summary_length_above_limit",
            loop=True
        )
        # Implicit: if condition not met (i.e., length OK), no edge matches -> Stop.
    ]

    return GraphDefinition(
        id="summarization_workflow",
        start_node_id="split_text",
        nodes=nodes,
        edges=edges
    )
