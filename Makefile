# Define your environmental variables here; TODO: Update them if needed
BAYERN_CLOUD_API_KEY := $(shell echo $(BAYERN_CLOUD_API_KEY))
REPO_PATH := $(shell pwd)
AWS_CREDENTIALS_PATH := ~/.aws
AWS_PROFILE := TM-DSSGx
IMAGE_NAME := bavarian-forest

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Run the Docker container
run:
	docker run \
		-v $(REPO_PATH):/app \
		-v $(AWS_CREDENTIALS_PATH):/root/.aws \
		-e BAYERN_CLOUD_API_KEY=$(BAYERN_CLOUD_API_KEY) \
		-e AWS_PROFILE=$(AWS_PROFILE) \
		-p 8501:8501 \
		-t $(IMAGE_NAME)

# Run the Docker container
run bash:
	docker run \
		-v $(REPO_PATH):/app \
		-v $(AWS_CREDENTIALS_PATH):/root/.aws \
		-e BAYERN_CLOUD_API_KEY=$(BAYERN_CLOUD_API_KEY) \
		-e AWS_PROFILE=$(AWS_PROFILE) \
		-p 8501:8501 \
		-it --entrypoint /bin/bash $(IMAGE_NAME)

# Combined build and run
all: build run