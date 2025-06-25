import cloudinary
import cloudinary.uploader
from utils.consts import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)

# Test credentials
print(f"Cloud Name: {CLOUDINARY_CLOUD_NAME}")
print(f"API Key: {CLOUDINARY_API_KEY}")
print(
    f"API Secret: {CLOUDINARY_API_SECRET[:10]}..." if CLOUDINARY_API_SECRET else "None"
)

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)

# Test upload with a simple string
try:
    result = cloudinary.uploader.upload(
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
        folder="test",
        public_id="test_image",
    )
    print(f"Test upload successful: {result}")
except Exception as e:
    print(f"Test upload failed: {str(e)}")
    import traceback

    traceback.print_exc()
