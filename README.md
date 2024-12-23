# Parking Management



docker run --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d postgres

docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management