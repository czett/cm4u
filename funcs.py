import psycopg
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

try:
    load_dotenv()
except:
    pass # :) great code, right?

# with open("credentials.yml", "r") as creds:
#     d = creds.read().split("|")
#     pw = d[0]
#     cli_api = d[1]
#     cli_secret = d[2]

db_password = os.getenv("DB_PASSWORD") # embarassing
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")
cli_api = os.getenv("API_KEY")
cli_secret = os.getenv("API_SECRET")

db_config = {
    "dbname": db_name,
    "user": db_user,
    "password": db_password,
    "host": db_host,
    "port": db_port
}

def login_user(username, password):
    try:
        with psycopg.connect(**db_config) as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT 1
                    FROM users
                    WHERE username = %s AND password = %s
                """

                cur.execute(query, (username, password))
                result = cur.fetchone()

                if result:
                    return True, 200
                else:
                    return False, "Invalid username or password."
    except Exception as e:
        return False, "error"
    
cloudinary.config(
    cloud_name="dwbfhgelv",
    api_key=cli_api,
    api_secret=cli_secret
)

def upload_image(file):
    try:
        upload_result = cloudinary.uploader.upload(file)
        return upload_result['secure_url']
    except Exception as e:
        print(f"Upload error: {e}")
        return None
    
def upload_image(file):
    try:
        upload_result = cloudinary.uploader.upload(file)
        return upload_result['secure_url']
    except Exception as e:
        print(f"Upload error: {e}")
        return None

def save_post_with_images(title, description, image_urls):
    try:
        with psycopg.connect(**db_config) as conn:
            with conn.cursor() as cur:
                post_query = """
                    INSERT INTO posts (title, description)
                    VALUES (%s, %s) RETURNING id
                """
                cur.execute(post_query, (title, description))
                post_id = cur.fetchone()[0]

                image_query = """
                    INSERT INTO post_images (post_id, image_url)
                    VALUES (%s, %s)
                """
                for image_url in image_urls:
                    cur.execute(image_query, (post_id, image_url))

                conn.commit()
                return True
    except Exception as e:
        print(f"Database error: {e}")
        return False

def get_posts():
    posts = []

    try:
        with psycopg.connect(**db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, description FROM posts")
                posts_data = cur.fetchall()

                for post in posts_data:
                    cur.execute("SELECT image_url FROM post_images WHERE post_id = %s", (post[0],))
                    images = cur.fetchall()
                    posts.append({
                        "title": post[1],
                        "description": post[2],
                        "images": [img[0] for img in images]
                    })

        return posts[::-1]
    except Exception as e:
        return f"Database error: {e}"