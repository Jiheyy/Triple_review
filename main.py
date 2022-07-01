# -*- coding: utf-8 -*-
from config.init import app
from route import event


# route 설정
app.register_blueprint(event.bp)

if __name__ == "__main__":
        app.run(debug=False, host='127.0.0.1', port=8000)
