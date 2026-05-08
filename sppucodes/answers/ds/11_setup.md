# Setup Guide — MapReduce Log Processor

---

## 1. Install Java

```bash
sudo apt update
sudo apt install openjdk-8-jdk -y
java -version
```

---

## 2. Download & Extract Hadoop

```bash
wget https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
tar -xvzf hadoop-3.3.6.tar.gz
mv hadoop-3.3.6 hadoop
```

---

## 3. Set Environment Variables

```bash
nano ~/.bashrc
```

Add at the bottom:

```bash
export HADOOP_HOME=~/hadoop
export PATH=$PATH:$HADOOP_HOME/bin
export PATH=$PATH:$HADOOP_HOME/sbin
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```

```bash
source ~/.bashrc
```

---

## 4. Configure Hadoop

**core-site.xml** — `nano ~/hadoop/etc/hadoop/core-site.xml`

```xml
<configuration>
  <property>
    <n>fs.defaultFS</n>
    <value>hdfs://localhost:9000</value>
  </property>
</configuration>
```

**hdfs-site.xml** — `nano ~/hadoop/etc/hadoop/hdfs-site.xml`

```xml
<configuration>
  <property>
    <n>dfs.replication</n>
    <value>1</value>
  </property>
</configuration>
```

---

## 5. Fix JAVA_HOME in Hadoop Config

```bash
readlink -f $(which java)
# Output example: /usr/lib/jvm/java-8-openjdk-amd64/bin/java
```

```bash
nano ~/hadoop/etc/hadoop/hadoop-env.sh
```

Find and update:

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```

---

## 6. Format Namenode

```bash
hdfs namenode -format
```

---

## 7. Set Up SSH (Passwordless)

```bash
sudo apt install openssh-server -y
sudo service ssh start
ssh-keygen -t rsa -P ""
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
ssh localhost
```

---

## 8. Start Hadoop

```bash
start-dfs.sh
start-yarn.sh
jps
```

---

## 9. Install Python

```bash
sudo apt install python3 -y
sudo apt install python3-pip -y
sudo apt install python-is-python3
python --version
```

---

## 10. Verify Hadoop is Ready

```bash
hadoop version
hdfs dfs -ls /
```