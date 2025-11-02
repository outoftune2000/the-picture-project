from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from service.storage import save_image_to_original
from service.pixel_versioning import record_pixel_version, reconstruct_pixel_version
from service.versions import matrix_path
from service.index_db import load_index, save_index, _empty_index
from django.conf import settings
from django.conf.urls.static import static

BASE_DIR = Path(__file__).resolve().parents[2]


def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'home.html')


@require_http_methods(["GET", "POST"])
def upload(request: HttpRequest) -> HttpResponse:
    context: Dict[str, str] = {}
    if request.method == 'POST' and request.FILES.get('image') and request.POST.get('collection'):
        collection = request.POST['collection'].strip()
        image_file = request.FILES['image']

        # Originals live at images/original/<collection>.png
        original_path = BASE_DIR / 'images' / 'original' / f'{collection}.png'
        if not original_path.exists():
            # First upload becomes original (v1)
            saved = save_image_to_original(image_file, f'{collection}.png')
            context['saved'] = str(saved)
            context['message'] = 'Original image saved as version 1.'
        else:
            # Subsequent upload: compute next version matrix against original
            # Save uploaded file to a temporary path
            temp_dir = BASE_DIR / 'images' / 'versions' / collection
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_path = temp_dir / 'uploaded_tmp.png'
            with temp_path.open('wb') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

            # Determine next version number from index (fallback to 2 if missing)
            next_version = 2
            try:
                idx = load_index()
                entry = idx.get('images', {}).get(collection)
                if entry and entry.get('versions'):
                    next_version = max(entry['versions']) + 1
            except Exception:
                pass

            try:
                artifacts = record_pixel_version(
                    image_stem=collection,
                    from_version=1,
                    to_version=next_version,
                    original_image_path=original_path,
                    edited_image_path=temp_path,
                )

                context['message'] = f'New version v{next_version} recorded with pixel differences.'
                context['matrix'] = str(artifacts['matrix_path'])
                
                # Debug: check if matrix file exists and get file size (don't load entire matrix)
                if artifacts['matrix_path'].exists():
                    file_size = artifacts['matrix_path'].stat().st_size
                    context['debug_matrix'] = f"Matrix file created: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)"
                else:
                    context['debug_matrix'] = "Matrix file not created!"
                    
            except Exception as e:
                context['error'] = f'Error creating version: {str(e)}'
                import traceback
                context['debug_trace'] = traceback.format_exc()

            # Cleanup temp file
            try:
                temp_path.unlink()
            except Exception:
                pass

        context['collection'] = collection
    return render(request, 'upload.html', context)


@require_http_methods(["GET", "POST"])
def recombine(request: HttpRequest) -> HttpResponse:
    context: Dict[str, str] = {}
    if request.method == 'POST':
        collection = request.POST.get('collection', '').strip()
        to_version = int(request.POST.get('to_version', '2'))
        
        # All matrices are computed from version 1 (original)
        # The from_version field is not used, but kept for compatibility
        from_version = 1

        orig_path = BASE_DIR / 'images' / 'original' / f'{collection}.png'
        m_path = matrix_path(collection, from_version, to_version)
        
        context['debug_orig'] = f"Original path: {orig_path} (exists: {orig_path.exists()})"
        context['debug_matrix'] = f"Matrix path: {m_path} (exists: {m_path.exists()})"
        
        if not orig_path.exists() or not m_path.exists():
            context['error'] = 'Original or matrix not found.'
        else:
            # Debug: show matrix file info (don't load entire matrix for performance)
            file_size = m_path.stat().st_size
            context['debug_matrix_content'] = f"Matrix file: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)"
            
            out = reconstruct_pixel_version(orig_path, m_path)
            output_path = BASE_DIR / 'images' / 'versions' / f'{collection}_v{to_version}.png'
            output_path.parent.mkdir(parents=True, exist_ok=True)
            out.save(output_path)
            context['output'] = str(output_path)
            context['message'] = 'Reconstruction saved.'
            
            # Add image URLs for preview
            context['original_image_url'] = f'/images/original/{collection}.png'
            context['recombined_image_url'] = f'/images/versions/{collection}_v{to_version}.png'
            context['collection'] = collection
            context['to_version'] = to_version
    return render(request, 'recombine.html', context)


@require_http_methods(["GET", "POST"])
def delete_all(request: HttpRequest) -> HttpResponse:
    """Delete all images, matrices, metadata, and reset the database."""
    context: Dict[str, Any] = {}
    
    if request.method == 'POST':
        # Check for confirmation
        confirm = request.POST.get('confirm', '').strip().lower()
        
        if confirm == 'yes':
            deleted_items = {
                'images': [],
                'matrices': [],
                'metadata': [],
                'errors': []
            }
            
            try:
                # Delete all images in images/original/
                original_dir = BASE_DIR / 'images' / 'original'
                if original_dir.exists():
                    for img_file in original_dir.iterdir():
                        if img_file.is_file():
                            try:
                                img_file.unlink()
                                deleted_items['images'].append(str(img_file))
                            except Exception as e:
                                deleted_items['errors'].append(f"Error deleting {img_file}: {e}")
                
                # Delete all images in images/versions/
                versions_dir = BASE_DIR / 'images' / 'versions'
                if versions_dir.exists():
                    for img_file in versions_dir.iterdir():
                        if img_file.is_file():
                            try:
                                img_file.unlink()
                                deleted_items['images'].append(str(img_file))
                            except Exception as e:
                                deleted_items['errors'].append(f"Error deleting {img_file}: {e}")
                    
                    # Remove empty version directories
                    for version_dir in versions_dir.iterdir():
                        if version_dir.is_dir():
                            try:
                                version_dir.rmdir()
                            except Exception:
                                pass  # Directory might not be empty
                
                # Delete all transformations directories and files
                transformations_dir = BASE_DIR / 'transformations'
                if transformations_dir.exists():
                    for image_stem_dir in transformations_dir.iterdir():
                        if image_stem_dir.is_dir():
                            # Delete all files in the directory
                            for file in image_stem_dir.rglob('*'):
                                if file.is_file():
                                    try:
                                        file.unlink()
                                        deleted_items['matrices'].append(str(file))
                                    except Exception as e:
                                        deleted_items['errors'].append(f"Error deleting {file}: {e}")
                            
                            # Delete metrics subdirectories
                            metrics_dir = image_stem_dir / 'metrics'
                            if metrics_dir.exists():
                                for metrics_file in metrics_dir.iterdir():
                                    if metrics_file.is_file():
                                        try:
                                            metrics_file.unlink()
                                            deleted_items['matrices'].append(str(metrics_file))
                                        except Exception as e:
                                            deleted_items['errors'].append(f"Error deleting {metrics_file}: {e}")
                                try:
                                    metrics_dir.rmdir()
                                except Exception:
                                    pass
                            
                            # Remove the image_stem directory
                            try:
                                image_stem_dir.rmdir()
                            except Exception:
                                pass
                    
                    # Remove transformations directory if empty
                    try:
                        transformations_dir.rmdir()
                    except Exception:
                        pass
                
                # Delete all metadata files
                metadata_dir = BASE_DIR / 'images' / 'metadata'
                if metadata_dir.exists():
                    for meta_file in metadata_dir.iterdir():
                        if meta_file.is_file():
                            try:
                                meta_file.unlink()
                                deleted_items['metadata'].append(str(meta_file))
                            except Exception as e:
                                deleted_items['errors'].append(f"Error deleting {meta_file}: {e}")
                
                # Reset the index database
                empty_index = _empty_index()
                save_index(empty_index)
                
                # Clear cache by forcing reload
                import service.index_db
                service.index_db._index_cache = empty_index
                service.index_db._index_cache_dirty = False
                
                context['success'] = True
                context['deleted_items'] = deleted_items
                context['message'] = f"Deleted {len(deleted_items['images'])} images, {len(deleted_items['matrices'])} matrices, and {len(deleted_items['metadata'])} metadata files. Database reset."
                
            except Exception as e:
                context['error'] = f"Error during deletion: {str(e)}"
                import traceback
                context['debug_trace'] = traceback.format_exc()
        else:
            context['error'] = 'Deletion cancelled. Please confirm by typing "yes".'
    else:
        # GET request - show summary before deletion
        try:
            index = load_index()
            image_count = len(index.get('images', {}))
            
            original_dir = BASE_DIR / 'images' / 'original'
            images_count = len(list(original_dir.iterdir())) if original_dir.exists() else 0
            
            versions_dir = BASE_DIR / 'images' / 'versions'
            versions_count = len(list(versions_dir.iterdir())) if versions_dir.exists() else 0
            
            transformations_dir = BASE_DIR / 'transformations'
            matrix_count = 0
            if transformations_dir.exists():
                matrix_count = len(list(transformations_dir.rglob('*.npz'))) + len(list(transformations_dir.rglob('*.json')))
            
            metadata_dir = BASE_DIR / 'images' / 'metadata'
            metadata_count = len(list(metadata_dir.iterdir())) if metadata_dir.exists() else 0
            
            context['summary'] = {
                'image_collections': image_count,
                'original_images': images_count,
                'version_images': versions_count,
                'matrices': matrix_count,
                'metadata_files': metadata_count
            }
        except Exception as e:
            context['error'] = f"Error loading summary: {str(e)}"
    
    return render(request, 'delete.html', context)


