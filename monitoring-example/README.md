# Example monitoring infrastructure

The nccostorage application exposes metrics consumable by prometheus, on the `/metrics` endpoint.

This folder contains a simple grafana+prometheus docker-compose setup to visualize these metrics on a grafana dashboard. To get started just run:

```
# you might need to run this as sudo
# depending on how you have docker set up

docker-compose up --build
```

You can access grafana on [http://localhost:3000](http://localhost:3000). Just use the default admin user login creadentials:

```
user: admin
password: admin
```
