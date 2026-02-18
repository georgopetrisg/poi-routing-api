# 🧭 POI & Routing API
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![GraphHopper](https://img.shields.io/badge/GraphHopper-%23303030?style=for-the-badge&logo=graphhopper&logoColor=white)](https://www.graphhopper.com/)
[![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)](https://swagger.io/)

[![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=F7DF1E)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=Leaflet&logoColor=white)](https://leafletjs.com/)

[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)

RESTful API for querying **Points of Interest (POIs)**, computing routes via **GraphHopper**, and persisting public/private user routes - implemented in **Python & Flask**.

## 🧩 Project Overview

The **POI Routing API** allows users to:
- Query open datasets of **Points of Interest (POIs)** (e.g., beaches, museums, restaurants)
- Compute routes between POIs using the **GraphHopper Routing Engine**
- Store and manage public or private routes for authenticated users
- Access all functionality through RESTful HTTP endpoints documented via **Swagger UI**

The project combines **Flask**, **SQLite**, and **OpenAPI 3.0.3** to create a modular and extendable backend service.

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend Language** | [![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/) | The primary programming language used (v3.12). |
| **Web Framework** | [![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/) | Lightweight WSGI web application framework. |
| **Routing Engine** | [![GraphHopper](https://img.shields.io/badge/GraphHopper-%23303030?style=for-the-badge&logo=graphhopper&logoColor=white)](https://www.graphhopper.com/) | High-performance routing engine for path calculations. |
| **Database** | [![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html) | Serverless, self-contained SQL database engine. |
| **ORM** | [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-AA200F?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/) | SQL toolkit and Object Relational Mapper. |
| **Containerization** | [![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/) | Application containerization environment. |
| **Documentation** | [![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)](https://swagger.io/) | Automated API documentation via `flasgger`. |
| **Frontend Core** | [![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML) [![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS) | Structure and styling for the user interface. |
| **Scripting** | [![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=F7DF1E)](https://developer.mozilla.org/en-US/docs/Web/JavaScript) | Client-side logic for map interactions and API calls. |
| **Mapping Engine** | [![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=Leaflet&logoColor=white)](https://leafletjs.com/) | Open-source JavaScript library for interactive maps. |

## 🐳 Installation & Running (via Docker)

The easiest way to run the application is using **Docker** and **Docker Compose**. This ensures the environment is exactly as intended, without needing to manually install Python dependencies.

### Prerequisites
* **Docker Desktop** (or Docker Engine on Linux) installed and running.
* **Git** (optional, to clone the repo).

### 1️⃣ Clone the repository
```bash
git clone https://github.com/georgopetrisg/task-management-api.git
```

### 2️⃣ Build and Run the Container

Run the following command to **build** the image and **start the service**. The ```--build``` flag ensures that any recent changes to ```requirements.txt``` or code are included.

```bash
docker compose up --build
```

### 3️⃣ Access the API

Once the container is running, the API will be accessible at:

- **Base URL:** ```http://127.0.0.1:5000```
- **Swagger Documentation:** ```http://127.0.0.1:5000/apidocs```

### 4️⃣ Stop the Application

To stop the server:

- Press ```Ctrl + C``` in the terminal
- Or run:

```bash
docker compose down
```

## 📂 Project Structure

```
├── 📁 app
│   ├── 📁 auth
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 decorator.py
│   │   └── 🐍 routes.py
│   ├── 📁 main
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 routes.py
│   ├── 📁 pois
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 routes.py
│   ├── 📁 routes_api
│   │   ├── 🐍 __init__.py
│   │   └── 🐍 routes.py
│   ├── 📁 static
│   │   ├── 📁 css
│   │   │   └── 🎨 style.css
│   │   └── 📁 js
│   │       ├── 📄 auth.js
│   │       └── 📄 map.js
│   ├── 📁 templates
│   │   ├── 🌐 dashboard.html
│   │   ├── 🌐 login.html
│   │   └── 🌐 register.html
│   ├── 🐍 __init__.py
│   ├── 🐍 database.py
│   ├── 🐍 errors.py
│   ├── 🐍 middleware.py
│   ├── 🐍 models.py
│   └── 🐍 validators.py
├── 📁 data
│   ├── ⚙️ pois.json
│   ├── ⚙️ pois_updated.json
│   └── 🐍 update_ids.py
├── ⚙️ .dockerignore
├── ⚙️ .gitignore
├── 🐳 Dockerfile
├── 📄 LICENSE
├── 📝 README.md
├── 🐍 config.py
├── ⚙️ docker-compose.yml
├── 🐍 insert_pois.py
├── ⚙️ openapi.yml
├── 📄 requirements.txt
└── 🐍 run.py
```

<h2>👥 Authors</h2>

<p align="center">
<table>
  <tr>
    <th>No.</th>
    <th>Student ID</th>
    <th>Name</th>
    <th>Role</th>
    <th>Institution</th>
    <th>Department</th>
    <th>GitHub Profile</th>
  </tr>
  <tr align="center">
    <td>1</td>
    <td>inf2023031</td>
    <td>Georgios Georgopetris</td>
    <td>Undergraduate Student</td>
    <td>
      <a href="https://ionio.gr/" target="_blank">
        <img src="http://iivw.di.ionio.gr/wp-content/uploads/2015/07/logo-ionio-black-150x150.jpg" width="60"/><br>Ionian University
      </a>
    </td>
    <td>
      <a href="https://di.ionio.gr/" target="_blank">
        <img src="https://di.ionio.gr/favicon.ico" width="60"/><br>Informatics
      </a>
    </td>
    <td>
      <a href="https://github.com/georgopetrisg" target="_blank">
          <img src="https://github.com/georgopetrisg.png" width="60"/><br>@georgopetrisg
      </a>
    </td>
  </tr>
  <tr align="center">
    <td>2</td>
    <td>inf2023012</td>
    <td>Eleni-Maria Anthi</td>
    <td>Undergraduate Student</td>
    <td>
      <a href="https://ionio.gr/" target="_blank">
        <img src="http://iivw.di.ionio.gr/wp-content/uploads/2015/07/logo-ionio-black-150x150.jpg" width="60"/><br>Ionian University
      </a>
    </td>
    <td>
      <a href="https://di.ionio.gr/" target="_blank">
        <img src="https://di.ionio.gr/favicon.ico" width="60"/><br>Informatics
      </a>
    </td>
    <td>
      <a href="https://github.com/Marilenaki" target="_blank">
        <img src="https://github.com/Marilenaki.png" width="60"/><br>@Marilenaki
      </a>
    </td>
  </tr>
</table>
</p>

## 📄 License

Distributed under the **MIT License**.  
See [LICENSE](LICENSE) for more information.
<br><br>

> This project was developed as part of the **"Advanced Web Application Development Technologies" (Προχωρημένες Τεχνολογίες Ανάπτυξης Εφαρμογών Διαδικτύου)** course at the **Department of Informatics, Ionian University (2025-2026)**.