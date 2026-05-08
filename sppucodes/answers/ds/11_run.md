# Run Guide — MapReduce Log Processor

---

## 1. Create mapper.py

```bash
nano mapper.py
```

Paste this code:

```python
#!/usr/bin/env python3
import sys

for line in sys.stdin:
    line = line.strip()
    parts = line.split()

    if len(parts) >= 3:
        ip = parts[0]
        log_type = parts[1]

        print(f"{log_type}\t1")
        print(f"{ip}\t1")
```

Save and close:
- `Ctrl + X` → Exit
- `Y` → Confirm save
- `Enter` → Keep filename

---

## 2. Create reducer.py

```bash
nano reducer.py
```

Paste this code:

```python
#!/usr/bin/env python3
import sys

current_key = None
current_count = 0

for line in sys.stdin:
    key, value = line.strip().split("\t")
    value = int(value)

    if current_key == key:
        current_count += value
    else:
        if current_key:
            print(f"{current_key}\t{current_count}")
        current_key = key
        current_count = value

if current_key:
    print(f"{current_key}\t{current_count}")
```

Save and close:
- `Ctrl + X` → Exit
- `Y` → Confirm save
- `Enter` → Keep filename

---

## 3. Create log.txt

```bash
nano log.txt
```

Paste this data:

```
192.168.1.1 INFO User login
192.168.1.2 ERROR Disk failure
192.168.1.1 WARNING Low memory
192.168.1.3 INFO File uploaded
192.168.1.2 ERROR Network issue
```

Save and close:
- `Ctrl + X` → Exit
- `Y` → Confirm save
- `Enter` → Keep filename

---

## 4. Give Execute Permission

```bash
chmod +x mapper.py reducer.py
```

---

## 5. Test Locally First

```bash
cat log.txt | ./mapper.py | sort | ./reducer.py
```

Expected output:

```
ERROR       2
INFO        2
WARNING     1
192.168.1.1 2
192.168.1.2 2
192.168.1.3 1
```

---

## 6. Upload Log File to HDFS

```bash
hdfs dfs -mkdir /input
hdfs dfs -put log.txt /input
hdfs dfs -ls /input
```

---

## 7. Run MapReduce on Hadoop

```bash
hdfs dfs -rm -r /output
hadoop jar ~/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar \
  -input /input/log.txt \
  -output /output \
  -mapper mapper.py \
  -reducer reducer.py
```

> If JAR not found, locate it first:
> ```bash
> find ~/hadoop -name "*streaming*.jar"
> ```

---

## 8. View Output

```bash
hdfs dfs -cat /output/part-00000
```

Expected output:

```
192.168.1.1    2
192.168.1.2    2
192.168.1.3    1
ERROR          2
INFO           2
WARNING        1
```

---

## Troubleshooting

**Output folder already exists:**
```bash
hdfs dfs -rm -r /output
```

**log.txt not in HDFS:**
```bash
hdfs dfs -mkdir /input
hdfs dfs -put log.txt /input
```