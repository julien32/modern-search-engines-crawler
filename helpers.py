def make_keywords(words):
    return [word if "tübingen" in word else "tübingen " + word for word in words]