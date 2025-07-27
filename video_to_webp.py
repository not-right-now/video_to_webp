"""
Video to WebP Converter Module supports many video formats like WEBM, MP4, GIF, MOV, MKV, etc.

A simple Python module for converting various video formats (WebM, MP4, etc.) to animated WebP.
Features smart timing preservation and performance optimization.
"""

import os
from PIL import Image, ImageDraw
import argparse
import sys
import webp
import time
import av

class VideoToWebPConverter:
    """Converter class for Video to animated WebP conversion with automatic timing preservation."""
    
    def __init__(self, width: int = -1, height: int = -1, fps: float = 30.0, quality: int = 80, preserve_timing: bool = True):
        """
        Initialize the converter.
        
        Args:
            width: Output width in pixels (-1 for original)
            height: Output height in pixels (-1 for original)
            fps: Target frames per second (ignored if preserve_timing=True)
            quality: WebP quality (0-100)
            preserve_timing: If True, automatically adjusts FPS to preserve original video timing
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.quality = quality
        self.preserve_timing = preserve_timing

    @staticmethod
    def _select_indices(total_frames: int, count: int) -> list[int]:
        """
        Selects a specific `count` of frame indices from a total number of frames.
        """
        if count <= 0 or total_frames <= 0:
            return []
        if count == 1:
            return [0]
        if count >= total_frames:
            return list(range(total_frames))

        indices = [int(i * (total_frames - 1) / (count - 1)) for i in range(count)]
        return indices

    def _extract_frames_from_video(self, video_path: str, count: int):
        """
        Decodes all frames from a video file into a list of PIL Images.
        """
        frames = []
        original_duration = 0.0
        try:
            with av.open(video_path) as container:
                if not container.streams.video:
                    raise ValueError("The provided file has no video streams.")
                stream = container.streams.video[0]

                # Calculate total frames using the stream's duration
                original_fps = stream.average_rate or 30.0

                if stream.frames > 0:
                    total_frames = stream.frames
                else:
                    total_frames = int((container.duration / 1_000_000) * original_fps)
                _count = 0
                # Extract frames
                indices_to_extract = set(self._select_indices(total_frames, count))
                for frame in container.decode(stream):
                    # Append frames to the frames list
                    if _count in indices_to_extract:
                        pil_image = frame.to_image()
                        # resize if needed
                        if self.width != -1 and self.height != -1:
                            pil_image = pil_image.resize((self.width, self.height), Image.LANCZOS)
                        frames.append(pil_image)

                    _count += 1
                if not frames:
                    raise ValueError("Video file appears to have no frames.")

                # Calculate video duration 
                if container.duration:
                    original_duration = float(container.duration / av.time_base)
                elif stream.duration and stream.time_base:
                    original_duration = float(stream.duration * stream.time_base)
                
                # Fallback if duration metadata is still missing
                if original_duration == 0:
                    original_duration = total_frames / float(original_fps)
                
                print(f"Video details: {original_duration:.2f}s duration, {stream.width}x{stream.height} resolution.")

        except Exception as e:
            print(e)
            raise ValueError(f"Could not decode video file with PyAV: {video_path}") from e

        return frames, total_frames, original_duration
    
    
    
    def _create_fallback_frame(self, width: int, height: int, frame_num: int, total_frames: int) -> Image.Image:
        """Create a simple fallback frame when video processing fails."""
        img = Image.new('RGB', (width, height), (128, 128, 128))
        draw = ImageDraw.Draw(img)
        
        # Calculate animation progress
        progress = frame_num / max(total_frames - 1, 1)
        
        # Create a simple animated element
        center_x = int(width * (0.2 + 0.6 * progress))
        center_y = int(height * 0.5)
        radius = int(min(width, height) * 0.1)
        
        # Draw a circle
        color = (255, 100, 100)  # Red
        draw.ellipse([center_x - radius, center_y - radius, 
                     center_x + radius, center_y + radius], fill=color)
        
        # Add text
        text = f"Frame {frame_num + 1}/{total_frames}"
        text_bbox = draw.textbbox((0, 0), text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = center_y + radius + 20
        draw.text((text_x, text_y), text, fill=(255, 255, 255))
        
        return img
    
    def convert(self, video_path: str, webp_path: str) -> bool:
        """
        Convert video file to animated WebP.

        Args:
            video_path: Path to input video file
            webp_path: Path to output WebP file

        Returns:
            True if conversion successful, False otherwise

        Raises:
            FileNotFoundError: If the video file doesn't exist
            ValueError: If the video file is invalid
            IOError: If output file cannot be written
        """
        start_time = time.monotonic()

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            # Step 1: Extract only the specific frames we need (maintain cap)
            max_frames = 180
            frames ,original_total_frames, original_duration = self._extract_frames_from_video(video_path,max_frames)
            # Total frames after processing
            total_frames = len(frames)
            if not frames:
                # Create fallback frames if extraction fails
                print("Warning: Using fallback frames due to video processing failure")
                fallback_width = self.width if self.width != -1 else 512
                fallback_height = self.height if self.height != -1 else 512
                frames = [self._create_fallback_frame(fallback_width, fallback_height, i, 10) for i in range(10)]
                output_fps = 10.0 

            else:
                # logging details
                if original_total_frames > max_frames:
                    print(f"Video has {original_total_frames} frames.Limiting video to {max_frames} frames for performance.")
                else:
                    print(f"Preserving all {original_total_frames} frames.")

                # Step 2: Apply timing and frame sampling logic
                if self.preserve_timing:
                    # Adjust FPS to maintain the original duration with the new frame count
                    if original_duration > 0:
                        output_fps = total_frames / original_duration
                    

                else:
                    # If not preserving timing, just cap the frames
                    print(f"Not preserving timing: Using specified FPS of {self.fps}, which will alter the final duration.")
                    output_fps = self.fps
            
            if output_fps <= 0: output_fps = 1 # Avoid zero
            
            # Ensure output directory exists
            output_dir = os.path.dirname(webp_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # Step 3: Save as animated WebP
            webp.save_images(
                frames, 
                webp_path, 
                fps=output_fps, 
                quality=self.quality
            )

            return True

        except Exception as e:
            raise IOError(f"Conversion failed: {e}")
        
        finally:
            end_time = time.monotonic()
            duration = end_time - start_time
            print(f"⌛ Total time taken: {duration:.2f} seconds.")


def convert_video_to_webp(video_path: str, webp_path: str, 
                        width: int = -1, height: int = -1, 
                        fps: float = 30.0, quality: int = 80, preserve_timing: bool = True) -> bool:
    """
    Simple function to convert a video file to animated WebP with automatic timing preservation.
    
    Args:
        video_path: Path to input video file
        webp_path: Path to output WebP file
        width: Output width in pixels (default: Original)
        height: Output height in pixels (default: Original)
        fps: Target frames per second (ignored if preserve_timing=True, default: 30.0)
        quality: WebP quality 0-100 (default: 80)
        preserve_timing: Automatically preserve original video timing (default: True)
        
    Returns:
        True if conversion successful, False otherwise
        
    Example:
        >>> from video_to_webp import convert_video_to_webp
        >>> # Automatic timing preservation (recommended)
        >>> success = convert_video_to_webp('video.mp4', 'video.webp')
        >>> # Manual FPS control
        >>> success = convert_video_to_webp('video.mp4', 'video.webp', fps=20, preserve_timing=False)
    """
    converter = VideoToWebPConverter(width, height, fps, quality, preserve_timing)
    try:
        return converter.convert(video_path, webp_path)
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert video files (WebM, MP4, etc.) to animated WebP.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Required positional arguments
    parser.add_argument("input_file", help="Path to the input video file.")
    parser.add_argument("output_file", help="Path for the output WebP file.")

    # Optional arguments
    parser.add_argument("--width", type=int, default=-1, help="Output width in pixels. Default: Original.")
    parser.add_argument("--height", type=int, default=-1, help="Output height in pixels. Default: Original.")
    parser.add_argument("--quality", type=int, default=80, help="WebP quality (0-100). Default: 80.")
    parser.add_argument("--fps", type=float, default=30.0,
                        help="Frames per second. \n(Note: This is ignored by default unless you disable timing preservation).")

    parser.add_argument("--no-preserve-timing", action="store_false", dest="preserve_timing",
                        help="Disable automatic timing preservation to use the manual FPS value.")

    args = parser.parse_args()

    # Call the main function with the parsed arguments
    success = convert_video_to_webp(
        video_path=args.input_file,
        webp_path=args.output_file,
        width=args.width,
        height=args.height,
        quality=args.quality,
        fps=args.fps,
        preserve_timing=args.preserve_timing
    )

    if success:
        print(f"✅ Successfully converted {args.input_file} to {args.output_file}")
    else:
        print(f"❌ Failed to convert {args.input_file}")
        sys.exit(1)
