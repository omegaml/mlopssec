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
	scripts/start.sh

start-win:
	scripts/start-win.sh

stop:
	scripts/stop.sh

session:
	scripts/session.sh

mitmproxy:
	docker exec -it mlopssec mitmweb
