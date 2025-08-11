"""
Video to WebP Converter Module supports many video formats like WEBM, MP4, GIF, MOV, MKV, etc. (with no frames limit)

A simple Python module for converting various video formats (WebM, MP4, etc.) to animated WebP.
This version removes frame limits for extra-long videos. Use with caution!
"""

import os
from PIL import Image, ImageDraw
import webp
import time
import math
import av

class VideoToWebPConverter:
    """Converter class for video to animated WebP conversion with automatic timing preservation."""
    
    def __init__(self, width: int = -1, height: int = -1, quality: int = 80,
                keep_aspect: bool = True, allow_upscale: bool = True, pad: bool = True,
                fps: float = 30.0, preserve_timing: bool = True):       
        """
        Initialize the converter.
        
        Args:
            width: Output width in pixels
            height: Output height in pixels
            quality: WebP quality (0-100)
            keep_aspect: Preserve original aspect ratio (default True).
            allow_upscale: Allow enlarging smaller sources to meet target (default True).
            pad: When keep_aspect=True, pad with transparent canvas to fill target if True (default).
                If False, use cover+center-crop mode instead.
            fps: Target frames per second (ignored if preserve_timing=True)
            preserve_timing: If True, automatically adjusts FPS to preserve original animation timing
        """
        self.width = width
        self.height = height
        self.quality = quality
        self.keep_aspect = keep_aspect
        self.allow_upscale = allow_upscale
        self.pad = pad
        self.fps = fps
        self.preserve_timing = preserve_timing
    
    def _extract_all_frames_from_video(self, video_path: str):
        """
        Decodes only required frames from a video file into a list of PIL Images.
        """
        frames = []
        original_duration = 0.0
        try:
            with av.open(video_path) as container:
                if not container.streams.video:
                    raise ValueError("The provided file has no video streams.")
                stream = container.streams.video[0]

                original_fps = float(stream.average_rate) if getattr(stream, "average_rate", None) else 30.0

                # Decode all frames but store as av.VideoFrame with timestamps (don't convert to PIL now)
                decoded = []
                for frame in container.decode(stream):
                    # Prefer frame.time (float seconds) if available, else compute from pts & time_base
                    t = None
                    if getattr(frame, "time", None) is not None:
                        t = float(frame.time)
                    elif getattr(frame, "pts", None) is not None and getattr(frame, "time_base", None) is not None:
                        t = float(frame.pts * frame.time_base)
                    decoded.append((t, frame))
                    
                if not decoded:
                    raise ValueError("Video file appears to have no frames.")
                
                precision = False # if you want precision over reliability for calulating video duratio

                total_frames = len(decoded)
                duration_seconds = None
                
                if precision:
                    if getattr(container, "duration", None) not in (None, 0):
                        duration_seconds = float(container.duration) / 1_000_000.0
                    elif getattr(stream, "duration", None) and getattr(stream, "time_base", None):
                        duration_seconds = float(stream.duration * stream.time_base)

                # Calculating duration from actual frame timestamps, as metadata can be unreliable.
                last_frame_time = decoded[-1][0]
                
                # if the last frame's timestamp is valid
                if last_frame_time is not None and last_frame_time > 0.0:
                    # the duration is the timestamp of the last frame.
                    # We add the duration of one more frame to account for the last frame's display time.
                    avg_frame_duration = 1.0 / max(original_fps, 1.0)
                    duration_seconds = last_frame_time + avg_frame_duration
                else:
                    # Fallback: If timestamps are zero or None, estimate duration from frame count and FPS.
                    # This is a last resort for videos with broken time information.
                    print("-> ⚠️ Warning: Could not determine duration from frame timestamps. Falling back to FPS-based estimation.")
                    duration_seconds = total_frames / max(original_fps, 1.0)
                
                # Ensure we have a small, non-zero duration to prevent division-by-zero errors.
                original_duration = max(duration_seconds, 1e-6)

                original_duration = duration_seconds
                # logging
                print(f"Decoded {total_frames} frames; duration ~ {original_duration:.3f}s; avg_fps={original_fps}")

                # Extract frames
                for idx in range(total_frames):
                    # Append frames to the frames list

                    av_frame = decoded[idx][1]
                    pil_image = av_frame.to_image()
                    orig_w, orig_h = pil_image.size
                    target_w = self.width if self.width != -1 else orig_w
                    target_h = self.height if self.height != -1 else orig_h
                    pad_mode = self.pad

                    # ========= resize logic ============== 

                    # if haven't given width and height or given but our image is already of that dimension, we need not to resize
                    if (orig_w, orig_h) == (target_w, target_h):
                        final_img = pil_image.convert("RGBA")
                    
                    else:# nah now we have to resize
                        if self.keep_aspect:
                            if pad_mode:
                                # Fit inside target, then pad (transparent canvas)
                                scale = min(target_w / orig_w, target_h / orig_h)
                            else:
                                # Cover the target, then crop center
                                scale = max(target_w / orig_w, target_h / orig_h)
                            # enforce allow_upscale (if manually set to Flase by user) and then we can only pad as cropping won't meet the asked dimensions
                            if not self.allow_upscale and scale > 1.0:
                                scale = 1.0
                                pad_mode = True
                            if pad_mode:
                                # fit: make sure new dims are <= target (use floor / clamp)
                                new_w = max(1, int(math.floor(orig_w * scale)))
                                new_h = max(1, int(math.floor(orig_h * scale)))
                                # clamp in case of rounding overshoot
                                new_w = min(new_w, target_w)
                                new_h = min(new_h, target_h)
                            else:
                                # cover: make sure new dims are >= target (use ceil / ensure minimum)
                                new_w = max(1, int(math.ceil(orig_w * scale)))
                                new_h = max(1, int(math.ceil(orig_h * scale)))
                                if new_w < target_w:
                                    new_w = target_w
                                if new_h < target_h:
                                    new_h = target_h
                            # scale the image
                            resized = pil_image.resize((new_w, new_h), Image.LANCZOS).convert("RGBA")
                            if pad_mode:
                                # paste centered onto transparent canvas of exact target size
                                canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                                left = (target_w - new_w) // 2
                                top = (target_h - new_h) // 2
                                canvas.paste(resized, (left, top), resized)
                                final_img = canvas
                            else:
                                # crop center from resized image (new_w/new_h >= target)
                                left = (new_w - target_w) // 2
                                top = (new_h - target_h) // 2
                                final_img = resized.crop((left, top, left + target_w, top + target_h))
                        else:
                            # keep_aspect == False: strict stretch to target, but if upscaling disabled, clamp per-dimension
                            desired_w, desired_h = target_w, target_h
                            if not self.allow_upscale:
                                # clamp each dimension separately so we don't upscale any axis
                                desired_w = min(desired_w, orig_w)
                                desired_h = min(desired_h, orig_h)
                                
                            if (desired_w, desired_h) == (orig_w, orig_h):
                                resized = pil_image.convert("RGBA")
                            else:
                                resized = pil_image.resize((desired_w, desired_h), Image.LANCZOS).convert("RGBA")
                            # Ensure final output is exactly target size by centering resized on transparent canvas when needed
                            if desired_w == target_w and desired_h == target_h:
                                final_img = resized
                            else:
                                canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
                                left = (target_w - desired_w) // 2
                                top = (target_h - desired_h) // 2
                                canvas.paste(resized, (left, top), resized)
                                final_img = canvas
                    frames.append(final_img)

                if not frames:
                    raise ValueError("Video file appears to have no frames.")



                
                print(f"Video details: {original_duration:.2f}s duration, {stream.width}x{stream.height} resolution.")

        except Exception as e:
            print(e)
            raise ValueError(f"Could not decode video file with PyAV: {video_path}") from e

        return frames, original_duration
    
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
        """
        start_time = time.monotonic()

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            # Step 1: Extract frames and get video properties 
            print("Rendering all original frames... this might take a moment.")
            frames, original_duration = self._extract_all_frames_from_video(video_path)

            total_frames = len(frames)
            original_fps = total_frames / original_duration

            if not frames:
                # Create fallback frames
                print("Warning: Using fallback frames due to video processing failure")
                fallback_width = self.width if self.width != -1 else 512
                fallback_height = self.height if self.height != -1 else 512
                frames = [self._create_fallback_frame(fallback_width, fallback_height, i, 10) for i in range(10)]
                output_fps = 10.0
            else:
                print(f"Found {total_frames} frames to process.")
                # Step 2: Determine the output FPS based on the mode
                if self.preserve_timing:
                    print(f"Preserving timing: Using original FPS of {original_fps:.2f}")
                    output_fps = original_fps
                else:
                    print(f"Not preserving timing: Using specified FPS of {self.fps}.")
                    output_fps = self.fps

            if output_fps <= 0: output_fps = 1  # Avoid zero

            # Ensure output directory exists
            output_dir = os.path.dirname(webp_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # Step 3: Save as animated WebP using the webp library
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
                       quality: int = 80,
                       keep_aspect: bool = True,
                       allow_upscale: bool = True,
                       pad: bool = True,
                       fps: float = 30.0, 
                       preserve_timing: bool = True) -> bool:
    """
    Simple function to convert a video file to animated WebP with automatic timing preservation.
    
    Args:
        video_path: Path to input video file
        webp_path: Path to output WebP file
        width: Output width in pixels (default: Original)
        height: Output height in pixels (default: Original)
        quality: WebP quality 0-100 (default: 80)
        keep_aspect: Preserve original aspect ratio (default True).
        allow_upscale: Allow enlarging smaller sources to meet target (default True).
        pad: When keep_aspect=True, pad with transparent canvas to fill target if True (default).
            If False, use cover+center-crop mode instead.
        fps: Target frames per second (ignored if preserve_timing=True, default: 30)
        preserve_timing: Automatically preserve original animation timing (default: True)
        
    Returns:
        True if conversion successful, False otherwise       
    """
    converter = VideoToWebPConverter(width, height, quality, keep_aspect, allow_upscale, pad, fps, preserve_timing)
    try:
        return converter.convert(video_path, webp_path)
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False


if __name__ == "__main__":
    import argparse, sys
    parser = argparse.ArgumentParser(
        description="Convert video files (WebM, MP4, etc.) to animated WebP (no frame limits).",
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

    # arguments with a default a boolean flag
    parser.add_argument("--no-keep-aspect", dest="keep_aspect", action="store_false",
                        help="Disable preserving aspect ratio (stretch the image).")
    parser.add_argument("--no-upscale", dest="allow_upscale", action="store_false",
                        help="Disable upscaling (do not enlarge source).")
    parser.add_argument("--crop", dest="pad", action="store_false",
                        help="When keeping aspect, use crop instead of padding.")
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
        keep_aspect=args.keep_aspect,
        allow_upscale=args.allow_upscale,
        pad=args.pad,
        fps=args.fps,
        preserve_timing=args.preserve_timing

    )

    if success:
        print(f"✅ Successfully converted {args.input_file} to {args.output_file}")
    else:
        print(f"❌ Failed to convert {args.input_file}")
        sys.exit(1)

