up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

deploy:
	kubectl apply -f k8s/

clean:
	docker system prune -f