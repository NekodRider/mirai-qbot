import os
from pathlib import Path

def detectSafeSearchUri(uri):
    """Detects unsafe features in the file located in Google Cloud Storage or
    on the Web."""
    config_file = str(Path(__file__).parent.joinpath("Dota-Project-c6dd8c4677d4.json"))
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config_file

    from google.cloud import vision
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()
    image.source.image_uri = uri

    response = client.safe_search_detection(image=image)
    safe = response.safe_search_annotation

    # # Names of likelihood from google.cloud.vision.enums
    # likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
    #                    'LIKELY', 'VERY_LIKELY')

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return safe.racy