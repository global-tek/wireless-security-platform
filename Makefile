up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

test:
	pip install -r requirements-dev.txt
	pytest -q

deploy:
	kubectl apply -f k8s/

clean:
	docker system prune -f