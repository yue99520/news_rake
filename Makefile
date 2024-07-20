DOKCER_IMAGE_NAME = "my-docker-image"
docker:
	docker build -t $(DOKCER_IMAGE_NAME) .

version:
	poetry export --without-hashes --format=requirements.txt > requirements.txt