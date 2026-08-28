import boto3
import os
import urllib.parse
from PIL import Image
from io import BytesIO

s3 = boto3.client("s3")

IMAGE_SIZES = {
    "thumbnail": (150, 150),
    "medium": (500, 500),
    "large": (1000, 1000)
}


def lambda_handler(event, context):

    print("Event:", event)

    try:

        bucket = event["Records"][0]["s3"]["bucket"]["name"]

        key = urllib.parse.unquote_plus(
            event["Records"][0]["s3"]["object"]["key"]
        )

        print("Bucket:", bucket)
        print("File:", key)

        # Process only files uploaded to input/
        if not key.startswith("input/"):
            return {
                "statusCode": 200,
                "body": "File ignored"
            }

        # Download image from S3
        response = s3.get_object(
            Bucket=bucket,
            Key=key
        )

        image_data = response["Body"].read()

        image = Image.open(
            BytesIO(image_data)
        )

        # Convert images with transparency
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        filename = os.path.basename(key)

        # Create multiple image sizes
        for size_name, dimensions in IMAGE_SIZES.items():

            resized_image = image.copy()

            # Maintain aspect ratio
            resized_image.thumbnail(dimensions)

            buffer = BytesIO()

            resized_image.save(
                buffer,
                format="JPEG",
                quality=85
            )

            buffer.seek(0)

            output_key = (
                f"resized/{size_name}/{filename}"
            )

            # Upload resized image
            s3.put_object(
                Bucket=bucket,
                Key=output_key,
                Body=buffer,
                ContentType="image/jpeg"
            )

            print(
                f"{size_name} created: {output_key}"
            )

        return {
            "statusCode": 200,
            "body": "Images resized successfully"
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "body": str(e)
        }
