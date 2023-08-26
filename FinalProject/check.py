import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Now you can access the environment variables from settings.py
cloudinary_cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
cloudinary_api_key = os.environ.get('CLOUDINARY_API_KEY')
cloudinary_api_secret = os.environ.get('CLOUDINARY_API_SECRET')

print("Cloudinary Cloud Name:", cloudinary_cloud_name)
print("Cloudinary API Key:", cloudinary_api_key)
print("Cloudinary API Secret:", cloudinary_api_secret)
