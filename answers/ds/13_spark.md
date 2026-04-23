# Apache Spark + Scala — Setup and Execution Guide

---

## 1. Install Java

```bash
sudo apt update
sudo apt install openjdk-11-jdk -y
java -version
```

> 📌 Expected: `openjdk version "11.0.x" 2024-xx-xx`

---

## 2. Install Scala (Compatible Version)

```bash
wget https://downloads.lightbend.com/scala/2.12.18/scala-2.12.18.tgz
tar -xvzf scala-2.12.18.tgz
sudo mv scala-2.12.18 /opt/scala
```

Set PATH automatically (no manual editing):

```bash
echo 'export PATH=/opt/scala/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

Verify:

```bash
scala -version
```

> 📌 Expected: `Scala code runner version 2.12.18 -- Copyright 2002-2023, LAMP/EPFL and Lightbend, Inc.`

---

## 3. Install Apache Spark

```bash
wget https://downloads.apache.org/spark/spark-3.5.8/spark-3.5.8-bin-hadoop3.tgz
tar -xvf spark-3.5.8-bin-hadoop3.tgz
mv spark-3.5.8-bin-hadoop3 ~/spark
```

---

## 4. Set Spark Environment Variables

```bash
echo 'export SPARK_HOME=$HOME/spark' >> ~/.bashrc
echo 'export PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

Verify:

```bash
spark-shell
```

> 📌 Expected: `Welcome to Spark version 3.5.8 — Using Scala version 2.12.18`
> Press **Ctrl + C** to exit the shell.

---

## 5. Create Input File

```bash
nano input.txt
```

Type the following content:

```
hello spark
hello scala
hello world
```

> 💾 **To save and exit nano:**
> - Press `Ctrl + O` → then `Enter` to save the file
> - Press `Ctrl + X` to exit nano

---

## 6. Write the Scala Program

```bash
nano SimpleSparkApp.scala
```

Paste the following code:

```scala
import org.apache.spark.sql.SparkSession

object SimpleSparkApp {
  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder()
      .appName("Simple Word Count")
      .master("local[*]")
      .getOrCreate()

    import spark.implicits._

    val textFile = spark.read.textFile("input.txt")

    val counts = textFile
      .flatMap(_.split(" "))
      .groupBy("value")
      .count()

    counts.show()

    spark.stop()
  }
}
```

> 💾 **To save and exit nano:**
> - Press `Ctrl + O` → then `Enter` to save the file
> - Press `Ctrl + X` to exit nano

---

## 7. Compile the Program

```bash
scalac -classpath "$SPARK_HOME/jars/*" SimpleSparkApp.scala
```

---

## 8. Create JAR File

```bash
jar cvf app.jar *.class
```

---

## 9. Run the Program

```bash
spark-submit --class SimpleSparkApp app.jar
```

---

## 10. Expected Output

```
+-----+-----+
|value|count|
+-----+-----+
|hello|    3|
|scala|    1|
|spark|    1|
|world|    1|
+-----+-----+
```

---

## 11. Conclusion

- Apache Spark was successfully installed and configured.
- Scala program was executed using the Spark framework.
- Word count was performed on the input data.

---

## Notes

- Scala version must be **2.12.x** for Spark 3.5.x
- Environment variables were set using shell commands (no manual editing required)
- Spark runs locally using `local[*]`