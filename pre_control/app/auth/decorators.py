from flask import request, jsonify
from functools import wraps

# allowed_users = ['zhijin', 'cason']
#
# def require_auth(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         auth_user = request.headers.get('auth-user')
#         if auth_user in allowed_users:
#             return f(*args, **kwargs)
#         else:
#             return jsonify({"message": "Access denied"}), 403
#
#     return decorated_function