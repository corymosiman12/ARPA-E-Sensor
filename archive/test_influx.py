import influxdb

def main():
    client = influxdb.InfluxDBClient('localhost', 8086, database='test')
    json_body = [
        {
            "measurement": "cpu_load_short",
            "tags": {
                "host": "server01",
                "region": "us-west"
            },
            "time": "2009-11-10T20:00:00Z",
            "fields": {
                "Float_value": 0.64,
                "Int_value": 3,
                "String_value": "Text",
                "Bool_value": True
            }
        }
    ]

    client.write_points(json_body)
    r = client.query('select * from cpu_load_short')
    print(r)

if __name__ == "__main__":
    main()