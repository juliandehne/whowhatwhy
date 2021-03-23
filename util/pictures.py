from PIL import Image


def resize_picture(image):
    img = Image.open(image.path)
    if img.height > 300 or img.width > 300:
        output_size = (300, 300)
        img.thumbnail(output_size)
        img.save(image.path)
    return image

