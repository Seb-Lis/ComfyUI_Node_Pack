# Custom Nodes for ComfyUI

A collection of utility nodes for image processing, workflow management, and generation metadata tracking.

## Installation

1. Navigate to your ComfyUI `custom_nodes` directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```
2. Clone this repository (or copy the folder `seb-nodes-comfyui`):
   ```bash
   git clone https://github.com/yourusername/seb-nodes-comfyui.git
   ```
3. Restart ComfyUI.
    *   Connect the outputs of this node (Seed, Steps, etc.) to your actual **KSampler** node.
    *   Connect `text_overlay` and `start_time` to the **Generation Time** node (optional).

### 2. Generation Time (SEB)
**Category:** `sampling/control`

Calculates the total generation time and appends it to your text overlay.

*   **Inputs:**
    *   `image`: The generated image (from VAE Decode).
    *   `text`: The `text_overlay` output from the **KSampler Bridge** node.
    *   `start_time`: The `start_time` output from the **KSampler Bridge** node.
*   **Outputs:**
    *   `image`: Passthrough of the input image.
    *   `text`: Updated text string including "Time: X.XXs".
*   **How to Connect:** Place this after your VAE Decode. Connect the image and the data from the Bridge node.

### 3. Text Label (SEB)
Combines multiple image batches into a single grid layout.

*   **Inputs:** `columns` (grid width), `padding`, and up to 6 optional image inputs (`image_1`...`image_6`).
*   **Outputs:** A single grid image.
*   **Usage:** Useful for comparing results or creating contact sheets.

---

## Example Workflow

1.  **KSampler Bridge** -> (Pass parameters) -> **KSampler** -> **VAE Decode** -> **Generation Time** (Input Image).
2.  **KSampler Bridge** -> (Pass `text_overlay` + `start_time`) -> **Generation Time**.
3.  **Generation Time** -> (Pass `image` + `text`) -> **Text Label**.
4.  **Text Label** -> **Save Image**.
