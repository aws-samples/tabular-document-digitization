# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from PIL import Image
from io  import BytesIO

class ImageHelper:

    def __init__(self, imageBytes : bytearray):

        self.__image : Image = Image.open(BytesIO(imageBytes))

    def convert(self, outputType = 'pdf') -> bytearray:

        outputBytes = BytesIO()

        self.__image.save(outputBytes, format = outputType)

        return outputBytes.getvalue()

if  __name__ == '__main__':

    with open('000.pdf', 'wb') as f:

        f.write(ImageHelper(open('sample/000.png', 'rb').read()).convert(outputType = 'pdf'))