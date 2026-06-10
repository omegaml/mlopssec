build:
	docker buildx build --platform linux/amd64 --load -t omegaml/mlopssec:amd64 .
	docker buildx build --platform linux/arm64 --load -t omegaml/mlopssec:arm64 .
	docker tag omegaml/mlopssec:amd64 omegaml/mlopssec:latest
	docker run -it omegaml/mlopssec scripts/test.sh

check:
	@-docker run -it omegaml/mlopssec bash -c "scripts/audit.sh
	scripts/test-cloned.sh

publish:
	docker push omegaml/mlopssec:amd64
	docker push omegaml/mlopssec:arm64
	docker buildx imagetools create -t omegaml/mlopssec:latest omegaml/mlopssec:amd64 omegaml/mlopssec:arm64

start:
	docker run -it --name mlopssec --network host -d -v .:/home/jovyan/mlopssec:rw omegaml/mlopssec bash || echo "INFO: Already running"

stop:
	docker stop mlopssec
	docker rm mlopssec

session:
	docker exec -it mlopssec bash

mitmproxy:
	docker exec -it mlopssec mitmweb
