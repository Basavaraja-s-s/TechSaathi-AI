import boto3
from botocore.exceptions import ClientError
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class S3Service:
    """Service for managing document storage in AWS S3"""
    
    def __init__(self, bucket_name: str, aws_access_key: str, aws_secret_key: str, region: str = "us-east-1"):
        """
        Initialize S3 service with AWS credentials.
        
        Args:
            bucket_name: Name of the S3 bucket
            aws_access_key: AWS access key ID
            aws_secret_key: AWS secret access key
            region: AWS region (default: us-east-1)
        """
        self.bucket_name = bucket_name
        self.region = region
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )
            logger.info(f"S3 service initialized for bucket: {bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    async def upload_file(self, file_bytes: bytes, filename: str, content_type: str = "application/pdf") -> str:
        """
        Upload file to S3 bucket.
        
        Args:
            file_bytes: File content as bytes
            filename: Name to store file under
            content_type: MIME type of file
            
        Returns:
            Public URL of uploaded file
            
        Raises:
            Exception: If upload fails
        """
        try:
            # Upload file to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=file_bytes,
                ContentType=content_type
            )
            
            # Generate public URL
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
            logger.info(f"File uploaded successfully: {filename}")
            return url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                logger.error(f"S3 bucket not found: {self.bucket_name}")
                raise Exception("Storage configuration error. Please contact support.")
            elif error_code == 'AccessDenied':
                logger.error("S3 access denied")
                raise Exception("Storage access error. Please contact support.")
            else:
                logger.error(f"S3 upload error: {e}")
                raise Exception("Failed to store document. Please try again.")
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            raise Exception("Failed to store document. Please try again.")
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the S3 bucket.
        
        Returns:
            List of document metadata dictionaries with keys:
            - filename: str
            - url: str
            - uploaded_at: str (ISO format)
            - size: int (bytes)
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            documents = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    filename = obj['Key']
                    documents.append({
                        'filename': filename,
                        'url': self.get_document_url(filename),
                        'uploaded_at': obj['LastModified'].isoformat(),
                        'size': obj['Size']
                    })
            
            logger.info(f"Listed {len(documents)} documents from S3")
            return documents
            
        except ClientError as e:
            logger.error(f"Failed to list S3 documents: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing documents: {e}")
            return []
    
    def get_document_url(self, filename: str) -> str:
        """
        Get public URL for a specific document.
        
        Args:
            filename: Name of the file in S3
            
        Returns:
            Public URL of the document
        """
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
    
    async def delete_file(self, filename: str) -> bool:
        """
        Delete file from S3 bucket.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if deletion was successful, False otherwise
            
        Raises:
            Exception: If deletion fails
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=filename
            )
            logger.info(f"File deleted successfully: {filename}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {e}")
            raise Exception("Failed to delete document. Please try again.")
        except Exception as e:
            logger.error(f"Unexpected error during S3 deletion: {e}")
            raise Exception("Failed to delete document. Please try again.")
