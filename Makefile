up:
	docker compose -f docker-compose.yml up -d --build

stop:
	docker compose down

agent:
	dapr run --app-id agent-hello --app-port 8000 --dapr-http-port 3500 --dapr-grpc-port 50001 -- python agents/agent_hello/main.py

cleanup:
	docker compose down --volumes --remove-orphans