from flask import Flask, request, redirect
from handle_exception import *
import datetime as dt
import re
import exrex

app = Flask(__name__)
shortcodes_db = {}


@app.errorhandler(InvalidUsage)
def handle_error(error):
    return error.generate_message()


@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.json if request.content_type == 'application/json' else request.args
    if "url" not in data.keys():
        raise InvalidUsage("Url not present", status_code=400)

    if "shortcode" in data.keys():
        shortcode = data["shortcode"]
        if not re.match(r"^[A-Za-z0-9_]+$", shortcode) or len(shortcode) != 6:
            raise InvalidUsage("The provided shortcode is invalid", status_code=412)
        elif shortcode in shortcodes_db.keys():
            raise InvalidUsage("Shortcode already in use", status_code=400)

    else:
        generate = True
        while generate:
            shortcode = exrex.getone(r"([A-Za-z0-9_]){6}")
            if shortcode not in shortcodes_db.keys():
                generate = False

    shortcodes_db[shortcode] = {"url": data["url"],
                                "created": dt.datetime.utcnow().isoformat(),
                                "lastRedirect": None,
                                "redirectCount": 0}
    response_message = {
        "shortcode": shortcode
    }

    return jsonify(response_message), 201


@app.route("/<string:shortcode>", methods=["GET"])
def get_shortcode(shortcode):
    if shortcode not in shortcodes_db.keys():
        raise InvalidUsage("Shortcode not found", status_code=404)

    shortcodes_db[shortcode]["lastRedirect"] = dt.datetime.utcnow().isoformat()
    shortcodes_db[shortcode]["redirectCount"] += 1
    return redirect(shortcodes_db[shortcode]["url"])  # default is already 302


@app.route("/<string:shortcode>/stats", methods=["GET"])
def get_shortcode_stats(shortcode):
    if shortcode not in shortcodes_db.keys():
        raise InvalidUsage("Shortcode not found", status_code=404)

    response_message = {
        "created": shortcodes_db[shortcode]["created"],
        "lastRedirect": shortcodes_db[shortcode]["lastRedirect"],
        "redirectCount": shortcodes_db[shortcode]["redirectCount"]
    }
    return jsonify(response_message)  # default is 200


if __name__ == "__main__":
    app.run()
