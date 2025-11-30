"""
Text Label Node for ComfyUI
Adds customizable text labels to images with transparent backgrounds and alignment options.
"""

import os
import platform
from typing import Tuple, List

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont


# Define filenames for custom fonts (relative to 'fonts' directory)
CUSTOM_FONTS = {
    "Funnel Sans": [
        "Funnel_Sans/static/FunnelSans-Regular.ttf",
        "FunnelSans-Regular.ttf"
    ],
    "Funnel Sans Bold": [
        "Funnel_Sans/static/FunnelSans-Bold.ttf",
        "FunnelSans-Bold.ttf"
    ],
    "Google Sans Code": [
        "Google_Sans_Code/static/GoogleSansCode-Regular.ttf",
        "GoogleSansCode-Regular.ttf"
    ],
    "Google Sans Code Bold": [
        "Google_Sans_Code/static/GoogleSansCode-Bold.ttf",
        "GoogleSansCode-Bold.ttf"
    ],
    "Arial": ["arial.ttf", "Arial.ttf"],
    "Arial Bold": ["arialbd.ttf", "Arialbd.ttf", "Arial Bold.ttf"],
    "Monospace": ["consola.ttf", "Consola.ttf", "DejaVuSansMono.ttf"],
}


# Define system fallback paths
SYSTEM_FONTS = {
    "Arial": [
        "C:\\Windows\\Fonts\\arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"
    ],
    "Arial Bold": [
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf"
    ],
    "Monospace": [
        "C:\\Windows\\Fonts\\consola.ttf",
        "/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    ],
}


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> Tuple[int, int, int, int]:
    """Convert hex color string to RGBA tuple."""
    hex_color = hex_color.strip().lstrip("#")
    
    if len(hex_color) == 3:
        r, g, b = [int(c * 2, 16) for c in hex_color]
    elif len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
    else:
        r, g, b = 255, 255, 255
    
    alpha_value = max(0, min(255, int(alpha * 255)))
    return (r, g, b, alpha_value)


def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
    """Convert PyTorch tensor to PIL Image."""
    array = (tensor.clamp(0, 1).cpu().numpy() * 255.0).round().astype(np.uint8)
    return Image.fromarray(array)


def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    """Convert PIL Image to PyTorch tensor."""
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0)


def get_font_paths(font_family: str) -> List[str]:
    """Get list of possible font file paths for the given font family."""
    paths = []
    
    if font_family in CUSTOM_FONTS:
        filenames = CUSTOM_FONTS[font_family]
        # Add local fonts directory
        local_fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
        for fname in filenames:
            paths.append(fname)  # Try direct filename (system/CWD)
            paths.append(os.path.join(local_fonts_dir, fname)) # Try local folder

    if font_family in SYSTEM_FONTS:
        paths.extend(SYSTEM_FONTS[font_family])
    
    # Add user font directories on Linux
    if platform.system().lower() == "linux":
        home = os.path.expanduser("~")
        paths += [
            os.path.join(home, ".fonts", "DejaVuSansMono.ttf"),
            os.path.join(home, ".local", "share", "fonts", "DejaVuSansMono.ttf")
        ]
    
    return paths


def load_font(font_family: str, font_size: int):
    """Load font from system or return default font."""
    for font_path in get_font_paths(font_family):
        try:
            return ImageFont.truetype(font_path, font_size)
        except Exception:
            continue
    
    return ImageFont.load_default()


def get_text_bbox(draw: ImageDraw.ImageDraw, text: str, font) -> Tuple[int, int, int, int]:
    """Get bounding box of text."""
    try:
        return draw.textbbox((0, 0), text, font=font)
    except Exception:
        width = int(draw.textlength(text, font=font))
        height = int(font.size)
        return (0, 0, width, height)


def calculate_position(
    image_width: int,
    image_height: int,
    box_width: int,
    box_height: int,
    placement: str,
    edge_offset: int
) -> Tuple[int, int]:
    """Calculate x, y coordinates for label placement."""
    positions = {
        "top_left": (edge_offset, edge_offset),
        "top_right": (image_width - box_width - edge_offset, edge_offset),
        "bottom_left": (edge_offset, image_height - box_height - edge_offset),
        "bottom_right": (image_width - box_width - edge_offset, image_height - box_height - edge_offset),
        "center": ((image_width - box_width) // 2, (image_height - box_height) // 2)
    }
    
    x, y = positions.get(placement, positions["center"])
    return int(x), int(y)


class TextLabel:
    """ComfyUI node for adding text labels to images."""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "text": ("STRING", {"default": "YOUR TEXT", "multiline": True}),
            },
            "optional": {
                "font_family": (
                    [
                        "Arial", "Arial Bold", "Monospace",
                        "Funnel Sans", "Funnel Sans Bold",
                        "Google Sans Code", "Google Sans Code Bold"
                    ],
                    {"default": "Google Sans Code Bold"}
                ),
                "font_size": ("INT", {"default": 30, "min": 6, "max": 256, "step": 1}),
                "text_align": (["left", "center", "right"], {"default": "left"}),
                "placement": (
                    ["top_left", "top_right", "bottom_left", "bottom_right", "center"],
                    {"default": "top_left"}
                ),
                "edge_offset": ("INT", {"default": 25, "min": 0, "max": 4096, "step": 1}),
                "color_scheme": (
                    ["white_on_black", "black_on_white"],
                    {"default": "white_on_black"}
                ),
                "padding": ("INT", {"default": 18, "min": 0, "max": 256, "step": 1}),
                "corner_radius": ("INT", {"default": 15, "min": 0, "max": 128, "step": 1}),
                "stroke_width": ("INT", {"default": 1, "min": 0, "max": 20, "step": 1}),
                "background_opacity": ("INT", {"default": 0, "min": 0, "max": 255, "step": 1}),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "add_text_label"
    CATEGORY = "image/annotation"
    
    def add_text_label(
        self,
        image: torch.Tensor,
        text: str,
        font_family: str = "Arial",
        font_size: int = 30,
        text_align: str = "center",
        placement: str = "top_left",
        edge_offset: int = 30,
        color_scheme: str = "black_on_white",
        padding: int = 15,
        corner_radius: int = 15,
        stroke_width: int = 0,
        background_opacity: int = 0,
    ) -> Tuple[torch.Tensor]:
        """Add text label to image(s)."""
        # Ensure image is 4D (batch, height, width, channels)
        if image.dim() == 3:
            image = image.unsqueeze(0)
        
        # Load font
        font = load_font(font_family, font_size)
        
        # Set text and background colors
        if color_scheme == "white_on_black":
            text_color, bg_color = "#FFFFFF", "#000000"
            stroke_color = "#000000"
        else:
            text_color, bg_color = "#000000", "#FFFFFF"
            stroke_color = "#FFFFFF"
        
        # Process each image in batch
        output_images = []
        for i in range(image.shape[0]):
            # Convert to PIL Image
            pil_image = tensor_to_pil(image[i]).convert("RGBA")
            draw = ImageDraw.Draw(pil_image, "RGBA")
            
            # Measure text dimensions
            left, top, right, bottom = get_text_bbox(draw, text, font)
            text_width = right - left
            text_height = bottom - top
            
            # Calculate box dimensions
            box_width = text_width + padding * 2
            box_height = text_height + padding * 2
            
            # Calculate label position
            x, y = calculate_position(
                pil_image.width,
                pil_image.height,
                box_width,
                box_height,
                placement,
                edge_offset
            )
            
            # Create overlay for semi-transparent background
            overlay = Image.new("RGBA", pil_image.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay, "RGBA")
            
            # Draw rounded rectangle background with 50% opacity
            radius = max(0, min(corner_radius, min(box_width, box_height) // 2))
            overlay_draw.rounded_rectangle(
                [x, y, x + box_width, y + box_height],
                radius=radius,
                fill=hex_to_rgba(bg_color, background_opacity / 255.0)
            )
            
            # Composite the overlay onto the base image
            pil_image = Image.alpha_composite(pil_image, overlay)
            
            # Draw text with full opacity and alignment
            draw = ImageDraw.Draw(pil_image, "RGBA")
            
            # Center text within the box
            center_x = x + box_width / 2.0
            center_y = y + box_height / 2.0
            text_x = int(center_x - text_width / 2.0 - left)
            text_y = int(center_y - text_height / 2.0 - top)
            
            draw.multiline_text(
                (text_x, text_y),
                text,
                font=font,
                fill=hex_to_rgba(text_color, 1.0),
                align=text_align,
                stroke_width=stroke_width,
                stroke_fill=hex_to_rgba(stroke_color, 1.0)
            )
            
            # Convert back to tensor
            output_images.append(pil_to_tensor(pil_image.convert("RGB")))
        
        return (torch.stack(output_images, dim=0),)


NODE_CLASS_MAPPINGS = {"TextLabel": TextLabel}
NODE_DISPLAY_NAME_MAPPINGS = {"TextLabel": "Text Label (SEB)"}
