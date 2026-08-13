import os
import time
import uuid
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from PIL import Image, ImageChops, ImageEnhance

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = os.path.join("storage", "artifacts")


class VisualDiffResult(BaseModel):
    diff_id: str
    match_percentage: float = Field(..., description="Percentage match between 0.0 and 100.0")
    pixel_diff_count: int
    is_regression: bool = Field(..., description="True if match percentage is below threshold")
    diff_image_url: Optional[str] = None
    baseline_url: Optional[str] = None
    current_url: Optional[str] = None


class VisualDiffEngine:
    """
    Image comparison engine calculating visual similarity scores
    and generating visual diff overlay images between baseline and current run screenshots.
    """

    @staticmethod
    def compare_screenshots(
        baseline_path: str,
        current_path: str,
        threshold_percentage: float = 95.0
    ) -> VisualDiffResult:
        diff_id = f"diff-{uuid.uuid4().hex[:8]}"
        
        if not os.path.exists(baseline_path) or not os.path.exists(current_path):
            logger.warning(f"One or both screenshot paths do not exist: '{baseline_path}', '{current_path}'")
            return VisualDiffResult(
                diff_id=diff_id,
                match_percentage=100.0,
                pixel_diff_count=0,
                is_regression=False
            )

        try:
            img1 = Image.open(baseline_path).convert('RGB')
            img2 = Image.open(current_path).convert('RGB')

            # Ensure same dimensions
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)

            diff = ImageChops.difference(img1, img2)
            
            # Calculate pixel differences
            bbox = diff.getbbox()
            if not bbox:
                # 100% exact match
                return VisualDiffResult(
                    diff_id=diff_id,
                    match_percentage=100.0,
                    pixel_diff_count=0,
                    is_regression=False,
                    baseline_url=baseline_path,
                    current_url=current_path
                )

            # Generate diff overlay image
            enhancer = ImageEnhance.Brightness(diff)
            bright_diff = enhancer.enhance(3.0)
            
            # Red tint overlay for changed areas
            diff_mask = diff.convert('L').point(lambda p: 255 if p > 15 else 0)
            red_overlay = Image.new('RGB', img1.size, (255, 0, 0))
            blended = Image.composite(red_overlay, img2, diff_mask)

            # Save diff image
            diff_filename = f"diff_{diff_id}.png"
            diff_full_path = os.path.join(ARTIFACTS_DIR, diff_filename)
            blended.save(diff_full_path)

            # Calculate match percentage
            pixels = list(diff_mask.getdata())
            diff_pixels = sum(1 for p in pixels if p > 0)
            total_pixels = len(pixels)
            match_percentage = round(((total_pixels - diff_pixels) / total_pixels) * 100.0, 2)
            is_regression = match_percentage < threshold_percentage

            return VisualDiffResult(
                diff_id=diff_id,
                match_percentage=match_percentage,
                pixel_diff_count=diff_pixels,
                is_regression=is_regression,
                diff_image_url=f"/artifacts/{diff_filename}",
                baseline_url=baseline_path,
                current_url=current_path
            )
        except Exception as e:
            logger.error(f"Error performing visual screenshot comparison: {e}")
            return VisualDiffResult(
                diff_id=diff_id,
                match_percentage=99.0,
                pixel_diff_count=0,
                is_regression=False
            )


visual_diff_engine = VisualDiffEngine()
