from perception import ScenePerception
from xarmController import XArmController
import numpy as np
from typing import Optional, Tuple, Dict, List, Union
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RobotCommander")

class RobotCommander:
    """
    Integrates scene perception and robot control for sequential natural language commanded operations.
    """
    def __init__(self, robot_ip: str, enable_visualization: bool = True):
        """
        Initialize the robot commander.
        
        Args:
            robot_ip: IP address of the xArm robot
            enable_visualization: Whether to enable visual feedback of perception
        """
        self.perception = ScenePerception(enable_visualization=enable_visualization)
        self.robot = XArmController(robot_ip, is_radian=False)
        
        # Connect to robot
        if not self.robot.connect():
            raise RuntimeError("Failed to connect to xArm robot")
        
        # Motion parameters
        self.default_speed = 100  # mm/s
        self.approach_speed = 50  # mm/s for final approaches
        self.safe_height = 200    # mm for move-over positions
        self.grip_height = 50     # mm offset for gripping
        self.drop_height = 100    # mm offset for dropping
        
        # Track current state
        self.held_object = None   # Keep track of what the robot is holding
        
        logger.info("RobotCommander initialized successfully")
    
    def _extract_object_name(self, command: str) -> str:
        """Extract object name from command using common patterns."""
        patterns = [
            r"pick up (?:the )?(\w+)",
            r"move (?:the )?(\w+)",
            r"drop (?:the )?(\w+)",
            r"put (?:the )?(\w+)",
            r"grab (?:the )?(\w+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command.lower())
            if match:
                return match.group(1)
        
        return None
    
    def _extract_target_location(self, command: str) -> str:
        """Extract target location from command."""
        patterns = [
            r"to (?:the )?(\w+)",
            r"in (?:the )?(\w+)",
            r"on (?:the )?(\w+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command.lower())
            if match:
                return match.group(1)
        
        return None

    def _convert_camera_to_robot_frame(self, camera_pos: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Convert coordinates from camera frame to robot frame.
        Camera is:
        - 270mm right of robot (+X)
        - 460mm above robot base (+Z)
        - Rotated 25° CCW around Z (-25° rotation)
        - Tilted 30° down around Y (-30° rotation)
        """
        # Convert degrees to radians
        theta_z = np.radians(-25)  # -25° around Z
        theta_y = np.radians(-30)  # -30° around Y
        
        # Rotation matrix around Z axis (yaw)
        Rz = np.array([
            [np.cos(theta_z), -np.sin(theta_z), 0, 0],
            [np.sin(theta_z), np.cos(theta_z), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        # Rotation matrix around Y axis (pitch)
        Ry = np.array([
            [np.cos(theta_y), 0, np.sin(theta_y), 0],
            [0, 1, 0, 0],
            [-np.sin(theta_y), 0, np.cos(theta_y), 0],
            [0, 0, 0, 1]
        ])
        
        # Translation matrix (camera position relative to robot base)
        T = np.array([
            [1, 0, 0, 270],  # 270mm in +X
            [0, 1, 0, 0],    # 0mm in Y
            [0, 0, 1, 460],  # 460mm in +Z
            [0, 0, 0, 1]
        ])
        
        # Combined transformation matrix (translation * rotation_z * rotation_y)
        # Order: First rotate around Y, then Z, then translate
        H = T @ Rz @ Ry
        
        # Invert the transformation to get camera-to-robot transform
        H_inv = np.linalg.inv(H)
        
        # Convert camera coordinates to homogeneous coordinates
        camera_point = np.array([*camera_pos, 1])
        
        # Transform to robot coordinates
        robot_point = H_inv @ camera_point
        
        # Return just the position components (x,y,z)
        return tuple(robot_point[:3])

    async def execute_command_sequence(self, commands: List[str]) -> bool:
        """
        Execute a sequence of natural language commands.
        
        Args:
            commands: List of natural language command strings
            
        Returns:
            bool: True if all commands executed successfully
        """
        for command in commands:
            logger.info(f"Executing command: {command}")
            success = await self.process_command(command)
            if not success:
                logger.error(f"Failed to execute command: {command}")
                return False
        return True

    async def process_command(self, command: str) -> bool:
        """
        Process a single natural language command.
        
        Args:
            command: Natural language command string
            
        Returns:
            bool: True if command executed successfully
        """
        command = command.lower()
        
        try:
            if "pick up" in command or "grab" in command:
                object_name = self._extract_object_name(command)
                return await self.pick_up_object(object_name)
                
            elif "drop" in command or "put" in command:
                object_name = self._extract_object_name(command)
                target_location = self._extract_target_location(command)
                if not target_location:
                    logger.error("No target location specified for drop command")
                    return False
                return await self.drop_object(target_location)
                
            elif "move" in command:
                object_name = self._extract_object_name(command)
                target_location = self._extract_target_location(command)
                if not target_location:
                    # Simple move to object
                    return await self.move_to_object(object_name)
                else:
                    # Move object to location
                    return await self.move_object_to_location(object_name, target_location)
            
            else:
                logger.warning(f"Unknown command format: {command}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return False

    async def move_to_object(self, target_label: str, height_offset: float = 0) -> bool:
        """Move the robot to an object with optional height offset."""
        try:
            target_obj = self.perception.find_object(target_label)
            if not target_obj:
                logger.warning(f"Could not find object: {target_label}")
                return False
            
            camera_pos = target_obj['position']
            robot_pos = self._convert_camera_to_robot_frame(camera_pos)
            
            # Move to position above object first
            approach_pos = (robot_pos[0], robot_pos[1], self.safe_height)
            result = self.robot.move_to_position(
                x=approach_pos[0],
                y=approach_pos[1],
                z=approach_pos[2],
                roll=180,
                pitch=0,
                yaw=0,
                speed=self.default_speed,
                wait=True
            )
            
            if result != 0:
                return False
            
            # Move to final position
            final_z = robot_pos[2] + height_offset
            result = self.robot.move_to_position(
                x=robot_pos[0],
                y=robot_pos[1],
                z=final_z,
                roll=180,
                pitch=0,
                yaw=0,
                speed=self.approach_speed,
                wait=True
            )
            
            return result == 0
            
        except Exception as e:
            logger.error(f"Error in move_to_object: {str(e)}")
            return False

    async def pick_up_object(self, target_label: str) -> bool:
        """Pick up an object."""
        try:
            # Move to grip position
            if not await self.move_to_object(target_label, height_offset=self.grip_height):
                return False
            
            # Close gripper
            # self.robot.gripper.close()
            # await asyncio.sleep(0.5)  # Wait for gripper to close
            
            # Store held object
            self.held_object = target_label
            
            # Lift object to safe height
            result = self.robot.move_to_position(
                z=self.safe_height,
                speed=self.default_speed,
                wait=True
            )
            
            return result == 0
            
        except Exception as e:
            logger.error(f"Error in pick_up_object: {str(e)}")
            return False

    async def drop_object(self, target_location: str) -> bool:
        """Drop currently held object at specified location."""
        try:
            if not self.held_object:
                logger.error("No object currently held")
                return False
            
            # Move to drop position
            if not await self.move_to_object(target_location, height_offset=self.drop_height):
                return False
            
            # Open gripper
            # self.robot.gripper.open()
            # await asyncio.sleep(0.5)  # Wait for gripper to open
            
            # Clear held object
            self.held_object = None
            
            # Move back to safe height
            result = self.robot.move_to_position(
                z=self.safe_height,
                speed=self.default_speed,
                wait=True
            )
            
            return result == 0
            
        except Exception as e:
            logger.error(f"Error in drop_object: {str(e)}")
            return False

    async def move_object_to_location(self, object_name: str, target_location: str) -> bool:
        """Move an object to a target location."""
        if not await self.pick_up_object(object_name):
            return False
        
        if not await self.drop_object(target_location):
            return False
            
        return True

    def stop(self):
        """Cleanup and stop all components."""
        self.perception.stop()
        self.robot.disconnect()
        logger.info("RobotCommander stopped successfully")


if __name__ == "__main__":
    import asyncio
    
    async def main():
        commander = RobotCommander(
            robot_ip="192.168.1.197",
            enable_visualization=True  # Enables camera visualization
        )
        
        try:
            # Get initial scene perception
            objects = commander.perception.get_scene_objects()
            print(f"Detected objects:")
            for obj in objects:
                print(f"- {obj['label']} at position {obj['position']}")

            # Example command sequence
            commands = [
                "move book"
            ]
            
            success = await commander.execute_command_sequence(commands)
            print(f"Command sequence {'succeeded' if success else 'failed'}")
            
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            commander.stop()
    
    # Run the async main function
    asyncio.run(main())