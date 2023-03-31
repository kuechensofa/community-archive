import os
import subprocess
from io import BytesIO
from django.conf import settings
from django.core.files import File

from PIL import Image
from pdf2image import convert_from_path

IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.tif', '.tiff']
THUMB_SIZE = (400, 400)
PREVIEW_SIZE = (2000, 2000)


def crop_image(image):
    width, height = image.size
    if width == height:
        return image
    offset = int(abs(height-width)/2)
    if width > height:
        image = image.crop([offset, 0, width-offset, height])
    else:
        image = image.crop([0, offset, width, height-offset])
    return image


def generate_thumbnail(model):
    if not hasattr(model, 'file') or not hasattr(model, 'thumbnail'):
        raise AttributeError('Model must have file and thumbnail file attributes.')

    file = model.file
    name, ext = os.path.splitext(file.name)

    if ext == '.pdf':
        images = convert_from_path(os.path.join(settings.MEDIA_ROOT, file.name))
        if images:
            image = images[0]
        else:
            return
    elif ext in IMAGE_EXTS:
        image = Image.open(os.path.join(settings.MEDIA_ROOT, file.name))
    else:
        return

    out_buffer = BytesIO()
    image = crop_image(image)
    image.thumbnail(THUMB_SIZE)
    image.save(out_buffer, 'JPEG')
    model.thumbnail = File(out_buffer, name=f'{name}_thumb.jpg')
    model.save()


def generate_preview(model):
    if not hasattr(model, 'file') or not hasattr(model, 'preview'):
        raise AttributeError('Model must have file and preview attributes')

    # generate video preview
    if model.is_video():
        preview_path = generate_video_preview(model.file.name)
        model.preview = preview_path
        model.save()
    elif model.is_image():
        file = model.file
        name, ext = os.path.splitext(file.name)

        if ext not in IMAGE_EXTS:
            return

        try:
            with Image.open(os.path.join(settings.MEDIA_ROOT, file.name)) as image:
                out_buffer = BytesIO()
                image.thumbnail(PREVIEW_SIZE)
                image.save(out_buffer, 'JPEG')
                model.preview = File(out_buffer, name=f'{name}_preview.jpg')
                model.save()
        except OSError:
            print(f'Creating preview for {file.name} failed')


def generate_video_preview(db_input_path):
    input_name, ext = os.path.splitext(db_input_path)
    db_output_path = input_name + '_preview.mp4'
    input_path = os.path.join(settings.MEDIA_ROOT, db_input_path)
    output_path = os.path.join(settings.MEDIA_ROOT, db_output_path)

    ffmpeg_command = ['ffmpeg', '-i', input_path, '-vf', 'scale=-1:720', '-vcodec', 'libx264',
                      '-profile:v', 'baseline', '-level', '3', output_path]
    subprocess.run(ffmpeg_command, cwd=settings.BASE_DIR)
    return db_output_path
