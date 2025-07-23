# Video to WebP Converter 🎬✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful and flexible Python tool to convert video files (WebM, MP4, GIF, MOV, etc.) into high-quality animated WebP format.

The primary goal of this project is to provide a simple way to convert video animations while intelligently preserving the original timing and duration, so your animations don't look sped up or slowed down. It's perfect for developers, content creators, or anyone who wants to use video animations in web projects with smaller file sizes.

## 🚀 Features

- **😋 Easy Conversion**: Convert video to animated WebP with a single command or function call.
- **🎥 Multi-Format Support**: Convert WebM, MP4, GIF, and other common video formats.
- **🧠 Smart Timing Preservation**: Automatically adjusts FPS to match the original video's duration. This is the default and recommended mode!
- **⚙️ Manual Control**: Option to disable automatic timing and set a manual FPS for full control.
- **🎨 Customizable Output**: Easily specify output resolution (`width`, `height`) and `quality`.
- **💻 Dual Usage Mode**: Can be used as a command-line tool or imported as a module into your own Python projects.
- **✌️ Two Flavors**:
    1. `video_to_webp.py`: **Performance-focused** version that limits animations to 30 frames to prevent high resource usage. Ideal for most videos.
    2. `video_to_webp_no_frame_limits.py`: **Power-user** version that removes the 30-frame limit for extra-long videos. Use with caution!

---

## 🔧 Setup & Installation

Before you can use the converter, you'll need to set up your environment.


### 1. Clone the Repository

Get the project files by cloning the repository:
```bash
git clone https://github.com/not-right-now/video_to_webp.git
cd video_to_webp
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

This is the quickest way to convert a single file. The arguments are the same for both `video_to_webp.py` and `video_to_webp_no_frame_limits.py`.

**Basic Usage:**
```bash
python video_to_webp.py path/to/your/input.mp4 path/to/your/output.webp
```

**Command-Line Arguments:**

| Argument              | Description                                                                                             | Default    |
| --------------------- | ------------------------------------------------------------------------------------------------------- | ---------- |
| `input_file`          | (Required) Path to the input video file.                                                                  | -          |
| `output_file`         | (Required) Path for the output WebP file.                                                               | -          |
| `--width`             | Output width in pixels.                                                                                 | `Original` |
| `--height`            | Output height in pixels.                                                                                | `Original` |
| `--quality`           | WebP quality (0-100). Higher is better.                                                                 | `80`       |
| `--fps`               | Frames per second. **Ignored by default** unless you use the `--no-preserve-timing` flag.               | `30`       |
| `--no-preserve-timing`| A flag to disable automatic timing preservation and use the manual `--fps` value instead.                 | `False`    |

**Example with custom settings:**
```bash
python video_to_webp.py "demo_inp/animation.webm" "demo_out/custom.webp" --width 400 --height 400 --quality 95
```

### As a Python Module

Import the converter into your project for more programmatic control.

**Simple Usage (Recommended):**
The `convert_video_to_webp` function is a simple one-liner.
```python
from video_to_webp import convert_video_to_webp

success = convert_video_to_webp('input.mp4', 'output.webp', quality=90)

if success:
    print("🎉 Conversion successful!")
else:
    print("😢 Conversion failed.")
```

**Advanced Usage (Class-based):**
For more complex scenarios, you can use the `VideoToWebPConverter` class. This is useful if you want to convert multiple files with the same settings.
```python
from video_to_webp import VideoToWebPConverter

# Configure the converter once
converter = VideoToWebPConverter(
    width=512,
    height=384,
    quality=85,
    preserve_timing=True # This is the default
)

# Reuse it for multiple files
converter.convert('video1.mp4', 'output1.webp')
converter.convert('video2.webm', 'output2.webp')
```

---

## ⚠️ The "No Frame Limits" Version

For videos that are longer than 30 frames, the standard `video_to_webp.py` will cap the output at 30 frames to save memory and CPU time. If you absolutely need to render every single frame of a long video, you can use `video_to_webp_no_frame_limits.py`.

**🚨 Warning:** Converting videos with a very high frame count can be resource-intensive and may consume a lot of RAM and CPU. Use this version wisely!

To use it, simply change your import statement:

```python
# Instead of from video_to_webp import ...
from video_to_webp_no_frame_limits import convert_video_to_webp, VideoToWebPConverter

# The rest of your code remains the same!
success = convert_video_to_webp('long_video.mp4', 'long_output.webp')
```

---

## 🎬 Running the Demo

A comprehensive demo script (`demo.py`) is included to showcase all the features.

1.  **Add video files**: Place your video files in the `demo_inp/` directory to get started. The demo includes sample files, or you can add your own!

2.  **Run the script**:
    ```bash
    python demo.py
    ```
    > **Note:** The demo script will first clear the `demo_out/` directory to ensure a fresh start for each run.

3.  **Check the results**: The script will run through various conversion scenarios and place all the output `.webp` files in the `demo_out/` directory for you to inspect.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
