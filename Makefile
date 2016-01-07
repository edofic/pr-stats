.PHONY: clean dist zip dockerdist

dist.zip: clean zip dist
	cd dist && zip -r dist.zip .
	mv dist/dist.zip ./
	chmod 666 dist.zip
	rm -rf dist/

dist:
	mkdir -p dist
	cp prst*.py main.py dist/
	pip install -r requirements.txt -t dist/

zip:
	which zip || (apt-get update && apt-get install -y zip)

clean:
	rm -rf dist dist.zip

dockerdist:
	docker run -it --rm -v `pwd`:/source python:2.7 sh -c "cd /source && make dist.zip"
	mv dist.zip _dist.zip
	cp _dist.zip dist.zip
	rm _dist.zip
