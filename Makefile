run:
	make clean
	make setup
	python3 nlp.py -o 1 -f corpora/treasureisland.txt -l 200 -t 0.5 -O None
	pytest nlp.py -vvrA

setup: requirements.txt
	pip install -r requirements.txt

clean:
	rm -rf __pycache__
