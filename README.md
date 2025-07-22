# WebM to WebP Converter 🎥✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful and flexible Python tool to convert WebM videos into high-quality animated WebP format.

The primary goal of this project is to provide a simple way to convert video animations while intelligently preserving the original timing and duration, so your animations don't look sped up or slowed down. It's perfect for developers, content creators, or anyone who wants to use WebM animations in web projects with smaller file sizes.

## 🚀 Features

- **Easy Conversion**: Convert WebM to animated WebP with a single command or function call.
- **🧠 Smart Timing Preservation**: Automatically adjusts FPS to match the original video's duration. This is the default and recommended mode!
- **⚙️ Manual Control**: Option to disable automatic timing and set a manual FPS for full control.
- **🎨 Customizable Output**: Easily specify output resolution (`width`, `height`) and `quality`.
- **💻 Dual Usage Mode**: Can be used as a command-line tool or imported as a module into your own Python projects.
- **✌️ Two Flavors**:
    1. `webm_to_webp.py`: **Performance-focused** version that limits animations to 60 frames to prevent high resource usage. Ideal for most videos.
    2. `webm_to_webp_no_frame_limits.py`: **Power-user** version that removes the 60-frame limit for extra-long videos. Use with caution!

---

## 🔧 Setup & Installation

Before you can use the converter, you'll need to set up your environment.


### 1. Clone the Repository

Get the project files by cloning the repository:
```bash
git clone https://github.com/your-username/webm_to_webp.git
cd webm_to_webp
```

### 2. Install Python Packages

Install the required Python libraries using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```
---

## 💡 How to Use

You can use this tool directly from your terminal or import it into your Python scripts.

### As a Command-Line Tool

This is the quickest way to convert a single file. The arguments are the same for both `webm_to_webp.py` and `webm_to_webp_no_frame_limits.py`.

**Basic Usage:**
```bash
python webm_to_webp.py path/to/your/video.webm path/to/your/output.webp
```

**Command-Line Arguments:**

| Argument              | Description                                                                                             | Default    |
| --------------------- | ------------------------------------------------------------------------------------------------------- | ---------- |
| `input_file`          | (Required) Path to the input WebM file.                                                                  | -          |
| `output_file`         | (Required) Path for the output WebP file.                                                               | -          |
| `--width`             | Output width in pixels.                                                                                 | `Original` |
| `--height`            | Output height in pixels.                                                                                | `Original` |
| `--quality`           | WebP quality (0-100). Higher is better.                                                                 | `80`       |
| `--fps`               | Frames per second. **Ignored by default** unless you use the `--no-preserve-timing` flag.               | `30`       |
| `--no-preserve-timing`| A flag to disable automatic timing preservation and use the manual `--fps` value instead.                 | `False`    |

**Example with custom settings:**
```bash
python webm_to_webp.py "demo_inp/animation.webm" "demo_out/custom.webp" --width 400 --height 400 --quality 95
```

### As a Python Module

Import the converter into your project for more programmatic control.

**Simple Usage (Recommended):**
The `convert_webm_to_webp` function is a simple one-liner.
```python
from webm_to_webp import convert_webm_to_webp

success = convert_webm_to_webp('input.webm', 'output.webp', quality=90)

if success:
    print("🎉 Conversion successful!")
else:
    print("😢 Conversion failed.")
```

**Advanced Usage (Class-based):**
For more complex scenarios, you can use the `WebMToWebPConverter` class. This is useful if you want to convert multiple files with the same settings.
```python
from webm_to_webp import WebMToWebPConverter

# Configure the converter once
converter = WebMToWebPConverter(
    width=512,
    height=384,
    quality=85,
    preserve_timing=True # This is the default
)

# Reuse it for multiple files
converter.convert('video1.webm', 'output1.webp')
converter.convert('video2.webm', 'output2.webp')
```

---

## ⚠️ The "No Frame Limits" Version

For videos that are longer than 60 frames, the standard `webm_to_webp.py` will cap the output at 60 frames to save memory and CPU time. If you absolutely need to render every single frame of a long video, you can use `webm_to_webp_no_frame_limits.py`.

**🚨 Warning:** Converting videos with a very high frame count can be resource-intensive and may consume a lot of RAM and CPU. Use this version wisely!

To use it, simply change your import statement:

```python
# Instead of from webm_to_webp import ...
from webm_to_webp_no_frame_limits import convert_webm_to_webp, WebMToWebPConverter

# The rest of your code remains the same!
success = convert_webm_to_webp('long_video.webm', 'long_output.webp')
```

---

## 🎬 Running the Demo

A comprehensive demo script (`demo.py`) is included to showcase all the features.

1.  **Add WebM files**: Place your `.webm` files in the `demo_inp/` directory to get started. The demo includes sample files, or you can add your own!

2.  **Run the script**:
    ```bash
    python demo.py
    ```
    > **Note:** The demo script will first clear the `demo_out/` directory to ensure a fresh start for each run.

3.  **Check the results**: The script will run through various conversion scenarios and place all the output `.webp` files in the `demo_out/` directory for you to inspect.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
