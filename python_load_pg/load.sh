docker run --rm \
	--network project_network \
	-e DB_HOST=postgres_container \
	-e DB_PORT=5432 \
	-e DB_NAME=dst_satisfaction_clients \
	-e DB_USER=dst_projet \
	-e DB_PASSWORD=dst_projet \
	python_load_pg:latest python3 load_data.py
