start_dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

build_dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

build_start_prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

stop:
	docker-compose down --remove-orphans