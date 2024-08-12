test:
	docker-compose -f tests/docker-compose.yml up --build --exit-code-from migrate migrate && \
	docker-compose -f tests/docker-compose.yml up --build --exit-code-from create_superuser create_superuser && \
	docker-compose -f tests/docker-compose.yml up --build --exit-code-from tests tests  && \
	docker-compose -f tests/docker-compose.yml down -v
