IMAGE=sync-music
DOCKER=docker run -ti --rm -v $(PWD):/workdir -v $(PWD)/token:/root/.local/share/google-music $(IMAGE)

.PHONY: dryrun
dryrun: image state.json
	$(DOCKER) python3 sync.py

.PHONY: sync
sync: image state.json
	$(DOCKER) python3 sync.py --doit

.PHONY: debug
debug: image state.json
	$(DOCKER) sh

.PHONY: image
image:
	docker build --quiet --tag $(IMAGE) .

.PHONY: encrypt
encrypt:
	gpg --default-recipient-self --encrypt state.json

state.json: state.json.gpg
	gpg --output $@ --decrypt $@.gpg
