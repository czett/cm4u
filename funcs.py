import psycopg
import cloudinary
import cloudinary.uploader

with open("credentials.yml", "r") as creds:
    d = creds.read().split("|")
    pw = d[0]
    cli_api = d[1]
    cli_secret = d[2]

db_config = {
    "dbname": "postgres",
    "user": "postgres",
    "password": pw,
    "host": "db.rmjtxjyqiltlqevhpzbe.supabase.co",
    "port": "5432"
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

        return posts
    except Exception as e:
        return f"Database error: {e}"