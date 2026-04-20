# pip install pyspark

# Simple Spark program using PySpark

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SimpleApp").getOrCreate()

data = ["hello spark", "hello world", "spark is easy"]

rdd = spark.sparkContext.parallelize(data)

result = rdd.flatMap(lambda x: x.split()) \
            .map(lambda word: (word, 1)) \
            .reduceByKey(lambda a, b: a + b)

for item in result.collect():
    print(item)

spark.stop()