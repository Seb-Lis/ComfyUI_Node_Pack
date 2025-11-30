"""
SEB Custom Nodes for ComfyUI
Collection of utility nodes for image processing and workflow management.
"""

from .ksampler_control import KSamplerControl, GenerationTime
from .text_label import TextLabel
from .image_grid import ImageGrid


# Node Registration
NODE_CLASS_MAPPINGS = {
    "KSamplerControl": KSamplerControl,
    "GenerationTime": GenerationTime,
    "TextLabel": TextLabel,
    "ImageGrid": ImageGrid,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KSamplerControl": "KSampler Bridge to Text (SEB)",
    "GenerationTime": "Generation Time (SEB)",
    "TextLabel": "Text Label (SEB)",
    "ImageGrid": "Image Grid (SEB)",
}