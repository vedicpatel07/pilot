from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
import json
import logging
from datetime import datetime
import os
from xarmController import XArmController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaskExecutor")

class TaskExecutor:
    def __init__(self, robot: XArmController, api_endpoint: str, api_key: str):
        """
        Initialize TaskExecutor.
        
        Args:
            robot: Instance of XArmController
            api_endpoint: URL of the OpenPi VLA endpoint
            api_key: API key for authentication
        """
        self.robot = robot
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Define common robot tasks and their parameter templates
        self.task_templates = {
            "move": {
                "params": ["x", "y", "z", "speed"],
                "method": self.robot.move_to_position
            },
            "home": {
                "params": ["speed"],
                "method": self.robot.home
            },
            "pick": {
                "params": ["x", "y", "z", "speed"],
                "method": self._execute_pick
            },
            "place": {
                "params": ["x", "y", "z", "speed"],
                "method": self._execute_place
            }
        }

    async def process_task(self, task_description: str) -> Dict[str, Any]:
        """
        Process a natural language task through VLA and execute on robot.
        
        Args:
            task_description: Natural language description of the task
            
        Returns:
            Dict containing task execution results
        """
        try:
            # Get robot commands from VLA
            vla_response = await self._get_vla_response(task_description)
            
            # Parse and execute commands
            execution_results = await self._execute_vla_commands(vla_response)
            
            return {
                "status": "success",
                "task_description": task_description,
                "execution_results": execution_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "task_description": task_description,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _get_vla_response(self, task_description: str) -> Dict[str, Any]:
        """
        Get response from VLA endpoint.
        """
        async with aiohttp.ClientSession() as session:
            payload = {
                "task": task_description,
                "robot_state": self.robot.get_status(),
                "available_commands": list(self.task_templates.keys())
            }
            
            async with session.post(
                self.api_endpoint,
                headers=self.headers,
                json=payload
            ) as response:
                if response.status != 200:
                    raise Exception(f"VLA API error: {response.status}")
                return await response.json()

    async def _execute_vla_commands(self, vla_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute the commands returned by VLA.
        """
        results = []
        commands = vla_response.get("commands", [])
        
        for cmd in commands:
            try:
                cmd_type = cmd.get("type")
                params = cmd.get("parameters", {})
                
                if cmd_type not in self.task_templates:
                    raise ValueError(f"Unknown command type: {cmd_type}")
                
                template = self.task_templates[cmd_type]
                method = template["method"]
                
                # Execute the command
                result = await asyncio.to_thread(method, **params)
                
                results.append({
                    "command": cmd_type,
                    "parameters": params,
                    "status": "success",
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "command": cmd.get("type"),
                    "parameters": cmd.get("parameters"),
                    "status": "error",
                    "error": str(e)
                })
                logger.error(f"Error executing command: {str(e)}")
                # Depending on error handling strategy, might want to break here
                
        return results

    def _execute_pick(self, x: float, y: float, z: float, speed: Optional[float] = None) -> int:
        """
        Execute a pick operation.
        """
        # Move above pick position
        code = self.robot.move_to_position(x=x, y=y, z=z + 50, speed=speed, wait=True)
        if code != 0:
            return code
            
        # Move to pick position
        code = self.robot.move_to_position(x=x, y=y, z=z, speed=speed/2, wait=True)
        if code != 0:
            return code
            
        # Activate gripper/vacuum
        # Note: Implementation depends on end effector type
        # self.robot.set_vacuum_gripper(True)
        
        # Move up with object
        return self.robot.move_to_position(x=x, y=y, z=z + 50, speed=speed/2, wait=True)

    def _execute_place(self, x: float, y: float, z: float, speed: Optional[float] = None) -> int:
        """
        Execute a place operation.
        """
        # Move above place position
        code = self.robot.move_to_position(x=x, y=y, z=z + 50, speed=speed, wait=True)
        if code != 0:
            return code
            
        # Move to place position
        code = self.robot.move_to_position(x=x, y=y, z=z, speed=speed/2, wait=True)
        if code != 0:
            return code
            
        # Deactivate gripper/vacuum
        # Note: Implementation depends on end effector type
        # self.robot.set_vacuum_gripper(False)
        
        # Move up
        return self.robot.move_to_position(x=x, y=y, z=z + 50, speed=speed/2, wait=True)

# Example usage
if __name__ == "__main__":
    # Load configuration from environment variables
    ROBOT_IP = os.getenv("ROBOT_IP", "192.168.1.100")
    VLA_ENDPOINT = os.getenv("VLA_ENDPOINT", "https://api.example.com/vla")
    API_KEY = os.getenv("VLA_API_KEY", "your-api-key")
    
    # Initialize robot and executor
    robot = XArmController(ROBOT_IP, is_radian=False)
    executor = TaskExecutor(robot, VLA_ENDPOINT, API_KEY)
    
    async def run_example():
        # Connect to robot
        if robot.connect():
            try:
                # Process a natural language task
                result = await executor.process_task(
                    "Pick up the red cube from position 1 and place it at position 2"
                )
                print(f"Task execution result: {json.dumps(result, indent=2)}")
                
            finally:
                robot.disconnect()
    
    # Run the example
    asyncio.run(run_example())