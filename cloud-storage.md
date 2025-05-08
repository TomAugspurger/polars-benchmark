# Cloud Storage

This document describes running the [Polars Decision Support](https://github.com/pola-rs/polars-benchmark) benchmarks against Cloud Object Storage (remote S3 and local MinIO).

## Setup

One-time setup that needs to be done before the benchmarks can be run.

### Infra

The benchmarks read from the S3 bucket created and managed by terraform:

```
cd infrastructure/aws
tofu apply
```

### Data

We generate the data locally and upload it to S3.

```
aws s3 cp /datasets/.../data/tpch-data/scale-10.0/ s3://pds-5orbvjq1/scale-10.0/ --recursive  --profile default
```

## Running the Benchmarks

Before running the benchmarks, you need to configure a few things:

### Environment

```
mamba env create
```

That'll create a conda env from `environment.yml` named
`polars-benchmark-runner`.

Then activate it. We're using Coiled's package-sync to get this uploaded.

### Environment variables

Set the following environment variables (used by coiled to auth to S3)

- AWS_ACCESS_KEY
- AWS_SECRET_ACCESS_KEY
- AWS_SESSION_TOKEN

### Remote, CPU

```
coiled batch run \
    --secret-env PATH_STORAGE_OPTIONS__AWS_ACESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    --secret-env PATH_STORAGE_OPTIONS__AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    --secret-env PATH_STORAGE_OPTIONS__AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    --env PATH_TABLES=s3://pds-5orbvjq1/ \
    --env SCALE_FACTOR=10.0 \
    --forward-aws-credentials \
    python -m queries.polars
```

Change the module to `queries.polars.q{id}` to run a specific query if you want.

### Remote, GPU

```
coiled batch run \
    --vm-type=g4dn.xlarge \
    --gpu \
    --forward-aws-credentials \
    --env RUN_POLARS_GPU=1 \
    --secret-env AWS_ACESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    --secret-env AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    --secret-env AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    --env AWS_DEFAULT_REGION=us-east-1 \
    --secret-env AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    --secret-env PATH_STORAGE_OPTIONS__AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    --secret-env PATH_STORAGE_OPTIONS__AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    --secret-env PATH_STORAGE_OPTIONS__AWS_ACESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    --secret-env PATH_STORAGE_OPTIONS__AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    --secret-env PATH_STORAGE_OPTIONS__AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    --env PATH_TABLES=s3://pds-5orbvjq1/ \
    --env SCALE_FACTOR=10.0 \
    python -m queries.polars
```

Change the module to `queries.polars.q{id}` to run a specific query if you want.

### Locally, Remote data, CPU:

For testing

```
PATH_STORAGE_OPTIONS__AWS_ACESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    PATH_STORAGE_OPTIONS__AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    PATH_STORAGE_OPTIONS__AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    PATH_TABLES=s3://pds-5orbvjq1/ \
    SCALE_FACTOR=10.0 \
    python -m queries.polars
```

### Locally, Remote data, CPU:

For testing.

```
RUN_POLARS_GPU=1 \
    AWS_ACESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    AWS_DEFAULT_REGION=us-east-1 \
    PATH_STORAGE_OPTIONS__AWS_ACESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    PATH_STORAGE_OPTIONS__AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    PATH_STORAGE_OPTIONS__AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN \
    PATH_TABLES=s3://pds-5orbvjq1/ \
    SCALE_FACTOR=10.0 \
    python -m queries.polars

```

### Locally, Local Data via MinIO:

For testing. Make sure to

1. Clear any local `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN`
   variables.
2. Clear out your `~/.aws/credentials`. I'm not sure why, but polars seems to struggle
   whne some creds are set there and some are set here.

**CPU**:

```
PATH_STORAGE_OPTIONS__AWS_ACESS_KEY_ID="minioadmin" \
    PATH_STORAGE_OPTIONS__AWS_SECRET_ACCESS_KEY="minioadmin" \
    PATH_STORAGE_OPTIONS__ENDPOINT_URL="http://localhost:9000" \
    PATH_TABLES=s3://pds/ \
    SCALE_FACTOR=10.0 \
    python -m queries.polars 2>&1 | tee logs-local-cpu.txt
```


**GPU**:

```
RUN_POLARS_GPU=1 \
    AWS_DEFAULT_REGION="us-east-1" \
    AWS_ACCESS_KEY_ID="minioadmin" \
    AWS_SECRET_ACCESS_KEY="minioadmin" \
    AWS_ENDPOINT_URL="http://localhost:9000" \
    PATH_STORAGE_OPTIONS__AWS_ACESS_KEY_ID="minioadmin" \
    PATH_STORAGE_OPTIONS__AWS_SECRET_ACCESS_KEY="minioadmin" \
    PATH_STORAGE_OPTIONS__ENDPOINT_URL="http://localhost:9000" \
    PATH_TABLES=s3://pds/ \
    SCALE_FACTOR=10.0 \
    python -m queries.polars 2>&1 | tee logs-local-gpu.txt
```

## Logs

```
coiled logs --no-color '{id}' | grep -i 'Code block' > 'logs-{type}.txt'
```

## Locallay with MinIO


You run this locally with MinIO in a docker container. Use `-v {local-path}:/data`
to persist data after the docker container exits.

```
docker run -p 9000:9000 -p 9001:9001 \
    --rm \
    -v /datasets/toaugspurger:/data \
    quay.io/minio/minio server /data --console-address ":9001"
```

The default credentials are

- `AWS_ACCESS_KEY_ID`: `minioadmin`
- `AWS_SECRET_ACCESS_KEY`: `minioadmin`

and you'll need to use the endpoint URL `http://localhost:9000`.

You'll need to create a Bucket and upload data. For example, using the S3 API:

```
aws s3api create-bucket --bucket pds --endpoint-url http://localhost:9000/
aws s3 cp data/tables/ s3://pds/ --recursive --endpoint-url http://localhost:9000/
```