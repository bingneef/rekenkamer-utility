from flask import abort, jsonify


def json_abort(code, message):
    response = jsonify({'code': code, 'message': message})

    response.status_code = code
    abort(response)


def get_post_body(req):
    if req.form == {}:  # If form is empty, try to get body as json
        return req.get_json()

    return req.form


def verify_body_keys(body, keys):
    missing_keys = []
    for key in keys:
        if key not in body.keys():
            missing_keys.append(key)

    if len(missing_keys) > 0:
        json_abort(422, f"Missing key(s): {', '.join(missing_keys)}")
