<h1 align="center">TRTBS:<br>Taiwan Railway 🚃 Ticket Booking System<br>台灣鐵路火車訂票系統</h1>

台灣鐵路火車訂票系統（TRTBS）為使用 Python Flask 和 SQLite 來建構的關聯資料庫系統網頁服務。<br>本專案為國立政治大學的資料庫系統課程（課程代號：1122_703025001/753884001）的期末專題作業。本專案成果僅供課堂演示，不可用於實際的訂票需求。

Taiwan Railway Ticket Booking System (TRTBS) is a relational database management system that built with Python Flask and SQLite.<br>
This project was developed at NCCU for the course: Database System (course no. 1122_703025001/753884001). The system in this project was only for demo on the class and should not be used in real environments.


## 支援操作 Supported operation

TRTBS 可以提供基本的訂票服務，包含查詢車次、訂購車票、查詢訂單、修改訂單及取消訂單。與現有火車訂票系統不同的是，我們添加了座位選擇的功能，讓訂票的服務更加便利。

TRTBS supports basic ticket booking services, including tickets booking, inquiries, canceling and train schedule inquires. Additionally, this system also offers seat reservation and change services, providing users with a more convenient ticket booking experience.

## 檔案架構 File Structure

- `app.py` ：主程式，定義不同網頁服務的路由與顯示資訊。
- `requitement.txt` ： 所有必要套件。
- `/modules` ：功能模組，定義訂票服務功能的運作邏輯。
- `/static` ： 前端介面的 CSS 和 Javascript。
- `/templates` ：HTML 頁面，定義前端顯示內容。
- `/database` ：資料庫，包含 sqlite 資料庫檔案與資料庫架構。

## 安裝步驟 (使用 Docker) Installation

### 1. 複製專案資料到本地端

前往放置專案的目錄，使用以下指令複製專案資料。<br>Navigate to the directory that you want to place the project. Then clone the repository. 

```
git clone https://github.com/1122-Database-System-Final-Project/DBMSTR.git
```

### 2. 啟動 docker

```
sudo docker-compose up -d --build
```

### 3. 進入網站

```
docker-compose logs
```
終端機會顯示網站網址（通常是 `http://127.0.0.1:8000` ），複製連結就可以進入網頁。

### 4. 進入 SQLite

```
cd database
sqlite3 database.db
```

### 5. 備份資料庫

```
sqlite> .backup backup.sq3
```

## 安裝步驟 (使用虛擬環境) Installation

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
    cd DBMSTR
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
如果系統提示需要更新 pip，使用以下指令更新：
```
python -m pip install --upgrade pip
```
接著安裝需求套件。
```
pip install -r requirements.txt
```
### 5. 進入網站 
```
python app.py
```
會執行 `app.py` 主程式，並且在終端機顯示網站網址（通常是 `http://127.0.0.1:8000` ），複製連結就可以進入網頁。