import pandas as pd

from services.database import get_connection
from services.embeddings import create_embedding


CSV_FILE = "data/Amazon_Reviews.csv"


def ingest_data():

    df = pd.read_csv(CSV_FILE, on_bad_lines='skip', encoding='utf-8', engine='python')

    print("Total rows:", len(df))

    connection = get_connection()

    cursor = connection.cursor()

    for index, row in df.iterrows():

        review_text = f"""
Review Title: {row.get('Review Title', '')}

Review:
{row.get('Review Text', '')}

Rating:
{row.get('Rating', '')}

Country:
{row.get('Country', '')}

Review Date:
{row.get('Review Date', '')}
"""

        embedding = create_embedding(review_text)

        # Extract rating number from text like "Rated 1 out of 5 stars"
        rating_text = str(row.get("Rating", "0"))
        rating = 0
        if "Rated" in rating_text:
            try:
                rating = int(rating_text.split()[1])
            except:
                rating = 0
        else:
            try:
                rating = int(rating_text)
            except:
                rating = 0

        cursor.execute(
            """
            INSERT INTO amazon_reviews
            (
                reviewer_name,
                country,
                rating,
                review_date,
                review_title,
                review_text,
                embedding
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(row.get("Reviewer Name", "")),
                str(row.get("Country", "")),
                rating,
                str(row.get("Review Date", "")),
                str(row.get("Review Title", "")),
                str(row.get("Review Text", "")),
                embedding
            )
        )

        if index % 100 == 0:
            print(f"Processed {index} rows")

    connection.commit()

    cursor.close()
    connection.close()

    print("Data ingestion completed.")


if __name__ == "__main__":
    ingest_data()