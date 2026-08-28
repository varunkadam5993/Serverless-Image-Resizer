# Serverless-Image-Resizer

A serverless AWS project that automatically resizes images when they are uploaded to an Amazon S3 bucket.

📌 Project Overview

When a user uploads an image to the input/ folder in an Amazon S3 bucket, an S3 event automatically triggers an AWS Lambda function.

The Lambda function uses Python and the Pillow library to create multiple resized versions of the image:

Thumbnail — 150 × 150
Medium — 500 × 500
Large — 1000 × 1000

The processed images are then stored in the resized/ folder of the S3 bucket.

🏗️ Architecture
                ┌───────────────┐
                │     USER      │
                └───────┬───────┘
                        │
                  Upload Image
                        │
                        ▼
              ┌─────────────────┐
              │    AMAZON S3    │
              │     input/      │
              └────────┬────────┘
                       │
                ObjectCreated Event
                       │
                       ▼
              ┌─────────────────┐
              │   AWS LAMBDA    │
              │ Python + Pillow │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
     Thumbnail       Medium        Large
      150×150        500×500      1000×1000
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    AMAZON S3    │
              │    resized/     │
              └─────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   CLOUDWATCH    │
              │ Logs & Monitoring│
              └─────────────────┘
🚀 AWS Services Used
Service	Purpose
Amazon S3	Stores original and resized images
AWS Lambda	Processes and resizes uploaded images
AWS IAM	Provides permissions for Lambda to access AWS services
Amazon CloudWatch	Stores logs and monitors Lambda execution
📂 Project Structure
serverless-image-resizer/
│
├── lambda_function.py
│
├── requirements.txt
│
├── README.md
│
└── architecture/
    └── architecture-diagram.png
🪣 S3 Bucket Structure
your-s3-bucket/
│
├── input/
│   └── original-image.jpg
│
└── resized/
    │
    ├── thumbnail/
    │   └── original-image.jpg
    │
    ├── medium/
    │   └── original-image.jpg
    │
    └── large/
        └── original-image.jpg
⚙️ How It Works
A user uploads an image to the input/ folder in Amazon S3.
Amazon S3 generates an ObjectCreated event.
The event triggers the AWS Lambda function.
Lambda downloads the uploaded image from S3.
The Pillow library processes the image.
Lambda creates three different image sizes.
The resized images are uploaded back to S3.
Amazon CloudWatch stores Lambda execution logs.
🖼️ Image Sizes
Image Type	Maximum Size
Thumbnail	150 × 150
Medium	500 × 500
Large	1000 × 1000

The application maintains the original image aspect ratio while resizing.

💻 Lambda Function Code
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
📦 Dependencies

The project uses the Pillow library for image processing.

requirements.txt:

Pillow
🔐 IAM Permissions

For this project, the Lambda function requires permissions to:

Read images from Amazon S3
Upload resized images to Amazon S3
Write logs to Amazon CloudWatch

For development and testing, the following AWS managed policies can be attached:

AmazonS3FullAccess
AWSLambdaBasicExecutionRole

For production environments, it is recommended to use a least-privilege IAM policy.

🛠️ Deployment Steps
1. Create an S3 Bucket

Create an Amazon S3 bucket and add the following folders:

input/
resized/
2. Create an IAM Role

Create an IAM role for AWS Lambda and provide S3 and CloudWatch permissions.

3. Create the Lambda Function

Create a Lambda function with:

Runtime: Python 3.12
Architecture: x86_64
4. Add Pillow Layer

Create a Lambda Layer containing the Pillow library and attach it to the Lambda function.

Example:

mkdir python
pip install Pillow -t python

Create a ZIP file containing the python directory and upload it as a Lambda Layer.

5. Configure S3 Trigger

Configure an S3 trigger with:

Event type: ObjectCreated
Prefix: input/

This ensures that only images uploaded to the input/ folder trigger the Lambda function.

6. Upload an Image

Upload an image such as:

input/photo.jpg

The Lambda function will automatically generate:

resized/thumbnail/photo.jpg
resized/medium/photo.jpg
resized/large/photo.jpg
📊 Example Workflow
Upload:
input/photo.jpg

        ↓

AWS Lambda Triggered

        ↓

Image Processing

        ↓

Output:

resized/thumbnail/photo.jpg

resized/medium/photo.jpg

resized/large/photo.jpg
☁️ Monitoring

AWS CloudWatch is used to monitor the Lambda function.

CloudWatch logs can help identify:

Successful image processing
S3 event information
Processing errors
Lambda execution details

Example log output:

Bucket: your-s3-bucket
File: input/photo.jpg

thumbnail created: resized/thumbnail/photo.jpg
medium created: resized/medium/photo.jpg
large created: resized/large/photo.jpg
✨ Features
Serverless architecture
Automatic image processing
Event-driven workflow
Multiple image sizes
Aspect ratio preservation
Amazon S3 integration
AWS Lambda processing
CloudWatch monitoring
No EC2 server required
🔮 Future Enhancements

Possible improvements include:

Support for PNG, JPEG, and WebP formats
Image compression
Automatic image format conversion
Separate input and output buckets
API Gateway integration
Frontend image upload interface
DynamoDB for image metadata
Amazon CloudFront for faster image delivery
Infrastructure as Code using AWS SAM or Terraform
👨‍💻 Author

Varun Kadam

📄 License

This project is created for educational and learning purposes.
