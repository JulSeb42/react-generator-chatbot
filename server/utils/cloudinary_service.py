import cloudinary
import cloudinary.uploader
import cloudinary.api
import uuid  # Add this import
import time  # Add this import
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
    print("Cloudinary configured successfully")
except Exception as e:
    print(f"Cloudinary configuration error: {e}")


class CloudinaryService:
    @staticmethod
    def upload_image(file_data, filename: str, folder: str = "ui-mockups"):
        """Upload image to Cloudinary"""
        try:
            print(f"=== CLOUDINARY UPLOAD START ===")
            print(f"Filename: {filename}")
            print(f"Folder: {folder}")
            print(f"File data type: {type(file_data)}")
            
            if hasattr(file_data, '__len__'):
                print(f"File data size: {len(file_data)} bytes")
            
            # Check if file_data is empty
            if not file_data:
                return {"success": False, "error": "File data is empty"}

            # Upload image to Cloudinary (let Cloudinary generate the ID)
            print("Calling cloudinary.uploader.upload...")
            result = cloudinary.uploader.upload(
                file_data,
                folder=folder,
                resource_type="image",
                quality="auto:good",
                transformation=[
                    {"width": 1200, "height": 1200, "crop": "limit"},
                    {"quality": "auto:good"},
                ],
                unique_filename=True  # Let Cloudinary ensure uniqueness
            )

            print(f"=== CLOUDINARY UPLOAD SUCCESS ===")
            print(f"Result: {result}")

            return {
                "success": True,
                "url": result.get("secure_url"),
                "public_id": result.get("public_id"),
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "bytes": result.get("bytes"),
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
        """Delete image from Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id)
            print(f"Cloudinary delete result: {result}")
            return result
        except Exception as e:
            print(f"Cloudinary delete error: {str(e)}")
            return {"error": str(e)}


# Create service instance
cloudinary_service = CloudinaryService()
