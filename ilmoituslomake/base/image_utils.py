import sys

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile

from ilmoituslomake.settings import (
    PRIVATE_AZURE_READ_KEY,
    PRIVATE_AZURE_CONTAINER,
    AZURE_STORAGE,
    PUBLIC_AZURE_CONTAINER,
    FULL_WEB_ADDRESS,
)

import base64
import uuid
import io
import requests
from PIL import Image


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
        # print(e, file=sys.stderr)
        pass
    return []


def process_images(model, instance, images):
    # TODO: What if not an image
    data = None
    # print(images, file=sys.stderr)
    for upload in images:

        try:
            if upload["base64"] != "":
                data = base64.b64decode(upload["base64"].split(",")[1])
                del upload["base64"]
            elif upload["url"] != "":
                # print(upload["url"], file=sys.stderr)
                # Skip redownloading/uploading a file that already exists.
                if (
                    not upload["uuid"] in upload["url"]
                    or not PUBLIC_AZURE_CONTAINER in upload["url"]
                ):
                    # print(upload["url"], file=sys.stderr)
                    response = requests.get(upload["url"], stream=True)
                    if response.status_code == 200:
                        response.raw.decode_content = True
                        data = response.raw.read()
            #         else:
            #             continue
            #     else:
            #         continue
            # else:
            #     continue
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
        except Exception as e:
            # print(e, file=sys.stderr)
            continue

        #
        try:
            # print(upload, file=sys.stderr)
            if "data" in upload:
                image = model(
                    uuid=upload["uuid"],
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
        except Exception as e:
            pass
            # print(e, file=sys.stderr)


def update_preprocess_url(notification_id, images):
    for upload in images:
        if upload["base64"] != "":
            pass
        elif upload["url"] != "":
            # Modify proxy urls
            # print(upload["url"], file=sys.stderr)
            if FULL_WEB_ADDRESS in upload["url"]:
                upload["url"] = (
                    "https://"
                    + AZURE_STORAGE
                    + ".blob.core.windows.net/"
                    + PRIVATE_AZURE_CONTAINER
                    + "/"
                    + str(notification_id)
                    + "/"
                    + upload["filename"]
                    + PRIVATE_AZURE_READ_KEY
                )
    return images


def unpublish_images(model, moderated_instance):
    images = {mi["uuid"]: mi for mi in moderated_instance.data["images"]}
    updated_images = []
    qs = model.objects.all().filter(notification=moderated_instance.pk)
    for image in qs:
        if image.published:
            if not str(image.uuid) in images:
                image.published = False
                updated_images.append(image)
    for image in updated_images:
        image.save()


def unpublish_all_images(model, instance):
    updated_images = []
    qs = model.objects.all().filter(notification=instance.pk)
    for image in qs:
        if image.published:
            image.published = False
            updated_images.append(image)
    for image in updated_images:
        image.save()
