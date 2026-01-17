"""
S3 DAO - Data Access Object for AWS S3 operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError

from config import settings
from utils.aws_utils import get_s3_client, check_s3_bucket_exists, create_s3_bucket
from utils.text_utils import sanitize_filename, format_file_size, is_supported_file
from common.exceptions import S3ConnectionException, TranscriptNotFoundException, ValidationException

logger = logging.getLogger(__name__)


class S3DAO:
    """Data Access Object for S3 transcript storage."""
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        transcript_folder: Optional[str] = None,
        archive_folder: Optional[str] = None
    ):
        """
        Initialize S3 DAO.
        
        Args:
            bucket_name: S3 bucket name (defaults to settings)
            transcript_folder: Folder for transcripts (defaults to settings)
            archive_folder: Folder for archived transcripts (defaults to settings)
        """
        self.bucket_name = bucket_name or settings.S3_BUCKET_NAME
        self.transcript_folder = transcript_folder or settings.S3_TRANSCRIPT_FOLDER
        self.archive_folder = archive_folder or settings.S3_ARCHIVE_FOLDER
        self._client = None
    
    @property
    def client(self):
        """Lazy-load S3 client."""
        if self._client is None:
            self._client = get_s3_client()
        return self._client
    
    def _get_transcript_key(self, filename: str) -> str:
        """Get full S3 key for transcript file."""
        safe_filename = sanitize_filename(filename)
        return f"{self.transcript_folder}/{safe_filename}"
    
    def _get_archive_key(self, filename: str) -> str:
        """Get full S3 key for archived file."""
        safe_filename = sanitize_filename(filename)
        return f"{self.archive_folder}/{safe_filename}"
    
    def ensure_bucket_exists(self) -> bool:
        """
        Ensure S3 bucket exists, create if not.
        
        Returns:
            bool: True if bucket exists or was created
            
        Raises:
            S3ConnectionException: If bucket creation fails
        """
        if not self.bucket_name:
            raise S3ConnectionException("S3 bucket name not configured", bucket=None)
        
        exists, error = check_s3_bucket_exists(self.bucket_name)
        
        if exists:
            return True
        
        # Try to create bucket
        success, error = create_s3_bucket(self.bucket_name)
        if not success:
            raise S3ConnectionException(error, bucket=self.bucket_name)
        
        return True
    
    def upload_transcript(
        self,
        filename: str,
        content: bytes,
        content_type: str = "text/plain",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload transcript to S3.
        
        Args:
            filename: Name of the file
            content: File content as bytes
            content_type: MIME type
            metadata: Optional metadata
            
        Returns:
            Dict with upload details
            
        Raises:
            ValidationException: If file type not supported
            S3ConnectionException: If upload fails
        """
        if not is_supported_file(filename):
            raise ValidationException(
                f"File type not supported. Supported: {', '.join(['.txt', '.srt', '.vtt', '.json'])}",
                field="filename"
            )
        
        key = self._get_transcript_key(filename)
        
        # Prepare metadata
        upload_metadata = {
            "uploaded_at": datetime.utcnow().isoformat(),
            "original_filename": filename,
            "indexed": "false"
        }
        if metadata:
            upload_metadata.update(metadata)
        
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType=content_type,
                Metadata=upload_metadata
            )
            
            logger.info(f"Uploaded transcript: {key}")
            
            return {
                "filename": filename,
                "key": key,
                "bucket": self.bucket_name,
                "size": len(content),
                "size_formatted": format_file_size(len(content)),
                "uploaded_at": upload_metadata["uploaded_at"]
            }
        
        except ClientError as e:
            error_msg = f"Failed to upload transcript: {e.response['Error']['Message']}"
            logger.error(error_msg)
            raise S3ConnectionException(error_msg, bucket=self.bucket_name)
    
    def download_transcript(self, filename: str) -> Dict[str, Any]:
        """
        Download transcript from S3.
        
        Args:
            filename: Name of the file
            
        Returns:
            Dict with content and metadata
            
        Raises:
            TranscriptNotFoundException: If file not found
            S3ConnectionException: If download fails
        """
        key = self._get_transcript_key(filename)
        
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            content = response['Body'].read()
            
            return {
                "filename": filename,
                "key": key,
                "content": content.decode('utf-8'),
                "content_type": response.get('ContentType', 'text/plain'),
                "size": response['ContentLength'],
                "size_formatted": format_file_size(response['ContentLength']),
                "metadata": response.get('Metadata', {}),
                "last_modified": response['LastModified'].isoformat()
            }
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise TranscriptNotFoundException(filename)
            error_msg = f"Failed to download transcript: {e.response['Error']['Message']}"
            logger.error(error_msg)
            raise S3ConnectionException(error_msg, bucket=self.bucket_name)
    
    def delete_transcript(self, filename: str) -> bool:
        """
        Delete transcript from S3.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if deleted
            
        Raises:
            S3ConnectionException: If delete fails
        """
        key = self._get_transcript_key(filename)
        
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            logger.info(f"Deleted transcript: {key}")
            return True
        
        except ClientError as e:
            error_msg = f"Failed to delete transcript: {e.response['Error']['Message']}"
            logger.error(error_msg)
            raise S3ConnectionException(error_msg, bucket=self.bucket_name)
    
    def list_transcripts(self) -> List[Dict[str, Any]]:
        """
        List all transcripts in S3.
        
        Returns:
            List of transcript details
            
        Raises:
            S3ConnectionException: If list fails
        """
        prefix = f"{self.transcript_folder}/"
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            transcripts = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                filename = key.replace(prefix, '')
                
                # Skip folder marker
                if not filename:
                    continue
                
                # Get metadata
                try:
                    head = self.client.head_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
                    metadata = head.get('Metadata', {})
                except:
                    metadata = {}
                
                transcripts.append({
                    "filename": filename,
                    "key": key,
                    "size": obj['Size'],
                    "size_formatted": format_file_size(obj['Size']),
                    "last_modified": obj['LastModified'].isoformat(),
                    "indexed": metadata.get('indexed', 'false') == 'true',
                    "metadata": metadata
                })
            
            return transcripts
        
        except ClientError as e:
            error_msg = f"Failed to list transcripts: {e.response['Error']['Message']}"
            logger.error(error_msg)
            raise S3ConnectionException(error_msg, bucket=self.bucket_name)
    
    def transcript_exists(self, filename: str) -> bool:
        """
        Check if transcript exists.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if exists
        """
        key = self._get_transcript_key(filename)
        
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except ClientError:
            return False
    
    def update_metadata(self, filename: str, metadata: Dict[str, str]) -> bool:
        """
        Update transcript metadata.
        
        Args:
            filename: Name of the file
            metadata: Metadata to update
            
        Returns:
            bool: True if updated
        """
        key = self._get_transcript_key(filename)
        
        try:
            # Get current object
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            current_metadata = response.get('Metadata', {})
            current_metadata.update(metadata)
            
            # Copy object to itself with new metadata
            self.client.copy_object(
                Bucket=self.bucket_name,
                Key=key,
                CopySource={'Bucket': self.bucket_name, 'Key': key},
                Metadata=current_metadata,
                MetadataDirective='REPLACE'
            )
            
            logger.info(f"Updated metadata for: {key}")
            return True
        
        except ClientError as e:
            logger.error(f"Failed to update metadata: {e.response['Error']['Message']}")
            return False
    
    def archive_transcript(self, filename: str) -> bool:
        """
        Move transcript to archive folder.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if archived
        """
        source_key = self._get_transcript_key(filename)
        dest_key = self._get_archive_key(filename)
        
        try:
            # Copy to archive
            self.client.copy_object(
                Bucket=self.bucket_name,
                Key=dest_key,
                CopySource={'Bucket': self.bucket_name, 'Key': source_key}
            )
            
            # Delete original
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=source_key
            )
            
            logger.info(f"Archived transcript: {filename}")
            return True
        
        except ClientError as e:
            logger.error(f"Failed to archive transcript: {e.response['Error']['Message']}")
            return False