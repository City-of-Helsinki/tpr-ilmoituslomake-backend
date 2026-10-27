import base64
import io
from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from PIL import Image

from base.image_utils import process_images


class ImageProcessingTests(SimpleTestCase):
    def process(self, image, image_format, **save_options):
        source = io.BytesIO()
        image.save(source, format=image_format, **save_options)
        upload = {
            "uuid": "4f48a7af-8bb7-49fc-a90f-e7d09fd09903",
            "filename": "upload.jpg",
            "base64": "data:image/unknown;base64,"
            + base64.b64encode(source.getvalue()).decode("ascii"),
            "url": "",
            "metadata": {"description": "Upgrade regression test"},
        }
        model = Mock()
        notification = object()
        with patch("base.image_utils.logger") as logger:
            process_images(model, notification, [upload])
        logger.exception.assert_not_called()
        model.assert_called_once()
        model.return_value.save.assert_called_once_with()
        saved = model.call_args.kwargs
        self.assertIs(saved["notification"], notification)
        self.assertEqual(saved["metadata"], upload["metadata"])
        result = Image.open(saved["data"].file)
        result.load()
        self.assertEqual(result.format, "JPEG")
        self.assertEqual(result.mode, "RGB")
        return result

    def test_rgb_jpeg(self):
        result = self.process(Image.new("RGB", (6, 3), "red"), "JPEG")
        self.assertEqual(result.size, (6, 3))

    def test_opaque_rgba_png(self):
        result = self.process(Image.new("RGBA", (6, 3), (10, 20, 30, 255)), "PNG")
        self.assertEqual(result.size, (6, 3))

    def test_transparent_rgba_png(self):
        result = self.process(Image.new("RGBA", (6, 3), (10, 20, 30, 0)), "PNG")
        self.assertEqual(result.size, (6, 3))

    def test_palette_png(self):
        result = self.process(Image.new("P", (6, 3)), "PNG")
        self.assertEqual(result.size, (6, 3))

    def test_exif_orientation_is_applied_before_saving(self):
        exif = Image.Exif()
        exif[274] = 6
        result = self.process(Image.new("RGB", (6, 3), "blue"), "JPEG", exif=exif)
        self.assertEqual(result.size, (3, 6))

    def test_invalid_image_is_logged_and_not_saved(self):
        model = Mock()
        upload = {"base64": "data:image/png;base64,bm90IGFuIGltYWdl", "url": ""}
        with patch("base.image_utils.logger") as logger:
            process_images(model, object(), [upload])
        logger.exception.assert_called_once_with(
            "Image decoding or JPEG conversion failed"
        )
        model.assert_not_called()
