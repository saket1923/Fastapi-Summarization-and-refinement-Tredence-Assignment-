import asyncio
import copy
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.models.api_models import GraphDefinition, ExecutionLogEntry
from app.run_store import save_run, update_run, get_run
from app.registry import ToolRegistry


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
        
        save_run(self.run_id, {
            "run_id": self.run_id,
            "status": "running",
            "state": initial_state,
            "execution_log": []
        })
        
        
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

                start_ts = datetime.utcnow()
                
                action_func = ToolRegistry.get_tool(node_def.action_name)
                if not action_func:
                    raise ValueError(f"Tool {node_def.action_name} not found")

                
                state["_node_config"] = node_def.config
                
                logger.info(f"Executing {current_node_id}...")
                
                if asyncio.iscoroutinefunction(action_func):
                    result_updates = await action_func(copy.deepcopy(state))
                else:
                    result_updates = action_func(copy.deepcopy(state))
                
                if result_updates and isinstance(result_updates, dict):
                    state.update(result_updates)
                
                end_ts = datetime.utcnow()
                
               
                log_entry = ExecutionLogEntry(
                    node_id=current_node_id,
                    start_ts=start_ts,
                    end_ts=end_ts,
                    state_snapshot=copy.deepcopy(state)
                )
                
               
                current_run_data = get_run(self.run_id)
                current_log = current_run_data.get("execution_log", [])
                current_log.append(log_entry.dict())
                
                update_run(self.run_id, {
                    "state": state,
                    "execution_log": current_log
                })
                
                steps += 1

                
                edges = self.edges_map.get(current_node_id, [])
                next_node_id = None
                
                for edge in edges:
                    
                    condition_met = True
                    if edge.condition_name:
                        cond_func = ToolRegistry.get_condition(edge.condition_name)
                        if cond_func:
                            
                            condition_met = cond_func(state)
                        else:
                            logger.warning(f"Condition {edge.condition_name} not found, assuming False")
                            condition_met = False
                    
                    if condition_met:
                        next_node_id = edge.target_id
                       
                        break
                
                current_node_id = next_node_id

            update_run(self.run_id, {"status": "completed"})

        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            update_run(self.run_id, {
                "status": "failed",
                "error": str(e)
            })
