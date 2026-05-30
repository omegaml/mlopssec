build:
	docker buildx build --platform linux/amd64,linux/arm64 -t omegaml/mlopssec .
	docker run -it omegaml/mlopssec scripts/test.sh

check:
	@-docker run -it omegaml/mlopssec bash -c "scripts/audit.sh
	scripts/test-cloned.sh

publish:
	docker push omegaml/mlopssec

session:
	docker run -it --name mlopssec --network host omegaml/mlopssec bash
	docker commit mlopssec omegaml/mlopssec:session

session:
	docker run --rm -it --name mlopssec --network host -v userhome:/home/jovyan:rw omegaml/mlopssec bash


