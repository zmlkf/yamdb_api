USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLE_CHOICES = (
    (USER, 'пользователь'),
    (MODERATOR, 'модератор'),
    (ADMIN, 'администратор')
)
ME_URL = 'me'

TEXT_LENGTH = 50
MAX_LENGTH_USERNAME = 150
MAX_LENGTH_EMAIL = 254
MAX_LENGTH_ROLE = max(len(role[0]) for role in ROLE_CHOICES)
MAX_LENGTH_NAME = 256
MAX_LENGTH_SLUG = 50
MIN_SCORE = 1
MAX_SCORE = 10
MAX_LENGTH_CONFIRMATION_CODE = 50
