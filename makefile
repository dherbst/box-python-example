.PHONY: builddocker run

builddocker:
	docker build -t box .

run:
	docker run -it --rm -v ${PWD}:/usr/share/project -w /usr/share/project box bash
