install docker 
check installation
create postgres container and run it

docker run --name langgraph-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -p 5442:5432 \
  -d postgres:16


docker ps