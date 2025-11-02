from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from service.storage import save_image_to_original, list_original_images
from service.versioning import record_new_version
from service.reconstructor import reconstruct_version
from service.index_db import load_index


def add_image_command(image_path: str, filename: Optional[str] = None) -> None:
    """Add an image to the system."""
    image_file = Path(image_path)
    if not image_file.exists():
        print(f"Error: Image file {image_path} does not exist")
        sys.exit(1)
    
    if filename is None:
        filename = image_file.name
    
    try:
        saved_path = save_image_to_original(image_file, filename)
        print(f"Image added successfully: {saved_path}")
    except Exception as e:
        print(f"Error adding image: {e}")
        sys.exit(1)


def create_version_command(original_path: str, edited_path: str, image_stem: str, from_version: int, to_version: int) -> None:
    """Create a new version from original and edited images."""
    original_file = Path(original_path)
    edited_file = Path(edited_path)
    
    if not original_file.exists():
        print(f"Error: Original image {original_path} does not exist")
        sys.exit(1)
    
    if not edited_file.exists():
        print(f"Error: Edited image {edited_path} does not exist")
        sys.exit(1)
    
    try:
        artifacts = record_new_version(image_stem, from_version, to_version, original_file, edited_file)
        print(f"Version created successfully:")
        print(f"  Matrix: {artifacts['matrix_path']}")
        print(f"  RGB metrics: {artifacts['rgb_metrics_path']}")
        print(f"  Intensity metrics: {artifacts['intensity_metrics_path']}")
    except Exception as e:
        print(f"Error creating version: {e}")
        sys.exit(1)


def list_images_command() -> None:
    """List all images in the system."""
    try:
        images = list_original_images()
        if not images:
            print("No images found")
        else:
            print("Images in system:")
            for img in images:
                print(f"  {img}")
    except Exception as e:
        print(f"Error listing images: {e}")
        sys.exit(1)


def reconstruct_command(image_stem: str, version: int, matrix_path: str, output_path: str) -> None:
    """Reconstruct a version from original image and transformation matrix."""
    try:
        # Find original image
        images = list_original_images()
        original_image = None
        for img in images:
            if Path(img).stem == image_stem:
                original_image = Path("images/original") / img
                break
        
        if original_image is None:
            print(f"Error: Original image for {image_stem} not found")
            sys.exit(1)
        
        # Reconstruct version
        result = reconstruct_version(original_image, matrix_path)
        result.save(output_path)
        print(f"Reconstructed version saved to: {output_path}")
    except Exception as e:
        print(f"Error reconstructing version: {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Image Version Control System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add image command
    add_parser = subparsers.add_parser('add', help='Add an image to the system')
    add_parser.add_argument('image_path', help='Path to the image file')
    add_parser.add_argument('--filename', help='Filename to save as (default: original filename)')
    
    # Create version command
    create_parser = subparsers.add_parser('create-version', help='Create a new version')
    create_parser.add_argument('original_path', help='Path to original image')
    create_parser.add_argument('edited_path', help='Path to edited image')
    create_parser.add_argument('image_stem', help='Image stem (e.g., img_001)')
    create_parser.add_argument('from_version', type=int, help='Source version number')
    create_parser.add_argument('to_version', type=int, help='Target version number')
    
    # List images command
    subparsers.add_parser('list', help='List all images in the system')
    
    # Reconstruct command
    reconstruct_parser = subparsers.add_parser('reconstruct', help='Reconstruct a version')
    reconstruct_parser.add_argument('image_stem', help='Image stem (e.g., img_001)')
    reconstruct_parser.add_argument('version', type=int, help='Version number to reconstruct')
    reconstruct_parser.add_argument('matrix_path', help='Path to transformation matrix JSON file')
    reconstruct_parser.add_argument('output_path', help='Path to save reconstructed image')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        add_image_command(args.image_path, args.filename)
    elif args.command == 'create-version':
        create_version_command(args.original_path, args.edited_path, args.image_stem, args.from_version, args.to_version)
    elif args.command == 'list':
        list_images_command()
    elif args.command == 'reconstruct':
        reconstruct_command(args.image_stem, args.version, args.matrix_path, args.output_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
