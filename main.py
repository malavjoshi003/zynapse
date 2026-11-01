"""
Main Application — ZYNAPSE
FastAPI server — static files + API
"""

import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.mongo_loader import load_data, get_df
from app.core.database import ping as mongo_ping, ensure_indexes
from app.api.routes import router as api_router
from app.api.analytics import router as analytics_router


# ================= BASE PATH =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
IS_VERCEL = bool(os.getenv("VERCEL"))

# Application files are not used for writable storage on Vercel.
# Files in /tmp are temporary and are not shared between instances.
if IS_VERCEL:
    USER_IMG_DIR = "/tmp/zynapse-user-images"
else:
    USER_IMG_DIR = os.path.join(STATIC_DIR, "user_images")

os.makedirs(USER_IMG_DIR, exist_ok=True)


# ================= LIFESPAN =================

@asynccontextmanager
async def lifespan(app: FastAPI):
    if mongo_ping():
        print("[MongoDB] Connected successfully")
        ensure_indexes()
    else:
        print("[MongoDB] Not connected; CSV fallback needs to be available")

    load_data()

    from app.core.rf_model import get_model
    get_model()

    from app.core.dataset_builder import build_dataset

    # Preserve local behavior without writing into the deployed app.
    build_dataset(save=not IS_VERCEL)

    yield


# ================= APP INIT =================

app = FastAPI(
    title="ZYNAPSE",
    version="2.0.0",
    lifespan=lifespan,
)


# ================= CORS =================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= CACHE CONTROL =================

@app.middleware("http")
async def no_cache_html(request, call_next):
    response = await call_next(request)
    request_path = request.url.path

    if request_path == "/" or request_path.endswith(".html"):
        response.headers["Cache-Control"] = "no-store, must-revalidate"

    return response


# ================= API ROUTES =================

app.include_router(api_router)
app.include_router(analytics_router)


# ================= HTML ROUTES =================

@app.get("/")
async def home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/index.html")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/marketplace.html")
async def marketplace():
    return FileResponse(os.path.join(STATIC_DIR, "marketplace.html"))


@app.get("/product.html")
async def product():
    return FileResponse(os.path.join(STATIC_DIR, "product.html"))


@app.get("/checkout.html")
async def checkout():
    return FileResponse(os.path.join(STATIC_DIR, "checkout.html"))


@app.get("/login.html")
async def login():
    return FileResponse(os.path.join(STATIC_DIR, "login.html"))


@app.get("/admin.html")
async def admin():
    return FileResponse(os.path.join(STATIC_DIR, "admin.html"))


@app.get("/demand_trends.html")
async def demand_trends():
    return FileResponse(os.path.join(STATIC_DIR, "demand_trends.html"))


@app.get("/predictions.html")
async def predictions():
    return FileResponse(os.path.join(STATIC_DIR, "predictions.html"))


@app.get("/inventory.html")
async def inventory():
    return FileResponse(os.path.join(STATIC_DIR, "inventory.html"))


@app.get("/predict.html")
async def predict_page():
    return FileResponse(os.path.join(STATIC_DIR, "predict.html"))


@app.get("/category_analysis.html")
async def category_analysis_page():
    return FileResponse(os.path.join(STATIC_DIR, "category_analysis.html"))


@app.get("/analytics.html")
async def analytics_page():
    return FileResponse(os.path.join(STATIC_DIR, "analytics.html"))


@app.get("/add_product.html")
async def add_product_page():
    return FileResponse(os.path.join(STATIC_DIR, "add_product.html"))


@app.get("/my_products.html")
async def my_products_page():
    return FileResponse(os.path.join(STATIC_DIR, "my_products.html"))


@app.get("/profile.html")
async def profile_page():
    return FileResponse(os.path.join(STATIC_DIR, "profile.html"))


@app.get("/register.html")
async def register_page():
    return FileResponse(os.path.join(STATIC_DIR, "register.html"))


# ================= PRODUCT IMAGE UPLOAD =================

@app.post("/api/upload-product-image")
async def upload_product_image(
    file: UploadFile = File(...),
    product_id: str = Form(...),
    email: str = Form(...),
):
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    extension = os.path.splitext(file.filename or "")[1].lower()

    if extension not in allowed_extensions:
        return JSONResponse(
            status_code=400,
            content={"detail": "Only jpg/png/webp allowed"},
        )

    try:
        numeric_product_id = int(product_id)
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"detail": "Product ID must be a number"},
        )

    from app.core.database import user_products_col, get_gridfs, get_db

    product_filter = {
        "id": numeric_product_id,
        "owner_email": email.lower(),
    }
    product = user_products_col().find_one(product_filter)

    if product is None:
        return JSONResponse(
            status_code=404,
            content={"detail": "Matching user product not found"},
        )

    file_bytes = await file.read()

    # Generated names avoid using submitted email/path text as a filename.
    filename = f"up_{numeric_product_id}_{uuid.uuid4().hex}{extension}"
    destination = os.path.join(USER_IMG_DIR, filename)

    with open(destination, "wb") as output:
        output.write(file_bytes)

    user_products_col().update_one(
        product_filter,
        {
            "$set": {
                "image_filename": filename,
                "updated_on": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        },
    )

    asin = product.get("asin")

    content_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }[extension]

    if asin is not None:
        gridfs_filename = f"{asin}.jpg"
        database = get_db()
        storage = get_gridfs()

        previous_files = list(
            database["fs.files"].find(
                {"filename": gridfs_filename},
                {"_id": 1},
            )
        )

        storage.put(
            file_bytes,
            filename=gridfs_filename,
            contentType=content_type,
        )

        for previous in previous_files:
            storage.delete(previous["_id"])

    return {
        "success": True,
        "filename": filename,
        "url": f"/static/user_images/{filename}",
        "asin_img": (
            f"/api/images/{asin}.jpg"
            if asin is not None
            else None
        ),
    }


# ================= USER IMAGE ROUTE =================
# Register before /static so this route is not hidden by the mount.

@app.get("/static/user_images/{filename}")
async def serve_user_image(filename: str):
    if (
        filename != os.path.basename(filename)
        or "\\" in filename
        or filename in {".", ".."}
    ):
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid filename"},
        )

    image_path = os.path.join(USER_IMG_DIR, filename)

    if not os.path.isfile(image_path):
        placeholder = os.path.join(
            STATIC_DIR,
            "assets",
            "placeholder_product.png",
        )

        if os.path.isfile(placeholder):
            return FileResponse(
                placeholder,
                media_type="image/png",
            )

        return JSONResponse(
            status_code=404,
            content={"detail": "Image not found"},
        )

    extension = os.path.splitext(filename)[1].lower()
    media_type = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }.get(extension, "application/octet-stream")

    return FileResponse(image_path, media_type=media_type)


# ================= DATA CHECK =================

@app.get("/test-data")
async def test_data():
    dataframe = get_df()
    return {"total_products": len(dataframe)}


# ================= STATIC FILES =================

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR, check_dir=True),
    name="static",
)


# ================= LOCAL DEVELOPMENT =================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )