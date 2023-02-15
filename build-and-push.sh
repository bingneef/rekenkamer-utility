VERSION=${1:-'latest'}
docker build . -f Dockerfile -t bingneef/rekenkamer-utility:${VERSION}
docker push bingneef/rekenkamer-utility:${VERSION}