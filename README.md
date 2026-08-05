# ZYNAPSE

An AI-assisted fashion marketplace that combines machine learning, FastAPI, and MongoDB to help analyze product demand, manage inventory, and provide useful business insights.

---

## About the Project

During my final year, I wanted to build something that combined backend development, databases, and machine learning in one application instead of creating another basic CRUD project.

Fashion marketplaces contain thousands of products, but sellers often have very little information about which products are likely to perform well. My goal was to build a platform that could use historical product information to estimate demand while also providing a complete marketplace where products can be managed and explored.

ZYNAPSE is the result of that idea.

The application combines FastAPI, MongoDB, GridFS, and Machine Learning to create a marketplace capable of predicting demand, managing products, and presenting analytics through a clean web interface.

---

## Features

### Marketplace

- Browse fashion products
- Product detail page
- Category-wise products
- User product management
- Shopping cart
- Order management

### Machine Learning

- Product demand prediction
- Demand trend analysis
- Product analytics
- AI-assisted recommendation workflow

### Dashboard

- Analytics dashboard
- Inventory management
- Category analysis
- Product statistics

### User Management

- User registration
- Login
- Profile management

### Database

- MongoDB
- GridFS image storage
- Indexed collections for faster queries

---

## Technologies Used

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- FastAPI

### Database

- MongoDB
- GridFS

### Machine Learning

- Scikit-learn
- Pandas
- NumPy

### Tools

- Git
- GitHub
- MongoDB Compass
- VS Code

---

## Project Structure

```
zynapse-main

│
├── app
│   ├── api
│   ├── core
│
├── scripts
│
├── data
│
├── static
│
├── main.py
│
└── README.md
```

---

## How It Works

The application follows a simple workflow.

1. Product information is loaded from the dataset.
2. Product images are stored using MongoDB GridFS.
3. Product features are processed by the machine learning model.
4. The model predicts demand categories.
5. The prediction is displayed in the analytics dashboard and marketplace.

---

## Dataset

This project uses the Fashion Product Dataset available on Kaggle.

Dataset Link

https://www.kaggle.com/datasets/nirmalsankalana/fashion-product-text-images-dataset

The repository does not include the image dataset because it is approximately 4 GB.

After downloading the dataset, place the images inside:

```

static/images/

```

---

## Database Setup

Install MongoDB Community Server.

Import the dataset into MongoDB by running:

```bash
python scripts/migrate_to_mongo.py
```

The migration script imports

- Product data
- User data
- Product images into GridFS

---

## Running the Project

Clone the repository

```bash
git clone https://github.com/malavjoshi003/zynapse.git
```

Go to the project directory

```bash
cd zynapse-main
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the migration

```bash
python scripts/migrate_to_mongo.py
```

Start the backend

```bash
python -m uvicorn main:app --reload
```

Open your browser

```
http://127.0.0.1:8000
```

---

## Database Collections

The project uses the following MongoDB collections.

```
products
users
user_products
orders
cart
fs.files
fs.chunks
```

---

## What I Learned

Working on this project gave me practical experience with:

- FastAPI development
- REST API design
- MongoDB and GridFS
- Machine learning integration
- Dataset preprocessing
- Backend architecture
- Git and GitHub workflow

More importantly, it helped me understand how different technologies can be combined into a single real-world application instead of being used separately.

---

## Current Limitations

There are still a few areas that can be improved.

- Improve prediction accuracy
- Enhance recommendation quality
- Add JWT authentication
- Improve frontend responsiveness
- Deploy the application to the cloud

These improvements are planned for future versions.

---

## Future Scope

Some features I plan to add are:

- Better recommendation algorithm
- Real-time trend prediction
- Sales forecasting
- Explainable AI
- Docker deployment
- Cloud hosting
- Admin reporting

---

## Screenshots

Screenshots will be added soon.

---

## Author

**Malav Joshi**

Computer Science Engineering Student

GitHub

https://github.com/malavjoshi003

---

## Acknowledgements

- Kaggle Fashion Dataset
- FastAPI
- MongoDB
- Scikit-learn
- Python Community

---

If you found this project interesting, consider giving it a ⭐ on GitHub.
