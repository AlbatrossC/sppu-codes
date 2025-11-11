# 🧠 SPPU Codes

Visit the website for easy access to all codes: 👉 [https://sppucodes.vercel.app](https://sppucodes.vercel.app)

A collection of programs and code snippets for **SPPU (Savitribai Phule Pune University)** students. This project helps students quickly find, view, and use lab assignment codes for multiple subjects — accessible both on the website and directly via the terminal using the API.

---

## 😏 Instantly Get Answers in Your Terminal

Want answers right inside your terminal? Just open your terminal and type the following command 👇

### 🔹 COMMAND API URL Format

```
curl.exe https://sppucodes.vercel.app/api/{subject_code}/{question_no}
```

### 🔹 Example Command (Terminal Interface)

```bash
$ curl.exe https://sppucodes.vercel.app/api/cnl/16
import socket

choice = input("Enter '1' for Domain to IP or '2' for IP to Domain: ")

if choice == '1':
    domain = input("Enter domain name: ")
    ip = socket.gethostbyname(domain)
    print("IP address of", domain, "is:", ip)

elif choice == '2':
    ip = input("Enter IP address: ")
    host = socket.gethostbyaddr(ip)
    print("Domain name of", ip, "is:", host[0])

else:
    print("Invalid choice.")
$
```

💡 **Tip:** Works perfectly on Windows PowerShell, Ubuntu Terminal, or Mac Terminal.

---

## 🤝 How to Contribute

Want to help others by adding your own codes? You can contribute easily by submitting your solutions online.

### 🔸 Submit Your Code

Visit: [https://sppucodes.vercel.app/submit](https://sppucodes.vercel.app/submit)

Your contributions make this resource better for everyone! 🙌

---

## 🧩 Running Locally

Follow these steps to run the project on your local machine.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/AlbatrossC/sppu-codes.git
cd sppu-codes
```

### 2️⃣ Run the App

Make sure you have Python installed, then run:

```bash
python app.py
```

### 3️⃣ Access the Website

Once the server starts, open your browser and go to:

```
http://localhost:3000
```

⚠️ **Note:** Some features like **Contact** and **Submit Code** pages will not function locally because they require a database connection.

---

## 🔄 Pull Latest Updates

To get the latest answers and improvements locally, use:

```bash
git pull origin main
```

This ensures your local repository stays up to date with the newest codes and fixes from the main branch.

---

## 🧰 Preview

<img width="512" height="512" alt="image" src="https://github.com/user-attachments/assets/521b5097-58a9-4175-b2c7-761d64445ce5" />

---

## ⭐ Support the Project

If you find this helpful, consider giving the repo a star ⭐ on GitHub — it helps more students discover it!