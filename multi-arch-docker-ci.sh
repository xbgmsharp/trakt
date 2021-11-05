
## Check ENV
if [[ -z "${DOCKER_USERNAME}" ]]; then
 echo 'Missing DOCKER_USERNAME env'
 exit 1
fi
if [[ -z "${DOCKER_PASSWORD}" ]]; then
 echo 'Missing DOCKER_PASSWORD env'
 exit 1
fi

## Instantiate docker buildx builder with multi-architecture support.
docker buildx create --name mybuilder
docker buildx use mybuilder
# Start up buildx and verify that all is OK.
docker buildx inspect --bootstrap

## Log in to Docker Hub for deployment.
echo "$DOCKER_PASSWORD" | docker login -u="$DOCKER_USERNAME" --password-stdin

## Run buildx build and push.
#docker buildx build -t docker-trakt-tools:latest --platform linux/amd64,linux/arm64,linux/arm/v7 .
#docker buildx build -t docker-trakt-tools:latest --platform linux/amd64 --load .
docker buildx build -t ${DOCKER_USERNAME}/docker-trakt-tools:latest --platform linux/amd64,linux/arm64,linux/arm/v7 --push .

## Inspect architecture versions for images
#docker buildx imagetools inspect docker-trakt-tools:latest
docker buildx imagetools inspect ${DOCKER_USERNAME}/docker-trakt-tools:latest

# Inspect architecture manually
#docker inspect --format "{{.Architecture}}" docker-trakt-tools

# Stop and prune and remove buildx builder
docker buildx stop mybuilder
docker buildx prune
docker buildx rm mybuilder
