# -*- coding: utf-8 -*-
# File: save.py

# Copyright 2021 Dr. Janis Meyer. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module for saving
"""

import json
from pathlib import Path
from typing import Optional

from cv2 import imwrite

from ..dataflow import DataFlow, MapData, SerializerJsonlines
from ..datapoint.convert import convert_b64_to_np_array
from ..utils.detection_types import Pathlike
from ..utils.fs import mkdir_p


def dataflow_to_json(
    df: DataFlow,
    path: Pathlike,
    single_files: bool = False,
    file_name: Optional[str] = None,
    max_datapoints: Optional[int] = None,
    save_image: bool = False,
    save_image_in_json: bool = True,
    highest_hierarchy_only: bool = False,
) -> None:
    """
    Save a dataflow consisting of :class:`datapoint.Image` to a jsonl file. Each image will be dumped into a separate
    JSON object.

    :param df: Input dataflow
    :param path: Path to save the file(s) to
    :param single_files: will save image results to a single JSON file. If False all images of the dataflow will be d
                         dumped into a single jsonl file.
    :param file_name: file name, only needed for jsonl files
    :param max_datapoints: Will stop saving after dumping max_datapoint images.
    :param save_image: Will save the image. It can be saved separately in a sub folder "image" or in the .json file.
                       The choice can be customized by the next parameter.
    :param save_image_in_json: Will save the image to the JSON object
    :param highest_hierarchy_only: If True it will remove all image attributes of ImageAnnotations
    """
    if isinstance(path, str):
        path = Path(path)
    if single_files:
        mkdir_p(path)
    if not save_image_in_json:
        mkdir_p(path / "image")

    df = MapData(df, lambda dp: dp.get_export(save_image, highest_hierarchy_only))
    df.reset_state()
    if single_files:
        for idx, dp in enumerate(df):
            if idx == max_datapoints:
                break
            target_file = path / (dp["file_name"].split(".")[0] + ".json")
            if not save_image_in_json:
                target_file_png = path / "image" / (dp["file_name"].split(".")[0] + ".png")
                image = dp.pop("_image")
                image = convert_b64_to_np_array(image)
                imwrite(str(target_file_png), image)

            with open(target_file, "w", encoding="UTF-8") as file:
                json.dump(dp, file)

    else:
        assert file_name, "if single_files is set to False must pass a valid file name for .jsonl file"
        SerializerJsonlines.save(df, path, file_name, max_datapoints)
