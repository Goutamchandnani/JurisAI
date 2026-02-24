"""
Utility functions for file handling and formatting
"""
import os
import shutil

def save_uploaded_file(uploaded_file, save_dir="./data/uploads"):
    """
    Save uploaded file to disk
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    file_path = os.path.join(save_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    return file_path

def format_file_size(size_bytes):
    """
    Format file size to human readable string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
