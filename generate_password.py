from werkzeug.security import generate_password_hash, check_password_hash

hash1 = 'pbkdf2:sha256:50000$6Cc6Mjmo$3fe413a88db1bacfc4d617f7c1547bd1ea4cbd6c5d675a58e78332201f6befc6'

hash2 = 'pbkdf2:sha256:50000$vQutOphQ$9f80b3ef2b5bc2f971a40febf0d964326386e12d1b90e0f6f5d1a235f6e8093d'

print(check_password_hash(hash1, 'password'))
print(check_password_hash(hash2, 'password'))

print(generate_password_hash('password'))
