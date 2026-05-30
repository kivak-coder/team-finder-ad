import random
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from django.core.files.base import ContentFile
from team_finder.constants import (
    AvatarColor,
    AVATAR_SIZE,
    AVATAR_FONT_RATIO,
    AVATAR_TEXT_COLOR
)


def generate_avatar(name: str) -> ContentFile:
    bg_color = random.choice([color.value for color in AvatarColor])
    img = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), color=bg_color)
    draw = ImageDraw.Draw(img)
    letter = name[0].upper() if name else '?'
    font_size = int(AVATAR_SIZE * AVATAR_FONT_RATIO)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default(size=font_size)
    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (AVATAR_SIZE - text_width) / 2 - bbox[0]
    y = (AVATAR_SIZE - text_height) / 2 - bbox[1]

    draw.text(
        (x, y),
        letter,
        fill=AVATAR_TEXT_COLOR,
        font=font
    )

    stream = BytesIO()
    img.save(stream, format='PNG')
    stream.seek(0)
    return ContentFile(stream.read(), name='avatar.png')
