"""
KSampler Control Nodes for ComfyUI
Nodes for managing KSampler parameters and tracking generation time.
"""

import time
from typing import Tuple, Dict, Any

import torch
import comfy.samplers


class KSamplerControl:
    """
    Master Controller for KSampler.
    Captures parameters and start time, formats them for text overlay.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "latent": ("LATENT",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 9, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS,),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
            }
        }
    
    RETURN_TYPES = (
        "STRING",
        "LATENT",
        "INT",
        "INT",
        "FLOAT",
        comfy.samplers.KSampler.SAMPLERS,
        comfy.samplers.KSampler.SCHEDULERS,
        "FLOAT"
    )
    RETURN_NAMES = (
        "text_overlay",
        "latent",
        "seed",
        "steps",
        "cfg",
        "sampler_name",
        "scheduler",
        "start_time"
    )
    
    FUNCTION = "control"
    CATEGORY = "sampling/control"
    
    def control(
        self,
        latent: Dict[str, Any],
        seed: int,
        steps: int,
        cfg: float,
        sampler_name: str,
        scheduler: str
    ) -> Tuple[str, Dict[str, Any], int, int, float, str, str, float]:
        """
        Capture KSampler parameters and format them for display.

        Args:
            latent: The latent image dictionary.
            seed: Random seed used for generation.
            steps: Number of sampling steps.
            cfg: Classifier Free Guidance scale.
            sampler_name: Name of the sampler.
            scheduler: Name of the scheduler.

        Returns:
            Tuple containing text overlay string, passed-through parameters, and start time.
        """
        # Capture start time for generation tracking
        start_time = time.time()
        
        # Extract resolution from latent tensor
        # Latent shape: [batch, channels, height, width]
        latent_samples = latent["samples"]
        latent_height = latent_samples.shape[2]
        latent_width = latent_samples.shape[3]
        
        # Calculate actual image resolution (VAE uses 8x downsampling)
        width = latent_width * 8
        height = latent_height * 8
        
        # Format text overlay
        text = (
            f"Seed: {seed}\n"
            f"Steps: {steps} | CFG: {cfg:.1f}\n"
            f"{sampler_name} | {scheduler}\n"
            f"Resolution: {width}x{height}"
        )
        
        return (text, latent, seed, steps, cfg, sampler_name, scheduler, start_time)


class GenerationTime:
    """
    Appends generation time to text overlay.
    Should be placed AFTER image generation is complete.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "text": ("STRING", {"forceInput": True}),
                "start_time": ("FLOAT", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "text")
    FUNCTION = "append_time"
    CATEGORY = "sampling/control"
    
    def append_time(
        self,
        image: torch.Tensor,
        text: str,
        start_time: float
    ) -> Tuple[torch.Tensor, str]:
        """
        Calculate and append generation time to text.

        Args:
            image: The generated image tensor.
            text: The existing text overlay string.
            start_time: The start time timestamp.

        Returns:
            Tuple containing the image and the updated text string.
        """
        end_time = time.time()
        duration = end_time - start_time
        new_text = f"{text}\nTime: {duration:.2f}s"
        return (image, new_text)


NODE_CLASS_MAPPINGS = {
    "KSamplerControl": KSamplerControl,
    "GenerationTime": GenerationTime,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KSamplerControl": "KSampler Bridge to Text (SEB)",
    "GenerationTime": "Generation Time (SEB)",
}
