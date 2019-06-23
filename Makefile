build:
	docker build --tag=ship_well .
run:
	docker run -p 8000:80 ship_well
