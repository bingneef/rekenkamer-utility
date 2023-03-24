VERSION=${1:-'latest'}
docker build . --platform linux/amd64 -f Dockerfile -t bingneef/rekenkamer-utility:${VERSION}
docker push bingneef/rekenkamer-utility:${VERSION}