"""
Image Grid Node for ComfyUI
Arranges multiple image batches into a customizable grid layout.
"""

import math
from typing import Optional, Tuple

import torch
import torch.nn.functional as F


class ImageGrid:
    """ComfyUI node for creating image grids from multiple image batches."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "columns": ("INT", {"default": 2, "min": 0, "max": 100, "step": 1}),
                "padding": ("INT", {"default": 2, "min": 0, "max": 500, "step": 1}),
            },
            "optional": {
                "image_1": ("IMAGE",),
                "image_2": ("IMAGE",),
                "image_3": ("IMAGE",),
                "image_4": ("IMAGE",),
                "image_5": ("IMAGE",),
                "image_6": ("IMAGE",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "create_grid"
    CATEGORY = "image/grid"
    
    def create_grid(
        self,
        columns: int,
        padding: int,
        image_1: Optional[torch.Tensor] = None,
        image_2: Optional[torch.Tensor] = None,
        image_3: Optional[torch.Tensor] = None,
        image_4: Optional[torch.Tensor] = None,
        image_5: Optional[torch.Tensor] = None,
        image_6: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor]:
        """
        Create a grid from multiple image batches.

        Args:
            columns: Number of columns in the grid.
            padding: Padding between images in pixels.
            image_1...image_6: Optional image batches to include in the grid.

        Returns:
            A single tensor containing the grid image.
        """
        # Collect all provided images
        all_images = [
            img for img in [image_1, image_2, image_3, image_4, image_5, image_6]
            if img is not None
        ]
        
        if not all_images:
            return (torch.zeros((1, 512, 512, 3)),)
        
        # Get base dimensions from first image batch
        base_shape = all_images[0].shape
        target_height = base_shape[1]
        target_width = base_shape[2]
        channels = base_shape[3]
        
        # Resize all images to match first image dimensions
        processed_images = []
        for img_batch in all_images:
            if img_batch.shape[1] != target_height or img_batch.shape[2] != target_width:
                # Resize: permute to [B, C, H, W] for interpolation
                img_permuted = img_batch.permute(0, 3, 1, 2)
                img_resized = F.interpolate(
                    img_permuted,
                    size=(target_height, target_width),
                    mode="bilinear",
                    align_corners=False
                )
                # Permute back to [B, H, W, C]
                img_batch = img_resized.permute(0, 2, 3, 1)
            
            processed_images.append(img_batch)
        
        # Concatenate all image batches
        final_images = torch.cat(processed_images, dim=0)
        batch_size = final_images.shape[0]
        
        if batch_size == 0:
            return (torch.zeros((1, target_height, target_width, channels)),)
        
        # Calculate grid dimensions
        if columns > 0:
            cols = columns
            rows = math.ceil(batch_size / cols)
        else:
            # Auto-calculate roughly square grid
            cols = math.ceil(math.sqrt(batch_size))
            rows = math.ceil(batch_size / cols)
        
        # Calculate output dimensions
        grid_height = rows * target_height + (rows - 1) * padding
        grid_width = cols * target_width + (cols - 1) * padding
        
        # Initialize grid with zeros (black background)
        grid = torch.zeros(
            (1, grid_height, grid_width, channels),
            dtype=final_images.dtype,
            device=final_images.device
        )
        
        # Place images in grid
        for idx in range(batch_size):
            row = idx // cols
            col = idx % cols
            
            y_start = row * (target_height + padding)
            y_end = y_start + target_height
            x_start = col * (target_width + padding)
            x_end = x_start + target_width
            
            grid[0, y_start:y_end, x_start:x_end, :] = final_images[idx]
        
        return (grid,)


NODE_CLASS_MAPPINGS = {"ImageGrid": ImageGrid}
NODE_DISPLAY_NAME_MAPPINGS = {"ImageGrid": "Image Grid (SEB)"}
