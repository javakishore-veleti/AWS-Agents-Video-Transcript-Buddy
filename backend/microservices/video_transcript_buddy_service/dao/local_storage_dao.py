"""
Local Storage DAO - Data Access Object for local file storage operations.
"""

import logging
import os
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from config import settings
from utils.text_utils import sanitize_filename, format_file_size
from common.exceptions import TranscriptNotFoundException, ValidationException

logger = logging.getLogger(__name__)


class LocalStorageDAO:
    """Data Access Object for local transcript storage."""
    
    def __init__(
        self,
        transcript_folder: Optional[str] = None,
        archive_folder: Optional[str] = None
    ):
        """
        Initialize Local Storage DAO.
        
        Args:
            transcript_folder: Folder for transcripts (defaults to settings)
            archive_folder: Folder for archived transcripts (defaults to settings)
        """
        self.transcript_folder = transcript_folder or settings.LOCAL_STORAGE_PATH
        self.archive_folder = archive_folder or settings.LOCAL_ARCHIVE_PATH
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure storage directories exist."""
        Path(self.transcript_folder).mkdir(parents=True, exist_ok=True)
        Path(self.archive_folder).mkdir(parents=True, exist_ok=True)
        logger.info(f"Local storage initialized: {self.transcript_folder}")
    
    def _ensure_user_directory(self, user_id: str):
        """Ensure user-specific directory exists."""
        user_folder = os.path.join(self.transcript_folder, user_id)
        Path(user_folder).mkdir(parents=True, exist_ok=True)
        return user_folder
    
    def _get_transcript_path(self, filename: str, user_id: str) -> str:
        """Get full path for transcript file with user isolation."""
        user_folder = self._ensure_user_directory(user_id)
        safe_filename = sanitize_filename(filename)
        return os.path.join(user_folder, safe_filename)
    
    def _get_archive_path(self, filename: str, user_id: str) -> str:
        """Get full path for archived file with user isolation."""
        safe_filename = sanitize_filename(filename)
        user_archive = os.path.join(self.archive_folder, user_id)
        Path(user_archive).mkdir(parents=True, exist_ok=True)
        return os.path.join(user_archive, safe_filename)
    
    def upload_transcript(
        self,
        filename: str,
        content: bytes,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save a transcript file locally.
        
        Args:
            filename: Name of the file
            content: File content as bytes
            user_id: ID of the user uploading the file
            metadata: Optional metadata dict
            
        Returns:
            Dict with upload details
        """
        try:
            filepath = self._get_transcript_path(filename, user_id)
            
            # Write file
            with open(filepath, 'wb') as f:
                f.write(content)
            
            file_size = len(content)
            
            logger.info(f"Saved transcript locally: {filename} ({format_file_size(file_size)})")
            
            return {
                "filename": filename,
                "filepath": filepath,
                "size": file_size,
                "storage_type": "local",
                "uploaded_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
        except Exception as e:
            logger.error(f"Failed to save transcript {filename}: {e}")
            raise ValidationException(f"Failed to save file: {str(e)}")
    
    def get_transcript(self, filename: str, user_id: str) -> bytes:
        """
        Retrieve a transcript file.
        
        Args:
            filename: Name of the file
            user_id: ID of the user
            
        Returns:
            File content as bytes
        """
        filepath = self._get_transcript_path(filename, user_id)
        
        if not os.path.exists(filepath):
            raise TranscriptNotFoundException(f"Transcript not found: {filename}")
        
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read transcript {filename}: {e}")
            raise TranscriptNotFoundException(f"Failed to read file: {str(e)}")
    
    def delete_transcript(self, filename: str, user_id: str) -> bool:
        """
        Delete a transcript file.
        
        Args:
            filename: Name of the file
            user_id: ID of the user
            
        Returns:
            bool: True if deleted successfully
        """
        filepath = self._get_transcript_path(filename, user_id)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted transcript: {filename}")
                return True
            else:
                logger.warning(f"Transcript not found for deletion: {filename}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete transcript {filename}: {e}")
            return False
    
    def list_transcripts(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all transcript files for a specific user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of file details
        """
        transcripts = []
        
        try:
            user_folder = os.path.join(self.transcript_folder, user_id)
            if not os.path.exists(user_folder):
                return transcripts
            
            for filename in os.listdir(user_folder):
                filepath = os.path.join(user_folder, filename)
                
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    transcripts.append({
                        "filename": filename,
                        "filepath": filepath,
                        "size": stat.st_size,
                        "storage_type": "local",
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            logger.info(f"Found {len(transcripts)} local transcripts")
            return transcripts
            
        except Exception as e:
            logger.error(f"Failed to list transcripts: {e}")
            return []
    
    def archive_transcript(self, filename: str, user_id: str) -> bool:
        """
        Move a transcript to archive folder.
        
        Args:
            filename: Name of the file
            user_id: ID of the user
            
        Returns:
            bool: True if archived successfully
        """
        source_path = self._get_transcript_path(filename, user_id)
        dest_path = self._get_archive_path(filename, user_id)
        
        try:
            if os.path.exists(source_path):
                shutil.move(source_path, dest_path)
                logger.info(f"Archived transcript: {filename}")
                return True
            else:
                logger.warning(f"Transcript not found for archiving: {filename}")
                return False
        except Exception as e:
            logger.error(f"Failed to archive transcript {filename}: {e}")
            return False
    
    def transcript_exists(self, filename: str, user_id: str) -> bool:
        """
        Check if a transcript file exists.
        
        Args:
            filename: Name of the file
            user_id: ID of the user
            
        Returns:
            bool: True if file exists
        """
        filepath = self._get_transcript_path(filename, user_id)
        return os.path.exists(filepath)
    
    def get_file_info(self, filename: str, user_id: str) -> Dict[str, Any]:
        """
        Get information about a transcript file.
        
        Args:
            filename: Name of the file
            user_id: ID of the user
            
        Returns:
            Dict with file information
        """
        filepath = self._get_transcript_path(filename, user_id)
        
        if not os.path.exists(filepath):
            raise TranscriptNotFoundException(f"Transcript not found: {filename}")
        
        stat = os.stat(filepath)
        
        return {
            "filename": filename,
            "filepath": filepath,
            "size": stat.st_size,
            "storage_type": "local",
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
