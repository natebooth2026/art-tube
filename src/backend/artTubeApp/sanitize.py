from uuid import uuid4
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from cryptography.fernet import Fernet

fernet = Fernet(settings.FILE_CRYPT_KEY)

def sanitize_img(img_file):
    FORMAT_MAP = {
        'JPEG': 'jpg',
        'PNG': 'png',
        'WEBP': 'webp'
    }

    with Image.open(img_file) as img:
        orig_form = img.format

        if orig_form not in FORMAT_MAP:
            raise ValueError(f"Unsupported format: {orig_form}")

        ext = FORMAT_MAP[orig_form]

        if orig_form == 'JPEG':
            if img.mode in ('RGBA', 'LA' 'P'):
                img = img.convert('RGB')
            else:
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGBA')

        ostream = BytesIO()
        img.save(ostream, format=orig_form, optimize=True)
        ostream.seek(0)

        clean_name = f"{uuid4()}.{ext}"
        return ContentFile(fernet.encrypt(ostream.read()), name=clean_name), ext