import cloudinary
import cloudinary.uploader
import cloudinary.api
import uuid
import time
from utils.consts import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)

# Debug: Print credentials (hide sensitive parts)
print(f"Cloudinary config check:")
print(f"  Cloud Name: {CLOUDINARY_CLOUD_NAME}")
print(f"  API Key: {CLOUDINARY_API_KEY[:10] if CLOUDINARY_API_KEY else 'None'}...")
print(f"  API Secret: {'Set' if CLOUDINARY_API_SECRET else 'Missing'}")

# Configure Cloudinary
try:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )
    print("✅ Cloudinary configured successfully")
except Exception as e:
    print(f"❌ Cloudinary configuration error: {e}")


class CloudinaryService:
    """Service for handling Cloudinary image uploads and management"""

    @staticmethod
    def upload_image(file_data, filename: str, folder: str = "ironhack-final-project"):
        """
        Upload image to Cloudinary

        Args:
            file_data: Binary image data
            filename: Original filename
            folder: Cloudinary folder to upload to

        Returns:
            dict: Upload result with success status, URL, and metadata
        """
        try:
            print(f"=== CLOUDINARY UPLOAD START ===")
            print(f"Filename: {filename}")
            print(f"Folder: {folder}")
            print(f"File data type: {type(file_data)}")

            if hasattr(file_data, "__len__"):
                print(f"File data size: {len(file_data)} bytes")

            # Check if file_data is empty
            if not file_data:
                return {"success": False, "error": "File data is empty"}

            # Generate a unique public_id using uuid and timestamp
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
            clean_filename = (
                filename.replace(" ", "_").replace(".", "_") if filename else "image"
            )
            public_id = f"{clean_filename}_{timestamp}_{unique_id}"
            print(f"Generated public_id: {public_id}")

            # Upload image to Cloudinary
            print("Calling cloudinary.uploader.upload...")
            result = cloudinary.uploader.upload(
                file_data,
                folder=folder,
                public_id=public_id,
                resource_type="image",
                quality="auto:good",
                transformation=[
                    {"width": 1200, "height": 1200, "crop": "limit"},
                    {"quality": "auto:good"},
                ],
                use_filename=False,  # Don't use the original filename
                unique_filename=True,
            )

            print(f"=== CLOUDINARY UPLOAD SUCCESS ===")
            print(f"Secure URL: {result.get('secure_url')}")
            print(f"Public ID: {result.get('public_id')}")
            print(f"Format: {result.get('format')}")
            print(f"Bytes: {result.get('bytes')}")

            return {
                "success": True,
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "bytes": result.get("bytes"),
                "created_at": result.get("created_at"),
                "version": result.get("version"),
            }

        except Exception as e:
            print(f"=== CLOUDINARY UPLOAD ERROR ===")
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback

            traceback.print_exc()
            return {"success": False, "error": str(e)}

    @staticmethod
    def delete_image(public_id: str):
        """
        Delete image from Cloudinary

        Args:
            public_id: Cloudinary public ID of the image

        Returns:
            dict: Deletion result
        """
        try:
            print(f"=== CLOUDINARY DELETE ===")
            print(f"Deleting public_id: {public_id}")

            result = cloudinary.uploader.destroy(public_id)
            print(f"Delete result: {result}")
            return result

        except Exception as e:
            print(f"=== CLOUDINARY DELETE ERROR ===")
            print(f"Error: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def get_image_info(public_id: str):
        """
        Get image information from Cloudinary

        Args:
            public_id: Cloudinary public ID of the image

        Returns:
            dict: Image information
        """
        try:
            result = cloudinary.api.resource(public_id)
            return {
                "success": True,
                "public_id": result.get("public_id"),
                "url": result.get("secure_url"),
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "bytes": result.get("bytes"),
                "created_at": result.get("created_at"),
            }
        except Exception as e:
            print(f"Error getting image info: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def list_images(folder: str = "ironhack-final-project", max_results: int = 50):
        """
        List images in a Cloudinary folder

        Args:
            folder: Cloudinary folder name
            max_results: Maximum number of results to return

        Returns:
            dict: List of images
        """
        try:
            result = cloudinary.api.resources(
                type="upload", prefix=folder, max_results=max_results
            )
            return {
                "success": True,
                "images": result.get("resources", []),
                "total_count": result.get("total_count", 0),
            }
        except Exception as e:
            print(f"Error listing images: {str(e)}")
            return {"success": False, "error": str(e)}


# Create service instance
cloudinary_service = CloudinaryService()
