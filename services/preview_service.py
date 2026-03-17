import requests
import io
from PIL import Image


def gerar_preview(zpl, width_mm, height_mm):

    w_in = float(width_mm) / 25.4
    h_in = float(height_mm) / 25.4

    url = f"http://api.labelary.com/v1/printers/8dpmm/labels/{w_in:.2f}x{h_in:.2f}/0/"

    headers = {
        "Accept": "image/png"
    }

    response = requests.post(url, data=zpl.encode("utf-8"), headers=headers, timeout=5)

    if response.status_code != 200:
        raise Exception(f"Labelary erro {response.status_code}")

    img = Image.open(io.BytesIO(response.content))
    img.thumbnail((500, 250))

    return img