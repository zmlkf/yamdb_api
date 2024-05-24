**YAMDB API**

YaMDb is an API designed to collect and manage user reviews for various works of art and media. This API allows users to submit reviews, interact with comments, and manage categories and works. It serves as the backend infrastructure for a platform where users can share their opinions on books, movies, music, and more.

**Technologies Used:**
- Django: a high-level Python web framework for rapid development and clean, pragmatic design.
- Django REST Framework: a powerful and flexible toolkit for building Web APIs in Django.
- Django Filter: provides a simple way to filter down a queryset based on parameters a user provides.
- Django Simple JWT: provides a JSON Web Token authentication backend for the Django REST Framework.
- SQLite: a lightweight, serverless, relational database engine to store data locally.

**Features:**
- Authentication: users can sign up, sign in, and receive JWT tokens for authentication.
- User Management: admins can manage users, including viewing, creating, updating, and deleting user accounts.
- Category and Genre Management: admins can manage categories and genres for movies.
- Title Management: admins can manage movie titles, including adding, viewing, updating, and deleting movie entries.
- Review Management: users can leave reviews for movies, and admins can manage these reviews.
- Comment Management: users can leave comments on reviews, and admins can manage these comments.

**Getting Started:**
1. Clone the repository: `git clone git@github.com:zmlkf/yamdb_api.git`
2. Navigate to the project directory: `cd yamdb_api`
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create a superuser: `python manage.py createsuperuser`
6. Run the development server: `python manage.py runserver`

**API Endpoints:**
- `/admin/`: Django admin interface for managing the database.
- `/api/v1/`: Base endpoint for the API.
- `/api/v1/auth/token/`: Endpoint for obtaining JWT tokens.
- `/api/v1/auth/signup/`: Endpoint for user registration.
- `/api/v1/auth/users/me/`: Endpoint to view and update current user's information.
- `/api/v1/categories/`: Endpoint for managing movie categories.
- `/api/v1/genres/`: Endpoint for managing movie genres.
- `/api/v1/titles/`: Endpoint for managing movie titles.
- `/api/v1/titles/<title_id>/reviews/`: Endpoint for managing reviews for a specific movie.
- `/api/v1/titles/<title_id>/reviews/<review_id>/comments/`: Endpoint for managing comments on a specific review.

## Documentation

[Documentation](http://127.0.0.1:8000/redoc/) contains detailed information on how the YaMDb API works. It explains the functionality of each endpoint and provides examples of API requests and responses. The documentation is presented in the Redoc format.

**Author:**

- GitHub: [Roman Zemliakov](https://github.com/zmlkf)
