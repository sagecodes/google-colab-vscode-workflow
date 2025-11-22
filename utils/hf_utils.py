"""
Hugging Face utilities for uploading and downloading files
Works in both Google Colab and local environments
"""

import os
import shutil
import getpass
from dotenv import load_dotenv
from huggingface_hub import HfApi, hf_hub_download

# Load environment variables from .env file
load_dotenv()

def upload_file_to_hf(file_path: str, repo_name: str, path_in_repo: str = None) -> str:
    """
    Upload a file to Hugging Face Hub
    
    Args:
        file_path: Local path to the file to upload
        repo_name: HF repository name (e.g., "username/repo-name")
        path_in_repo: Path in repo (defaults to filename)
        
    Returns:
        Success message with HF URL
    """
    # Check if we're in Colab
    try:
        import google.colab
        IN_COLAB = True
    except ImportError:
        IN_COLAB = False
    
    hf_token = None
    
    if IN_COLAB:
        # In Colab, just ask for input to avoid timeout issues
        print("Running in Google Colab - please enter your HF token:")
        hf_token = getpass.getpass("Hugging Face token: ")
    else:
        # Local environment - try .env file first
        hf_token = os.getenv("HF_TOKEN")
        if hf_token is None:
            print("HF_TOKEN not found in environment variables.")
            hf_token = getpass.getpass("Please enter your Hugging Face token: ")
        else:
            print("Using Hugging Face token from environment.")
    
    if not hf_token or not hf_token.strip():
        return "Error: No HF token provided"

    # Create a new repository (if it doesn't exist)
    api = HfApi()
    api.create_repo(repo_name, token=hf_token, exist_ok=True)

    # Use filename if path_in_repo not specified
    if path_in_repo is None:
        path_in_repo = os.path.basename(file_path)

    # Upload the file to the HF repository
    api.upload_file(
        path_or_fileobj=file_path,
        path_in_repo=path_in_repo,
        repo_id=repo_name,
        commit_message="Upload file",
        token=hf_token
    )
    return f"File uploaded to Hugging Face Hub: {repo_name}/{path_in_repo}"


def download_file_from_hf(repo_id: str, filename: str, local_filename: str = None) -> str:
    """
    Download a file from Hugging Face Hub to local directory
    
    Args:
        repo_id: HF repository ID (e.g., "username/repo-name")
        filename: File to download from the repo
        local_filename: Local filename (defaults to original filename)
        
    Returns:
        Path to the downloaded file
    """
    if local_filename is None:
        local_filename = filename
    
    try:
        # Download to HF cache first
        cached_file = hf_hub_download(repo_id=repo_id, filename=filename)
        print(f"File downloaded to cache: {cached_file}")
        
        # Copy to proper local path
        shutil.copy2(cached_file, local_filename)
        local_path = os.path.abspath(local_filename)
        print(f"File copied to: {local_path}")
        
        return local_path
        
    except Exception as e:
        print(f"Download failed: {e}")
        raise