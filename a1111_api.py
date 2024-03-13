import requests
import base64
import os
from typing import Dict, Any


def api_change_face(
    input_image: str,
    face_image: str,
    face_restorer: str = "None",
    mask_face: int = 0,
    processing_unit: str = "GPU (CUDA)",
    edited_frames="edited_frames/",
) -> Dict[str, Any]:
    if processing_unit == "GPU (CUDA)":
        device_choice = "CUDA"
    else:
        device_choice = "CPU"

    with open(input_image, "rb") as image_file:
        image_binary = image_file.read()
    base64_image = base64.b64encode(image_binary).decode("utf-8")

    with open(face_image, "rb") as image_file:
        image_binary_face = image_file.read()
    base64_image_face = base64.b64encode(image_binary_face).decode("utf-8")

    current_directory = os.getcwd()
    path = os.path.join(current_directory, edited_frames)
    if not os.path.exists(path):
        os.makedirs(path)
    result_path = os.path.join(path, os.path.basename(input_image))

    payload = {
        "source_image": base64_image_face,
        "target_image": base64_image,
        "source_faces_index": [0],
        "face_index": [0],
        "upscaler": "None",
        "scale": 1,
        "upscale_visibility": 1,
        "face_restorer": face_restorer,  # "None", GFPGAN, CodeFormer
        "restorer_visibility": 1,
        "codeformer_weight": 0.3,
        "restore_first": 1,
        "model": "inswapper_128.onnx",
        "gender_source": 0,
        "gender_target": 0,
        "device": device_choice,
        "mask_face": 1,
    }
    url = "http://127.0.0.1:7860"
    response = requests.post(url=f"{url}/reactor/image", json=payload)
    response_data = response.json()

    # Assuming the API returns a base64-encoded image string in the 'image' field
    if "image" in response_data:
        image_data = base64.b64decode(response_data["image"])
        with open(result_path, "wb") as file:
            file.write(image_data)
        return {
            "status": "success",
            "message": "Image saved successfully",
            "path": result_path,
        }
    else:
        return {
            "status": "error",
            "message": "Failed to retrieve the image from the API",
        }
