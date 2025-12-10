import asyncio
import copy
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Node:
    def __init__(self, id: str, action: Callable, name: str = None):
        self.id = id
        self.action = action
        self.name = name or id

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the node's action and updates the state."""
        logger.info(f"Executing node: {self.id}")
        try:
            if asyncio.iscoroutinefunction(self.action):
                result = await self.action(copy.deepcopy(state))
            else:
                result = self.action(copy.deepcopy(state))
            
            if isinstance(result, dict):
                state.update(result)
            return state
        except Exception as e:
            logger.error(f"Error executing node {self.id}: {e}")
            raise e

class Edge:
    def __init__(self, source_id: str, target_id: str, condition: Callable[[Dict[str, Any]], bool] = None):
        self.source_id = source_id
        self.target_id = target_id
        self.condition = condition

    def check_condition(self, state: Dict[str, Any]) -> bool:
        if self.condition is None:
            return True
        return self.condition(state)

class Graph:
    def __init__(self, id: str, start_node_id: str):
        self.id = id
        self.start_node_id = start_node_id
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_outgoing_edges(self, node_id: str) -> List[Edge]:
        return [edge for edge in self.edges if edge.source_id == node_id]

class WorkflowEngine:
    def __init__(self, graph: Graph):
        self.graph = graph

    async def run(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Runs the workflow starting from the start node."""
        state = copy.deepcopy(initial_state)
        current_node_id = self.graph.start_node_id
        execution_log = []

        max_steps = 100
        steps = 0

        while current_node_id and steps < max_steps:
            current_node = self.graph.get_node(current_node_id)
            if not current_node:
                logger.error(f"Node {current_node_id} not found.")
                break

           
            execution_log.append(current_node_id)
            state = await current_node.execute(state)
            steps += 1

           
            edges = self.graph.get_outgoing_edges(current_node_id)
            next_node_id = None
            
            for edge in edges:
                if edge.check_condition(state):
                    next_node_id = edge.target_id
                    break # Take the first matching edge (priority)
            
            current_node_id = next_node_id

        state["_execution_log"] = execution_log
        return state
