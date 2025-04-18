# Github Actions Test Data in AWS

This stack is used to store and retrieve test data for GitHub actions in an S3 bucket, and invalidates the GitHub actions cache when new data is uploaded. When new test data is uploaded, the old data is deleted permanently.

Data is always placed in the download bucket as `test_data.tar.gz`. The cache invalidation routine assumes the data is cached as `test-data`. You can see an example of a setup in the CI for [this repo](https://github.com/ArgonneCPAC/OpenCosmo).

Its input parameters are:

- **ghRepoOwner**: The owner (user or org) of the repository
- **ghRepoName**: The name of the repository
- **ghAcessToken**: A GitHub access token. The token must have read/write priveliges for Actions in the given repository.

The output parameters are.

- **upload-bucket-name**: The name of the bucket to upload new test data to
- **upload-bucket-access-key**: An access key for a new user with put rights to the upload bucket
- **upload-bucket-access-secret**: The secret for the former
- **download-bucket-name**: The bucket your github CI should download data from
- **download-bucket-access-key**: An access key for your CI with read writes to the download bucket.
- **download bucket-access-secret**: The secret for the former

