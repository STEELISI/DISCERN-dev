# Database Querying Scripts Documentation

This directory has scripts which have to fine-tuned furthermore in order to get the logs aggregated by the sensors. The type of data collected is varied based on the nature/type of the attack and is stored in `psql` & `influx` databases. [Refer: System Design](https://github.com/STEELISI/DISCERN/blob/main/documentation/sensors/scripts/Architecture.svg)

## Table of Contents

- [db-influx-query.py](./db-influx-query.py)
  - Query `influx` database for data
- [db-psql-query.py](./db-psql-query.py)
  - Query `psql` database for data