IMAGE=sync-music
DOCKER=docker run -ti --rm -v $(PWD):/workdir -v $(PWD)/token:/root/.local/share/google-music $(IMAGE)

.PHONY: dryrun
dryrun: image
	$(DOCKER) python3 sync.py

.PHONY: sync
sync: image
	$(DOCKER) python3 sync.py --doit

.PHONY: debug
debug: image
	$(DOCKER) sh

.PHONY: image
image:
	docker build --quiet --tag $(IMAGE) .

.PHONY: encrypt
encrypt:
	gpg --default-recipient-self --encrypt state.json

state.json:
	gpg --output $@ --decrypt $@.gpg
