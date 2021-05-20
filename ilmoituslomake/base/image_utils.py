from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile

from ilmoituslomake.settings import (
    PRIVATE_AZURE_READ_KEY,
    PRIVATE_AZURE_CONTAINER,
    AZURE_STORAGE,
    FULL_WEB_ADDRESS,
)

import base64
import uuid
import io
import requests
from PIL import Image


# def preprocess_images(request):
#     try:
#         images = []
#         request_images = []
#         # Handle images
#         data_images = request.data["data"]["images"]  # DATA, url or base64
#         if "images" in request.data:
#             # JSON-info
#             request_images = request.data["images"]  # validate

#         #
#         if len(request_images) > 0:
#             # images: [{ index: <some number>, base64: "data:image/jpeg;base64,<blah...>"}]
#             # Handle base64 image
#             for i in range(len(request_images)):
#                 image_idx = request_images[i]["uuid"]
#                 for idx in range(len(data_images)):  # image in data_images:
#                     image = data_images[idx]
#                     if image["uuid"] == image_idx:
#                         data_image = data_images[idx]
#                         # image = base64.b64decode(str('stringdata'))
#                         images.append(
#                             {
#                                 "uuid": str(image_idx),
#                                 "filename": str(image_idx) + ".jpg",
#                                 "base64": request_images[i]["base64"]
#                                 if ("base64" in request_images[i])
#                                 else "",
#                                 "url": request_images[i]["url"]
#                                 if ("url" in request_images[i])
#                                 else "",
#                                 "metadata": data_image,
#                             }
#                         )
#                         break
#         return images
#     except Exception as e:
#         print(e)
#     return []


def preprocess_images(request):
    try:
        images = []

        # Handle images
        data = {}
        metadata = {image["uuid"]: image for image in request.data["data"]["images"]}
        # URL or Base64
        if "images" in request.data:
            data = {image["uuid"]: image for image in request.data["images"]}

        #
        if len(metadata) != 0:
            # images: [{ index: <some number>, base64: "data:image/jpeg;base64,<blah...>"}]
            for key in metadata:
                if key in data:
                    images.append(
                        {
                            "uuid": str(key),
                            "filename": str(key) + ".jpg",
                            "base64": data[key]["base64"]
                            if ("base64" in data[key])
                            else "",
                            "url": data[key]["url"] if ("url" in data[key]) else "",
                            "metadata": metadata[key],
                        }
                    )
                else:
                    pass
                    print("Existing data.")
        return images
    except Exception as e:
        pass
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
            # uuid=upload["uuid"],
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


def update_preprocess_url(notification_id, images):
    for upload in images:
        if upload["base64"] != "":
            pass
        elif upload["url"] != "" and (FULL_WEB_ADDRESS in upload["url"]):
            upload["url"] = (
                "https://"
                + AZURE_STORAGE
                + ".blob.core.windows.net/"
                + PRIVATE_AZURE_CONTAINER
                + "/"
                + str(notification_id)
                + "/"
                + filename
                + PRIVATE_AZURE_READ_KEY
            )
    return images


def unpublish_images(moderated_instance):
    images = {}  # { mi["uuid"] : mi for mi in moderated_instance.data["images"] }
    updated_images = []
    for image in moderated_instance.images:
        if image.published:
            if not image.metadata["uuid"] in images:
                image.published = False
                updated_images.append(image)
    for image in updated_images:
        image.save()

    # unpublish notificationimages

    # images
    # {
    #     "uuid": str(image_idx),
    #     "filename": str(image_idx) + ".jpg",
    #     "base64": request_images[i]["base64"]
    #     if ("base64" in request_images[i])
    #     else "",
    #     "url": request_images[i]["url"]
    #     if ("url" in request_images[i])
    #     else "",
    #     "metadata": data_image,
    # }
