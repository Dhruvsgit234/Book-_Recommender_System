from flask import Flask, render_template, request
import pickle
import numpy as np
import random

# Load pickled files
popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)

# Mood keywords mapping (simplified - in production, use ML/NLP)
MOOD_KEYWORDS = {
    'happy': ['joy', 'happy', 'cheerful', 'uplifting', 'positive', 'light'],
    'sad': ['sad', 'melancholy', 'tragic', 'heartbreaking', 'emotional'],
    'funny': ['funny', 'humor', 'comedy', 'witty', 'hilarious', 'laugh'],
    'serious': ['serious', 'philosophical', 'thoughtful', 'deep', 'profound'],
    'romantic': ['romance', 'love', 'romantic', 'passion', 'heart'],
    'mystery': ['mystery', 'thriller', 'suspense', 'detective', 'crime'],
    'adventure': ['adventure', 'journey', 'quest', 'exploration', 'action'],
    'inspiring': ['inspirational', 'motivational', 'hope', 'triumph', 'courage']
}

@app.route('/')
def index():
    # Get trending books (top rated with high votes)
    trending_indices = popular_df.nlargest(12, 'avg_rating').index[:12]
    trending_books = {
        'book_name': [popular_df.loc[i, 'Book-Title'] for i in trending_indices],
        'author': [popular_df.loc[i, 'Book-Author'] for i in trending_indices],
        'image': [popular_df.loc[i, 'Image-URL-M'] for i in trending_indices],
        'votes': [popular_df.loc[i, 'num_ratings'] for i in trending_indices],
        'rating': [popular_df.loc[i, 'avg_rating'] for i in trending_indices]
    }
    
    return render_template('index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        votes=list(popular_df['num_ratings'].values),
        rating=list(popular_df['avg_rating'].values),
        trending=trending_books
    )

@app.route('/recommend')
def recommend():
    return render_template('recommend.html')

@app.route('/mood')
def mood_search():
    return render_template('mood.html', moods=list(MOOD_KEYWORDS.keys()))

@app.route('/mood_books', methods=['POST'])
def mood_books():
    selected_moods = request.form.getlist('moods')
    if not selected_moods:
        return render_template('mood.html', moods=list(MOOD_KEYWORDS.keys()), error="Please select at least one mood.")
    
    # Simple keyword-based filtering (in production, use ML/NLP)
    # For now, return random popular books as placeholder
    sample_size = min(20, len(popular_df))
    sample_indices = random.sample(range(len(popular_df)), sample_size)
    
    mood_books = {
        'book_name': [popular_df.iloc[i]['Book-Title'] for i in sample_indices],
        'author': [popular_df.iloc[i]['Book-Author'] for i in sample_indices],
        'image': [popular_df.iloc[i]['Image-URL-M'] for i in sample_indices],
        'votes': [popular_df.iloc[i]['num_ratings'] for i in sample_indices],
        'rating': [popular_df.iloc[i]['avg_rating'] for i in sample_indices]
    }
    
    return render_template('mood_results.html', data=mood_books, selected_moods=selected_moods)

@app.route('/categories')
def categories():
    categories_list = [
        {'name': 'Happy Books', 'slug': 'happy_books', 'icon': '😊', 'desc': 'Uplifting stories to cheer you up'},
        {'name': 'Funny Books', 'slug': 'funny_books', 'icon': '😂', 'desc': 'Hilarious reads for a good laugh'},
        {'name': 'Serious Fiction', 'slug': 'serious_fiction', 'icon': '🤔', 'desc': 'Thought-provoking literature'},
        {'name': 'Romantic', 'slug': 'romantic', 'icon': '💕', 'desc': 'Love stories and romance'},
        {'name': 'Mystery & Thriller', 'slug': 'mystery_thriller', 'icon': '🔍', 'desc': 'Suspenseful page-turners'},
        {'name': 'Adventure', 'slug': 'adventure', 'icon': '🗺️', 'desc': 'Epic journeys and quests'},
        {'name': 'Inspiring', 'slug': 'inspiring', 'icon': '✨', 'desc': 'Motivational and uplifting tales'},
        {'name': 'Short Reads', 'slug': 'short_reads', 'icon': '📖', 'desc': 'Quick reads for busy schedules'},
        {'name': 'Long Reads', 'slug': 'long_reads', 'icon': '📚', 'desc': 'Epic novels to dive deep into'},
        {'name': 'High Rated', 'slug': 'high_rated', 'icon': '⭐', 'desc': 'Top-rated books by readers'},
        {'name': 'Most Popular', 'slug': 'most_popular', 'icon': '🔥', 'desc': 'Books with most ratings'},
        {'name': 'New Discoveries', 'slug': 'new_discoveries', 'icon': '🌟', 'desc': 'Hidden gems to explore'}
    ]
    return render_template('categories.html', categories=categories_list)

@app.route('/category_books/<category>')
def category_books(category):
    # Map category to filtering logic
    if category == 'high_rated':
        filtered = popular_df.nlargest(20, 'avg_rating')
        category_name = 'High Rated Books'
    elif category == 'most_popular':
        filtered = popular_df.nlargest(20, 'num_ratings')
        category_name = 'Most Popular Books'
    elif category == 'short_reads':
        # Placeholder - would need book length data
        filtered = popular_df.sample(min(20, len(popular_df)))
        category_name = 'Short Reads'
    elif category == 'long_reads':
        # Placeholder - would need book length data
        filtered = popular_df.sample(min(20, len(popular_df)))
        category_name = 'Long Reads'
    else:
        filtered = popular_df.sample(min(20, len(popular_df)))
        category_name = category.replace('_', ' ').title()
    
    category_data = {
        'book_name': list(filtered['Book-Title'].values),
        'author': list(filtered['Book-Author'].values),
        'image': list(filtered['Image-URL-M'].values),
        'votes': list(filtered['num_ratings'].values),
        'rating': list(filtered['avg_rating'].values)
    }
    
    return render_template('category_results.html', data=category_data, category_name=category_name)

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
