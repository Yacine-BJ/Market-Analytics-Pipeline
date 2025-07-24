from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Configuration Kafka
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "polygon"

# Configuration MySQL
MYSQL_URL = "jdbc:mysql://mysql:3306/exercice" 
MYSQL_PROPERTIES = {
    "user": "test",
    "password": "test",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# Schéma des données Kafka
SCHEMA = StructType([
    StructField("symbol", StringType()),
    StructField("timestamp", LongType()),
    StructField("open", DoubleType()),
    StructField("high", DoubleType()),
    StructField("low", DoubleType()),
    StructField("close", DoubleType()),
    StructField("volume", LongType())
])

def create_spark_session():
    """Crée et configure la session Spark"""
    return SparkSession.builder \
        .appName("PolygonStockProcessor") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,mysql:mysql-connector-java:8.0.30") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .getOrCreate()

def ensure_table_exists(spark):
    """Vérifie que la table MySQL existe"""
    try:
        spark.read \
            .format("jdbc") \
            .option("url", MYSQL_URL) \
            .option("dbtable", "stock_moving_averages") \
            .option("user", MYSQL_PROPERTIES["user"]) \
            .option("password", MYSQL_PROPERTIES["password"]) \
            .load() \
            .limit(1) \
            .collect()
    except Exception as e:
        print(f"Table might not exist, attempting to create: {str(e)}")
        

def write_to_db(batch_df, batch_id):
    """Fonction d'écriture dans MySQL avec gestion d'erreur"""
    try:
        batch_df.write \
            .format("jdbc") \
            .option("url", MYSQL_URL) \
            .option("dbtable", "stock_moving_averages") \
            .option("user", MYSQL_PROPERTIES["user"]) \
            .option("password", MYSQL_PROPERTIES["password"]) \
            .option("driver", MYSQL_PROPERTIES["driver"]) \
            .mode("append") \
            .save()
    except Exception as e:
        print(f"Error writing batch {batch_id}: {str(e)}")
        

def process_stream(spark):
    """Traite le flux Kafka et écrit dans MySQL"""
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

    # Transformation des données
    processed_df = df.select(
        from_json(col("value").cast("string"), SCHEMA).alias("data")
    ).select("data.*") \
     .withColumn("datetime", to_timestamp(from_unixtime(col("timestamp")/1000))) \
     .withWatermark("datetime", "1 minute")

    # Calcul des moyennes mobiles
    windowed_df = processed_df \
        .groupBy(
            "symbol",
            window("datetime", "1 minute").alias("window")
        ) \
        .agg(
            avg("open").alias("avg_open_1min"),
            avg("high").alias("avg_high_1min"),
            avg("low").alias("avg_low_1min"),
            avg("close").alias("avg_close_1min")
        ) \
        .select(
            "symbol",
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            "avg_open_1min",
            "avg_high_1min",
            "avg_low_1min",
            "avg_close_1min"
        )

    # Écriture dans MySQL
    query = windowed_df.writeStream \
        .foreachBatch(write_to_db) \
        .outputMode("update") \
        .option("checkpointLocation", "/tmp/checkpoint") \
        .start()

    return query

def main():
    spark = create_spark_session()
    ensure_table_exists(spark)
    
    print("Starting streaming query...")
    query = process_stream(spark)
    
    try:
        query.awaitTermination()
    except KeyboardInterrupt:
        print("Stopping stream gracefully...")
        query.stop()
    except Exception as e:
        print(f"Streaming query failed: {str(e)}")
        query.stop()
        raise e

if __name__ == "__main__":
    main()