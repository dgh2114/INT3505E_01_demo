from flask import Flask, jsonify, request

app = Flask(__name__)

# Fake data
books = [
    {"id": 1, "title": "Data Structures and Algorithms", "author": "N. Wirth", "category": "Computer Science", "published_year": 2015},
    {"id": 2, "title": "Operating System Concepts", "author": "Silberschatz", "category": "Computer Science", "published_year": 2018},
    {"id": 3, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "category": "Software Engineering", "published_year": 2019},
    {"id": 4, "title": "Clean Code", "author": "Robert C. Martin", "category": "Software Engineering", "published_year": 2008},
    {"id": 5, "title": "Artificial Intelligence", "author": "Russell & Norvig", "category": "AI", "published_year": 2020},
]

@app.route('/books', methods=['GET'])
def get_books():
    q = request.args.get('q', '').lower()
    category = request.args.get('category', '').lower()
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 2))

    filtered = [
        b for b in books
        if (q in b['title'].lower() or q in b['author'].lower() or q == '')
        and (category in b['category'].lower() or category == '')
    ]

    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]

    return jsonify({
        "page": page,
        "limit": limit,
        "total_items": total,
        "total_pages": (total + limit - 1) // limit,
        "items": paginated
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
