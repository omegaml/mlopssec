build:
	docker buildx build --platform linux/amd64,linux/arm64 -t omegaml/mlopssec .
	docker run -it omegaml/mlopssec scripts/test.sh

check:
	@-docker run -it omegaml/mlopssec bash -c "scripts/audit.sh
	scripts/test-cloned.sh

publish:
	docker push omegaml/mlopssec

start:
	docker run -it --name mlopssec --network host -d -v .:/home/jovyan/mlopssec:rw omegaml/mlopssec bash || echo "INFO: Already running"

stop:
	docker stop mlopssec
	docker rm mlopssec

session:
	docker exec -it mlopssec bash

mitmproxy:
	docker exec -it mlopssec mitmweb
