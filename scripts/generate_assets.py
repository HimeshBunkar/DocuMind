from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "frontend" / "public"


def main() -> None:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    size = 512
    image = Image.new("RGBA", (size, size), "#071013")
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(size):
        ratio = y / size
        color = (
            int(7 + 12 * ratio),
            int(16 + 26 * ratio),
            int(19 + 18 * ratio),
            255,
        )
        draw.line((0, y, size, y), fill=color)

    for offset in range(-120, size, 42):
        draw.line((offset, 0, offset + 220, size), fill=(103, 232, 249, 22), width=2)

    panel = Image.new("RGBA", (320, 390), (255, 255, 255, 0))
    panel_draw = ImageDraw.Draw(panel, "RGBA")
    panel_draw.rounded_rectangle((0, 0, 320, 390), radius=28, fill=(255, 255, 255, 28), outline=(255, 255, 255, 70), width=3)
    for index, width in enumerate([220, 260, 190, 246, 170]):
        y = 88 + index * 45
        panel_draw.rounded_rectangle((44, y, 44 + width, y + 12), radius=6, fill=(237, 247, 248, 92))
    panel_draw.rounded_rectangle((44, 38, 156, 58), radius=10, fill=(94, 234, 212, 160))
    panel = panel.rotate(-7, resample=Image.Resampling.BICUBIC, expand=True)
    image.alpha_composite(panel, (96, 68))

    node_layer = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    node_draw = ImageDraw.Draw(node_layer, "RGBA")
    nodes = [(156, 168), (276, 126), (354, 230), (240, 320), (378, 360), (132, 334)]
    for start, end in zip(nodes, nodes[1:]):
        node_draw.line((*start, *end), fill=(103, 232, 249, 150), width=4)
    for x, y in nodes:
        node_draw.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(103, 232, 249, 210), outline=(255, 255, 255, 150), width=3)

    glow = node_layer.filter(ImageFilter.GaussianBlur(13))
    image.alpha_composite(glow)
    image.alpha_composite(node_layer)

    image.save(PUBLIC / "documind-signal.png")


if __name__ == "__main__":
    main()
