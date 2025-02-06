import os
import json
import logging
import traceback
from pathlib import Path

import torch
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenVLAServer:
    def __init__(self, model_path: str = "openvla/openvla-7b"):
        """Initialize the OpenVLA model server"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load model and processor
        logger.info("Loading model and processor...")
        self.processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModelForVision2Seq.from_pretrained(
            model_path,
            attn_implementation="flash_attention_2",
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        ).to(self.device)
        logger.info("Model loaded successfully")

    async def predict(self, image, instruction: str):
        """Run prediction on image and instruction"""
        try:
            # Process inputs
            inputs = self.processor(
                text=instruction,
                images=image.convert("RGB"),
                return_tensors="pt"
            ).to(self.device, torch.bfloat16)

            # Run inference
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_length=100)
            
            # Process outputs
            result = self.processor.decode(outputs[0], skip_special_tokens=True)
            return {"prediction": result}
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

def create_app():
    """Create and configure FastAPI app"""
    app = FastAPI()
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update this in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize model
    model = OpenVLAServer()
    
    @app.post("/act")
    async def predict(image: bytes, instruction: str):
        return await model.predict(Image.open(image), instruction)
    
    return app

def main():
    """Main entry point"""
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    # Create and run app
    app = create_app()
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()