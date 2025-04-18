import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_notifications as s3_notifications
from aws_cdk import CfnOutput, CfnParameter, Duration, Stack
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct


class S3TestDataStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        gh_access_token = CfnParameter(
            self, "ghAccessToken", description="Access token for Github"
        )
        repo_owner = CfnParameter(
            self, "ghRepoOwner", description="Owner of the repository"
        )
        repo_name = CfnParameter(
            self, "ghRepoName", description="Name of the repository"
        )

        download_user_group = iam.Group(self, "test-data-download-users")
        download_user = iam.User(self, "test-data-download-user")
        download_user.add_to_group(download_user_group)

        upload_group = iam.Group(self, "test-data-upload-users")
        upload_user = iam.User(self, "test-data-upload-user")
        upload_user.add_to_group(upload_group)

        access_key = iam.CfnAccessKey(
            self, "test-data-upload-access-key", user_name=upload_user.user_name
        )

        download_access_key = iam.CfnAccessKey(
            self, "test-data-download-access-key", user_name=download_user.user_name
        )

        upload_bucket = s3.Bucket(
            self,
            "test-data-upload-bucket",
        )

        download_bucket = s3.Bucket(self, "test-data-download-bucket")

        new_data_lambda = PythonFunction(
            self,
            "new-data-handler",
            entry="s3_test_data/lambda",
            runtime=lambda_.Runtime.PYTHON_3_12,
            index="new_data.py",
            environment={
                "UPLOAD_BUCKET_NAME": upload_bucket.bucket_name,
                "DOWNLOAD_BUCKET_NAME": download_bucket.bucket_name,
                "GITHUB_ACCESS_TOKEN": gh_access_token.value_as_string,
                "REPO_OWNER": repo_owner.value_as_string,
                "REPO_NAME": repo_name.value_as_string,
            },
            timeout=Duration.seconds(120),
        )

        upload_notification = s3_notifications.LambdaDestination(new_data_lambda)
        upload_notification.bind(self, upload_bucket)
        upload_bucket.add_object_created_notification(
            upload_notification, s3.NotificationKeyFilter(suffix=".tar.gz")
        )

        upload_bucket.grant_read_write(new_data_lambda)
        download_bucket.grant_read_write(new_data_lambda)

        upload_bucket.grant_put(upload_user)
        download_bucket.grant_read(download_user)

        CfnOutput(self, "download-bucket-name", value=download_bucket.bucket_name)
        CfnOutput(self, "download-access-key", value=download_access_key.ref)
        CfnOutput(
            self,
            "download-access-secret",
            value=download_access_key.attr_secret_access_key,
        )
        CfnOutput(self, "upload-bucket-name", value=upload_bucket.bucket_name)
        CfnOutput(self, "upload-access-key", value=access_key.ref)
        CfnOutput(self, "upload-access-secret", value=access_key.attr_secret_access_key)
