# Generated by Django 3.2.19 on 2023-06-29 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("db_monitor", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="noticegroup",
            name="db_type",
            field=models.CharField(
                choices=[
                    ("mysql", "MySQL"),
                    ("tendbcluster", "TendbCluster"),
                    ("redis", "Redis"),
                    ("kafka", "Kafka"),
                    ("hdfs", "HDFS"),
                    ("es", "ElasticSearch"),
                    ("pulsar", "Pulsar"),
                    ("influxdb", "InfluxDB"),
                    ("riak", "Riak"),
                    ("cloud", "Cloud"),
                ],
                max_length=32,
                verbose_name="数据库类型",
            ),
        ),
    ]