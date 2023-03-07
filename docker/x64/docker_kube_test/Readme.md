Run this image with

docker run -d \
  -it \
  --name test_api \
  --mount type=bind,source="$(pwd)"/,target=/opt/kube \
  test_api_image:latest