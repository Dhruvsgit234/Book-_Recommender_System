from flask import Flask, render_template, request
import pickle
import numpy as np

# Load pickled files
popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        votes=list(popular_df['num_ratings'].values),
        rating=list(popular_df['avg_rating'].values)
    )

@app.route('/recommend')
def recommend():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['POST'])
def recommend_book():
    user_input = request.form.get('user_input')

    # Normalize input and index for safer matching
    user_input_clean = user_input.strip().lower()
    pt_index_clean = pt.index.str.lower()

    # Check if the book exists
    matches = np.where(pt_index_clean == user_input_clean)[0]
    if len(matches) == 0:
        return render_template('recommend.html', error="Book not found. Please check the title.(Enter the exact title)")

    index = matches[0]

    # Get similar items
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:8]

    data = []

    for i in similar_items:
        item = []
        temp_df = books[books["Book-Title"] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        data.append(item)

    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
