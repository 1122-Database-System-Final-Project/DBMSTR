<h1 align="center">TRTBS:<br>Taiwan Railway 🚃 Ticket Booking System<br>台灣鐵路火車訂票系統</h1>

<h2 align="center"><a href="https://" align="center">Demo</a>(尚未更新)</h2>

台灣鐵路火車訂票系統（TRTBS）為使用 Python Flask 和 SQLite 來建構的關聯資料庫系統服務。<br>本專案為國立政治大學的資料庫系統課程（課程代號：1122_703025001/753884001）的期末專題作業。這裡提供的 Demo 僅用於課堂演示。

Taiwan Railway Ticket Booking System (TRTBS) is a relational database management system that built with Python Flask and SQLite.<br>
This project was developed at NCCU for the course: Database System (course no. 1122_703025001/753884001). The system in this project was only for demo on the class and should not be used in real environments.


## 支援操作 Supported operation

TRTBS 可以提供基本的訂票服務，包含查詢車次、訂票、查詢訂單、修改訂單及取消訂單。與現有火車訂票系統不同的是，我們添加了座位選擇的功能，讓訂票的服務更加便利。

TRTBS supports basic ticket booking services, including tickets booking, inquiries, canceling and train schedule inquires. Additionally, this system also offers seat reservation and change services, providing users with a more convenient ticket booking experience.


## 安裝步驟 Installation

### 1. 複製專案資料到本地端 Clone it into your local machine

前往放置專案的目錄，使用以下指令複製專案資料。<br>Navigate to the directory that you want to place the project. Then clone the repository. 

```
git clone https://github.com/1122-Database-System-Final-Project/DBMSTR.git
```

### 2. 建立虛擬環境 Create an virtual environment

- Windows

    ```
    cd DBMSTR
    python -m venv venv
    ```
- Linux, MacOS

    ```
    cd Login-System-with-Python-Flask-and-MySQL
    python3 -m venv venv
    ```

### 3. 啟動虛擬環境 Activate the environment
- Windows

    ```
    venv\Scripts\activate
    ```

- Linux, MacOS
    ```
    . venv/bin/activate
    ```
    or
    ```
    source venv/bin/activate
    ```

### 4. 安裝需求的套件 Install the requirements

```
pip install -r requirements.txt
```