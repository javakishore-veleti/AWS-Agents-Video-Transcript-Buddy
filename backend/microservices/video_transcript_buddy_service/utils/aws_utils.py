"""
AWS Utilities - Helper functions for AWS operations.
"""

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, Tuple
import logging

from config import settings
from common.exceptions import S3ConnectionException, ConfigurationException

logger = logging.getLogger(__name__)


def get_aws_session() -> boto3.Session:
    """
    Create and return an AWS session.
    
    Uses credentials from:
    1. Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    2. Settings configuration
    3. AWS profile if specified
    
    Returns:
        boto3.Session: Configured AWS session
        
    Raises:
        ConfigurationException: If credentials are not configured
    """
    try:
        # If profile is specified, use it
        if settings.AWS_PROFILE:
            return boto3.Session(
                profile_name=settings.AWS_PROFILE,
                region_name=settings.AWS_REGION
            )
        
        # Use explicit credentials if provided
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            return boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        
        # Fall back to default credential chain
        return boto3.Session(region_name=settings.AWS_REGION)
    
    except Exception as e:
        logger.error(f"Failed to create AWS session: {e}")
        raise ConfigurationException(
            message="Failed to create AWS session. Check your credentials.",
            config_key="AWS_CREDENTIALS"
        )


def get_s3_client():
    """
    Get S3 client with retry configuration.
    
    Returns:
        boto3.client: Configured S3 client
    """
    session = get_aws_session()
    
    config = Config(
        retries={
            'max_attempts': 3,
            'mode': 'adaptive'
        },
        connect_timeout=5,
        read_timeout=30
    )
    
    return session.client('s3', config=config)


def get_bedrock_client():
    """
    Get Bedrock client for AgentCore operations.
    
    Returns:
        boto3.client: Configured Bedrock client
    """
    session = get_aws_session()
    
    config = Config(
        retries={
            'max_attempts': 3,
            'mode': 'adaptive'
        },
        connect_timeout=5,
        read_timeout=60
    )
    
    return session.client('bedrock-agent-runtime', config=config)


def validate_aws_credentials() -> Tuple[bool, Optional[str]]:
    """
    Validate AWS credentials by making a test API call.
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        session = get_aws_session()
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        
        logger.info(f"AWS credentials valid. Account: {identity['Account']}")
        return True, None
    
    except NoCredentialsError:
        error_msg = "No AWS credentials found"
        logger.error(error_msg)
        return False, error_msg
    
    except ClientError as e:
        error_msg = f"AWS credentials invalid: {e.response['Error']['Message']}"
        logger.error(error_msg)
        return False, error_msg
    
    except Exception as e:
        error_msg = f"Failed to validate AWS credentials: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def check_s3_bucket_exists(bucket_name: str) -> Tuple[bool, Optional[str]]:
    """
    Check if S3 bucket exists and is accessible.
    
    Args:
        bucket_name: Name of the S3 bucket
        
    Returns:
        Tuple[bool, Optional[str]]: (exists, error_message)
    """
    try:
        s3_client = get_s3_client()
        s3_client.head_bucket(Bucket=bucket_name)
        return True, None
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            return False, f"Bucket '{bucket_name}' does not exist"
        elif error_code == '403':
            return False, f"Access denied to bucket '{bucket_name}'"
        else:
            return False, f"Error checking bucket: {e.response['Error']['Message']}"
    
    except Exception as e:
        return False, f"Failed to check bucket: {str(e)}"


def create_s3_bucket(bucket_name: str, region: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Create S3 bucket if it doesn't exist.
    
    Args:
        bucket_name: Name of the S3 bucket
        region: AWS region (defaults to settings.AWS_REGION)
        
    Returns:
        Tuple[bool, Optional[str]]: (success, error_message)
    """
    region = region or settings.AWS_REGION
    
    try:
        s3_client = get_s3_client()
        
        # Check if bucket already exists
        exists, _ = check_s3_bucket_exists(bucket_name)
        if exists:
            logger.info(f"Bucket '{bucket_name}' already exists")
            return True, None
        
        # Create bucket
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        logger.info(f"Created bucket '{bucket_name}' in {region}")
        return True, None
    
    except ClientError as e:
        error_msg = f"Failed to create bucket: {e.response['Error']['Message']}"
        logger.error(error_msg)
        return False, error_msg
    
    except Exception as e:
        error_msg = f"Failed to create bucket: {str(e)}"
        logger.error(error_msg)
        return False, error_msg