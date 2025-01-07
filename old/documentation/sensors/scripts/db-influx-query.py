from influxdb import InfluxDBClient

client = InfluxDBClient(
    host='mydomain.com', port=8086, username='myuser', password='mypass', ssl=True, verify_ssl=True
    )
print(client.get_list_database())
client.query('SELECT * FROM db;')