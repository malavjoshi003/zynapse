# ZYNAPSE

An AI-assisted fashion marketplace built with FastAPI, MongoDB,
and machine learning, with automated checks through GitHub Actions
and automatic deployment to Vercel.

## Links

- [Live application](https://zynapse-fawn.vercel.app/)
- [GitHub repository](https://github.com/malavjoshi003/zynapse)
- [CI workflow runs](https://github.com/malavjoshi003/zynapse/actions)

## About the Project

ZYNAPSE is a studio-based project combining web development,
database management, and machine learning.

The application helps users explore fashion products and analyze
demand-related indicators such as price, ratings, purchase activity,
and bestseller status.

The local application uses MongoDB for products, users, carts,
orders, and GridFS images. The current Vercel deployment uses a
CSV fallback for product data.

## Features

### Marketplace and User Features

The application includes code for:

- Product browsing and product details
- Category-based exploration
- User registration and login
- Profile management
- User-added products
- Shopping carts and orders

Database-dependent features require a working MongoDB connection.
They are not fully configured in the current cloud deployment.

### Machine Learning and Analytics

- Demand-category prediction
- Product analytics
- Demand trends
- Inventory and category dashboards
- Class-balanced dataset generation

The current model uses Scikit-learn's MLPClassifier.

Demand labels are derived from a composite score based on ratings,
purchase activity, bestseller status, and price. Model accuracy
against these derived labels is not a measure of real-world sales
forecasting accuracy.

### DevOps

- Source code hosted on GitHub
- Automated dependency and syntax checks
- Application startup and HTTP smoke checks
- Automatic production deployment through Vercel
- Git-tracked deployment configuration

## Technologies

| Area | Technologies |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, FastAPI, Uvicorn |
| Database | MongoDB, PyMongo, GridFS |
| Data and machine learning | Pandas, NumPy, Scikit-learn |
| Version control | Git, GitHub |
| Continuous integration | GitHub Actions |
| Continuous deployment and hosting | Vercel |

## Project Structure

```text
zynapse/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── api/
│   └── core/
│       ├── database.py
│       ├── loader.py
│       ├── mongo_loader.py
│       ├── rf_model.py
│       └── dataset_builder.py
├── data/
├── scripts/
├── static/
├── .gitignore
├── .vercelignore
├── main.py
├── requirements.txt
├── test_backend.py
└── README.md
```

## How It Works

1. Load product information from MongoDB.
2. Fall back to the product CSV when MongoDB is unavailable
   or contains no products.
3. Process product attributes and calculate demand-related features.
4. Train the classification model during application startup.
5. Serve the website and API through FastAPI.

In the local MongoDB setup, product images are served using GridFS.

## Run Locally

The current dependency setup has been tested with Python 3.14.

### 1. Clone the Repository

```bash
git clone https://github.com/malavjoshi003/zynapse.git
cd zynapse
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure MongoDB When Needed

The default connection is:

```text
mongodb://localhost:27017
```

The default database name is:

```text
zynapse
```

The application reads these environment variables:

| Variable | Purpose |
|---|---|
| MONGO_URI | MongoDB connection URI |
| MONGO_DB | Database name; defaults to zynapse |

For example, in PowerShell:

```powershell
$env:MONGO_URI = "mongodb://localhost:27017"
$env:MONGO_DB = "zynapse"
```

Set environment variables in the shell or hosting dashboard.
Do not commit database credentials.

### 5. Start the Application

```bash
python -m uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Without MongoDB, the CSV fallback supports product-data loading.
It does not replace database storage for accounts, carts, or orders.

## Dataset and Images

The project uses the
[Fashion Product Dataset](https://www.kaggle.com/datasets/nirmalsankalana/fashion-product-text-images-dataset).

- The CSV fallback loaded 10,000 products during verification.
- The existing local MongoDB database contained 10,002 products.
- The large original image dataset is excluded from Git.
- Cloud image migration is outside the current deployment scope.

For a local dataset setup, images can be placed in:

```text
static/images/
```

The existing migration script can import data into MongoDB:

```bash
python scripts/migrate_to_mongo.py
```

Review its configuration and required input files before running it.
Migration is not required to start the application with CSV data.

## MongoDB Collections

```text
products
users
user_products
orders
cart
fs.files
fs.chunks
```

GridFS uses fs.files and fs.chunks to store image metadata
and image contents.

## Continuous Integration

The workflow is defined in:

```text
.github/workflows/ci.yml
```

It runs automatically on:

- Pushes to main
- Pull requests targeting main

### Automated Checks

1. Check out the repository.
2. Set up Python 3.14.
3. Install requirements.txt.
4. Check dependency compatibility using pip check.
5. Compile application Python files to check syntax.
6. Start FastAPI with an unavailable MongoDB address to exercise
   the CSV fallback.
7. Verify that /test-data returns a positive product count.
8. Verify that the homepage returns a successful HTTP response.

The workflow stops with a failure if these checks fail.

These are smoke checks. They do not test all business logic,
browser interactions, authentication, or database-backed workflows.

## Continuous Deployment

Vercel is connected to the GitHub repository and recognizes
the application as FastAPI.

Each push to main automatically triggers a production deployment.
No manual deployment command or approval is needed after setup.

### Current CI/CD Behavior

```text
Edit files
    ↓
Commit and push to main
    ├── GitHub Actions runs checks
    └── Vercel builds and deploys the application
```

GitHub Actions and Vercel currently run independently.
A failed GitHub Actions check does not automatically block
a Vercel deployment.

Pull requests run the GitHub Actions checks. Vercel may also create
preview deployments according to the project's Git integration settings.

## Deployment Preparation

The deployment work includes:

- Adding Python dependency versions in requirements.txt
- Handling MongoDB connection failures with a CSV fallback
- Setting MongoDB connection timeouts
- Using temporary storage for local upload files on Vercel
- Disabling startup CSV export on Vercel
- Excluding local datasets, backups, and preparation files with
  .vercelignore

## Deployment Verification

The following were verified during setup:

- GitHub Actions completed successfully.
- Vercel reported a Ready production deployment.
- The deployed /test-data endpoint returned:

```json
{"total_products":10000}
```

- A committed and pushed website text change appeared on the live
  Vercel website without a manual redeployment.

## Updating the Application

After editing and saving a file:

```bash
git add static/index.html
git commit -m "Update dashboard content"
git push origin main
```

Check GitHub Actions for the CI result and Vercel for deployment
status. Refresh the live website after the deployment is Ready.

## Current Deployment Limitations

- Cloud MongoDB is not configured.
- Product image migration is not included.
- Login, carts, orders, and other database-dependent features
  are not fully configured for the deployed environment.
- Temporary uploaded files are not persistent or shared between
  Vercel instances.
- Model training runs during startup and can increase startup time.
- CI checks and production deployment are not currently gated together.
- A successful deployment does not establish that every application
  feature works.

## Future Improvements

- Configure persistent cloud database and image storage
- Expand automated API and browser tests
- Make production deployment depend on successful CI checks
- Load a pre-trained model instead of training during startup
- Evaluate demand predictions using independent sales data
- Improve authentication and authorization
- Improve recommendations and frontend responsiveness

## Project and DevOps Work

ZYNAPSE is an existing studio-based project used for this
DevOps implementation.

The DevOps work adds GitHub Actions checks, Vercel deployment,
deployment-related compatibility changes, and documentation.

## Author

**Malav Joshi**

Computer Science Engineering Student

[GitHub profile](https://github.com/malavjoshi003)

## Acknowledgements

- ZYNAPSE studio project contributors
- Kaggle Fashion Dataset
- FastAPI and Uvicorn
- MongoDB and PyMongo
- Scikit-learn, Pandas, and NumPy
- GitHub Actions and Vercel
- OpenAI Codex for implementation and documentation assistance