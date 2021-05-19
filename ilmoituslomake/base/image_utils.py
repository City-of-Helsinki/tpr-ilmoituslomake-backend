from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile


import base64
import uuid
import io
import requests
from PIL import Image


def preprocess_images(request):
    try:
        images = []
        request_images = []
        # Handle images
        data_images = request.data["data"]["images"]  # DATA, url or base64
        if "images" in request.data:
            # JSON-info
            request_images = request.data["images"]  # validate

        #
        if len(request_images) > 0:
            # images: [{ index: <some number>, base64: "data:image/jpeg;base64,<blah...>"}]
            # Handle base64 image
            for i in range(len(request_images)):
                image_idx = request_images[i]["uuid"]
                for idx in range(len(data_images)):  # image in data_images:
                    image = data_images[idx]
                    if image["uuid"] == image_idx:
                        data_image = data_images[idx]
                        # image = base64.b64decode(str('stringdata'))
                        images.append(
                            {
                                "uuid": str(image_idx),
                                "filename": str(image_idx) + ".jpg",
                                "base64": request_images[i]["base64"]
                                if ("base64" in request_images[i])
                                else "",
                                "url": request_images[i]["url"]
                                if ("url" in request_images[i])
                                else "",
                                "metadata": data_image,
                            }
                        )
                        break
        return images
    except Exception as e:
        print(e)
    return []


def process_images(model, instance, images):
    # TODO: What if not an image
    data = None
    for upload in images:
        if upload["base64"] != "":
            data = base64.b64decode(upload["base64"].split(",")[1])
            del upload["base64"]
        elif upload["url"] != "":
            response = requests.get(upload["url"], stream=True)
            if response.status_code == 200:
                response.raw.decode_content = True
                data = response.raw.read()
            else:
                continue
        else:
            continue
        # TODO: Virus check
        #
        if data != None:
            image = Image.open(io.BytesIO(data))
            with io.BytesIO() as output:
                # print(output)
                image.save(output, format="JPEG")
                upload["data"] = ContentFile(output.getvalue())
        else:
            continue
        #
        image = model(
            filename=upload["filename"],
            data=InMemoryUploadedFile(
                upload["data"],
                None,  # field_name
                upload["filename"],  # file name
                "image/jpeg",  # content_type
                upload["data"].tell,  # size
                None,  # content_type_extra
            ),
            notification=instance,
            metadata=upload["metadata"],
        )
        image.save()
