import asyncio
import copy
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.models.api_models import GraphDefinition, ExecutionLogEntry
from app.run_store import save_run, update_run, get_run
from app.registry import ToolRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(self, graph_def: GraphDefinition, run_id: str = None):
        self.graph_def = graph_def
        self.run_id = run_id or str(uuid.uuid4())
        self.nodes_map = {n.id: n for n in self.graph_def.nodes}
        self.edges_map = {} # source_id -> list of edges
        for edge in self.graph_def.edges:
            if edge.source_id not in self.edges_map:
                self.edges_map[edge.source_id] = []
            self.edges_map[edge.source_id].append(edge)

    async def run_async(self, initial_state: Dict[str, Any], config: Dict[str, Any] = {}):
        """Starts the workflow in the background."""
        # Initialize run record
        save_run(self.run_id, {
            "run_id": self.run_id,
            "status": "running",
            "state": initial_state,
            "execution_log": []
        })
        
        # Fire and forget (or rather, run in background task)
        asyncio.create_task(self._execute(initial_state, config))
        return self.run_id

    async def run_sync(self, initial_state: Dict[str, Any], config: Dict[str, Any] = {}):
        """Runs the workflow synchronously and returns the result."""
        save_run(self.run_id, {
            "run_id": self.run_id,
            "status": "running",
            "state": initial_state,
            "execution_log": []
        })
        
        await self._execute(initial_state, config)
        return get_run(self.run_id)

    async def _execute(self, state: Dict[str, Any], config: Dict[str, Any]):
        current_node_id = self.graph_def.start_node_id
        max_iterations = config.get("max_iterations", 100)
        steps = 0
        
        try:
            while current_node_id and steps < max_iterations:
                node_def = self.nodes_map.get(current_node_id)
                if not node_def:
                    raise ValueError(f"Node {current_node_id} not found")

                # 1. Execute Node
                start_ts = datetime.utcnow()
                
                action_func = ToolRegistry.get_tool(node_def.action_name)
                if not action_func:
                    raise ValueError(f"Tool {node_def.action_name} not found")

                # Prepare args: state + config
                # Note: The requirement says nodes accept shared `state`.
                # We can pass config as part of state or separate? 
                # Requirement: "Nodes are plain Python functions that accept and return a shared `state` dict."
                # So we pass state. We can merge node config into state temporarily or just rely on state.
                # Let's assume node config is static params, maybe passed?
                # For simplicity, let's update state with node config if needed, or just pass state.
                # The prompt says: "Nodes... accept and return a shared state dict".
                # But we also have `config` in NodeDefinition. 
                # Let's inject `node_config` into state for the function to use?
                
                # Make a copy for safety? Or modify in place? Requirement: "modify a shared state dict".
                # We should probably pass a copy to avoid side effects if we want to keep history?
                # But usually state is mutable.
                
                # Inject node config into state under a special key?
                state["_node_config"] = node_def.config
                
                logger.info(f"Executing {current_node_id}...")
                
                if asyncio.iscoroutinefunction(action_func):
                    result_updates = await action_func(copy.deepcopy(state))
                else:
                    result_updates = action_func(copy.deepcopy(state))
                
                if result_updates and isinstance(result_updates, dict):
                    state.update(result_updates)
                
                end_ts = datetime.utcnow()
                
                # Log execution
                log_entry = ExecutionLogEntry(
                    node_id=current_node_id,
                    start_ts=start_ts,
                    end_ts=end_ts,
                    state_snapshot=copy.deepcopy(state)
                )
                
                # Update run store
                current_run_data = get_run(self.run_id)
                current_log = current_run_data.get("execution_log", [])
                current_log.append(log_entry.dict())
                
                update_run(self.run_id, {
                    "state": state,
                    "execution_log": current_log
                })
                
                steps += 1

                # 2. Determine Next Node
                edges = self.edges_map.get(current_node_id, [])
                next_node_id = None
                
                for edge in edges:
                    # Check condition
                    condition_met = True
                    if edge.condition_name:
                        cond_func = ToolRegistry.get_condition(edge.condition_name)
                        if cond_func:
                            # Condition functions also take state?
                            # Requirement: "condition_name that resolves to a condition function... returns bool"
                            # "summary_length_below_limit(state, param_max_length)"
                            condition_met = cond_func(state)
                        else:
                            logger.warning(f"Condition {edge.condition_name} not found, assuming False")
                            condition_met = False
                    
                    if condition_met:
                        next_node_id = edge.target_id
                        # If loop is True, we might stay here? 
                        # Requirement: "Looping: allow a node to be re-invoked until a condition... is met"
                        # This is handled by the edge pointing back to the same node (or previous).
                        # The `loop` bool in EdgeDefinition might be metadata, but the graph structure dictates the loop.
                        break
                
                current_node_id = next_node_id

            update_run(self.run_id, {"status": "completed"})

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            update_run(self.run_id, {
                "status": "failed",
                "error": str(e)
            })
