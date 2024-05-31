from krita import *
from .palette_converter import PaletteConverter

app = Krita.instance()

palette_converter = PaletteConverter(parent=app)
app.addExtension(palette_converter)

