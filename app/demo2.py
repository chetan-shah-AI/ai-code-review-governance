


def get_user(id):
    query = "SELECT * FROM users WHERE id = " + id
    return query