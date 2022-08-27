from flask import Flask, render_template, request, session
from flask import copy_current_request_context
from threading import Thread
from vsearch import search_letters
from checker import check_logged_in
from DBcm import SQLError, UseDatabase, ConnectionError, CredentinalError
import variables

app = Flask(__name__)

app.secret_key = variables.secret_key

app.config['dbconfig'] = variables.host_config


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':

    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        """Log details of the web requests."""
        browser = req.user_agent.browser
        if not browser:
            browser = 'None, but why'
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """insert into log
                    (phrase, letters, ip, browser, results)
                    values
                    (%s, %s, %s, %s, %s)"""
            cursor.execute(_SQL, (req.form['phrase'],
                                  req.form['letters'],
                                  req.remote_addr,
                                  browser,
                                  res))

    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Here are your results: '
    results = str(search_letters(phrase, letters))
    log_thread = Thread(target=log_request, args=(request, results))
    try:
        log_thread.start()
    except Exception as err:
        print(f'Try agains\n{str(err)}')
    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results, )


@app.route('/viewlog')
@check_logged_in
def view_log() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser, results
                    from log"""
            cursor.execute(_SQL)
            data = cursor.fetchall()
        titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
        return render_template('viewlog.html',
                               the_title='View Log',
                               the_row_titles=titles,
                               the_data=data)
    except ConnectionError as err:
        print(f'Problem with database conection: {str(err)}')
    except CredentinalError as err:
        print(f'User-id/pass issues. Error: {str(err)}')
    except SQLError as err:
        print(f'Is query correct? Error: {str(err)}')
    except Exception as err:
        print(f'Some Error: {str(err)}')
    return 'Error'


@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return 'U a log in'


@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return 'Mhh ok, buy'


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    title = 'Welcome to search_letters on the web!'
    return render_template('entry.html', the_title=title)


if __name__ == '__main__':
    app.run(debug=True)
