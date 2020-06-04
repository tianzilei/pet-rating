import os
import random
import secrets
from datetime import datetime, date
import json

from flask import (render_template,
                   request,
                   session,
                   flash,
                   redirect,
                   url_for)
from sqlalchemy import and_
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.models import background_question, experiment
from app.models import background_question_answer
from app.models import page, question, embody_question, embody_answer
from app.models import background_question_option
from app.models import answer_set, answer, forced_id
from app.models import user, trial_randomization
from app.forms import LoginForm, RegisterForm, StartWithIdForm
from app.utils import saved_data_as_file, map_answers_to_questions, timeit

# Stimuli upload folder setting
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
@app.route('/index')
def index():
    experiments = experiment.query.all()

    if session:
        flash("")
    else:
        #flash("sessio ei voimassa")
        session['language'] = "English"

    return render_template('index.html', title='Home', experiments=experiments)


@app.route('/consent')
def consent():
    exp_id = request.args.get('exp_id', None)
    experiment_info = experiment.query.filter_by(idexperiment=exp_id).first()

    instruction_paragraphs = str(experiment_info.short_instruction)
    instruction_paragraphs = instruction_paragraphs.split('<br>')

    consent_paragraphs = str(experiment_info.consent_text)
    consent_paragraphs = consent_paragraphs.split('<br>')

    if experiment_info.use_forced_id == 'On':
        return redirect(url_for('begin_with_id', exp_id=exp_id))

    return render_template('consent.html',
                           exp_id=exp_id,
                           experiment_info=experiment_info,
                           instruction_paragraphs=instruction_paragraphs,
                           consent_paragraphs=consent_paragraphs)


@app.route('/set_language')
def set_language():
    session['language'] = request.args.get('language', None)
    lang = request.args.get('lang', None)
    return redirect(url_for('index', lang=lang))


@app.route('/remove_language')
def remove_language():
    experiments = experiment.query.all()
    return render_template('index.html', title='Home', experiments=experiments)


@app.route('/session')
def participant_session():
    '''Set up session variables and create answer_set (database level sessions)'''

    # start session
    session['exp_id'] = request.args.get('exp_id', None)
    session['agree'] = request.args.get('agree', None)

    # If user came via the route for "I have already a participant ID that I wish to use, Use that ID, otherwise generate a random ID
    if 'begin_with_id' in session:
        session['user'] = session['begin_with_id']
        session.pop('begin_with_id', None)
    else:
        # lets generate a random id. If the same id is allready in db, lets generate a new one and finally use that in session['user']
        random_id = secrets.token_hex(3)
        check_id = answer_set.query.filter_by(session=random_id).first()

        while check_id is not None:
            random_id = secrets.token_hex(3)
            check_id = answer_set.query.filter_by(session=random_id).first()

        session['user'] = random_id

    # Set session status variables
    exp_status = experiment.query.filter_by(
        idexperiment=session['exp_id']).first()

    # Create answer set for the participant in the database
    the_time = datetime.now()
    the_time = the_time.replace(microsecond=0)

    # Check which question type is the first in answer_set (embody is first if enabled)
    answer_set_type = 'slider'
    if exp_status.embody_enabled:
        answer_set_type = 'embody'

    participant_answer_set = answer_set(experiment_idexperiment=session['exp_id'],
                                        session=session['user'],
                                        agreement=session['agree'],
                                        answer_counter='0',
                                        answer_type=answer_set_type,
                                        registration_time=the_time,
                                        last_answer_time=the_time)
    db.session.add(participant_answer_set)
    db.session.commit()

    # If trial randomization is set to 'On' for the experiment, create a randomized trial order for this participant
    # identification is based on the uniquie answer set id
    if exp_status.randomization == 'On':

        session['randomization'] = 'On'

        # create a list of page id:s for the experiment
        experiment_pages = page.query.filter_by(
            experiment_idexperiment=session['exp_id']).all()
        original_id_order_list = [(int(o.idpage)) for o in experiment_pages]

        # create a randomized page id list
        helper_list = original_id_order_list
        randomized_order_list = []

        for i in range(len(helper_list)):
            element = random.choice(helper_list)
            helper_list.remove(element)
            randomized_order_list.append(element)

        # Input values into trial_randomization table where the original page_ids have a corresponding randomized counterpart
        experiment_pages = page.query.filter_by(
            experiment_idexperiment=session['exp_id']).all()
        original_id_order_list = [(int(o.idpage)) for o in experiment_pages]

        for c in range(len(original_id_order_list)):
            random_page = trial_randomization(page_idpage=original_id_order_list[c], randomized_idpage=randomized_order_list[
                                              c], answer_set_idanswer_set=participant_answer_set.idanswer_set, experiment_idexperiment=session['exp_id'])
            db.session.add(random_page)
            db.session.commit()

    if exp_status.randomization == "Off":
        session['randomization'] = "Off"

    # store participants session id in session list as answer_set, based on experiment id and session id
    session_id_for_participant = answer_set.query.filter(and_(
        answer_set.session == session['user'], answer_set.experiment_idexperiment == session['exp_id'])).first()
    session['answer_set'] = session_id_for_participant.idanswer_set
    # collect experiments mediatype from db to session['type'].
    # This is later used in task.html to determine page layout based on stimulus type
    mediatype = page.query.filter_by(
        experiment_idexperiment=session['exp_id']).first()
    if mediatype:
        session['type'] = mediatype.type
    else:
        flash('No pages or mediatype set for experiment')
        return redirect('/')

    # Redirect user to register page
    if 'user' in session:
        user = session['user']
        return redirect('/register')

    return "Session start failed return <a href = '/login'></b>" + "Home</b></a>"


@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm(request.form)
    questions_and_options = {}
    questions = background_question.query.filter_by(
        experiment_idexperiment=session['exp_id']).all()

    for q in questions:

        options = background_question_option.query.filter_by(
            background_question_idbackground_question=q.idbackground_question).all()
        options_list = [(o.option, o.idbackground_question_option)
                        for o in options]
        questions_and_options[q.idbackground_question,
                              q.background_question] = options_list

    form.questions1 = questions_and_options

    if request.method == 'POST' and form.validate():

        data = request.form.to_dict()
        for key, value in data.items():

            # tähän db insertit

            # flash(key)
            # flash(value)
            # Input registration page answers to database
            participant_background_question_answers = background_question_answer(
                answer_set_idanswer_set=session['answer_set'], answer=value, background_question_idbackground_question=key)
            db.session.add(participant_background_question_answers)
            db.session.commit()

        return redirect('/instructions')

    return render_template('register.html', form=form)


@app.route('/begin_with_id', methods=['GET', 'POST'])
def begin_with_id():
    '''Begin experiment with experiment ID. GET -method returns login page for starting the 
    experiment and POST -method verifys users ID before starting new experiment'''

    exp_id = request.args.get('exp_id', None)
    form = StartWithIdForm()
    experiment_info = experiment.query.filter_by(idexperiment=exp_id).first()

    instruction_paragraphs = str(experiment_info.short_instruction)
    instruction_paragraphs = instruction_paragraphs.split('<br>')

    consent_paragraphs = str(experiment_info.consent_text)
    consent_paragraphs = consent_paragraphs.split('<br>')

    if form.validate_on_submit():

        variable = form.participant_id.data

        # check if participant ID is found from db with this particular ID. If a match is found inform about error
        participant = answer_set.query.filter(and_(
            answer_set.session == variable, answer_set.experiment_idexperiment == exp_id)).first()
        is_id_valid = forced_id.query.filter(and_(
            forced_id.pregenerated_id == variable, forced_id.experiment_idexperiment == exp_id)).first()

        if participant is not None:
            flash(_('ID already in use'))
            return redirect(url_for('begin_with_id', exp_id=exp_id))

        # if there was not a participant already in DB:
        if participant is None:

            if is_id_valid is None:
                flash(_('No such ID set for this experiment'))
                return redirect(url_for('begin_with_id', exp_id=exp_id))

            else:
                # save the participant ID in session list for now, this is deleted after the session has been started in participant_session-view
                session['begin_with_id'] = form.participant_id.data
                return render_template('consent.html', exp_id=exp_id, experiment_info=experiment_info, instruction_paragraphs=instruction_paragraphs, consent_paragraphs=consent_paragraphs)

    return render_template('begin_with_id.html', exp_id=exp_id, form=form)


@app.route('/admin_dryrun', methods=['GET', 'POST'])
@login_required
def admin_dryrun():

    exp_id = request.args.get('exp_id', None)
    form = StartWithIdForm()
    experiment_info = experiment.query.filter_by(idexperiment=exp_id).first()

    if form.validate_on_submit():

        # check if participant ID is found from db with this particular ID. If a match is found inform about error
        participant = answer_set.query.filter(and_(
            answer_set.session == form.participant_id.data, answer_set.experiment_idexperiment == exp_id)).first()
        if participant is not None:
            flash('ID already in use')
            return redirect(url_for('admin_dryrun', exp_id=exp_id))

        # if there was not a participant already in DB:
        if participant is None:
            # save the participant ID in session list for now, this is deleted after the session has been started in participant_session-view
            session['begin_with_id'] = form.participant_id.data
            return render_template('consent.html', exp_id=exp_id, experiment_info=experiment_info)

    return render_template('admin_dryrun.html', exp_id=exp_id, form=form)


@app.route('/instructions')
def instructions():

    participant_id = session['user']
    instructions = experiment.query.filter_by(
        idexperiment=session['exp_id']).first()

    instruction_paragraphs = str(instructions.instruction)
    instruction_paragraphs = instruction_paragraphs.split('<br>')

    return render_template('instructions.html', instruction_paragraphs=instruction_paragraphs, participant_id=participant_id)


@app.route('/researcher_login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        #flash("allready logged in")
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user_details = user.query.filter_by(
            username=form.username.data).first()
        if user_details is None or not user_details.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user_details, remember=form.remember_me.data)
        return redirect(url_for('index'))

#        flash('Login requested for user {}, remember_me={}'.format(
#            form.username.data, form.remember_me.data))
#        return redirect('/index')
    return render_template('researcher_login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/view_research_notification')
def view_research_notification():

    exp_id = request.args.get('exp_id', None)
    image = experiment.query.filter_by(idexperiment=exp_id).first()
    research_notification_filename = image.research_notification_filename

    return render_template('view_research_notification.html', research_notification_filename=research_notification_filename)


@timeit
@app.route('/download_csv')
@login_required
def download_csv():

    exp_id = request.args.get('exp_id', None)
    experiment_info = experiment.query.filter_by(idexperiment=exp_id).all()

    print(experiment_info)

    # answer sets with participant ids
    participants = answer_set.query.filter_by(
        experiment_idexperiment=exp_id).all()

    # pages aka stimulants
    pages = page.query.filter_by(experiment_idexperiment=exp_id).all()

    # background questions
    bg_questions = background_question.query.filter_by(
        experiment_idexperiment=exp_id).all()

    # question
    questions = question.query.filter_by(experiment_idexperiment=exp_id).all()

    # embody questions
    embody_questions = embody_question.query.filter_by(
        experiment_idexperiment=exp_id).all()

    csv = ''

    # create CSV-header
    header = 'participant id;'
    header += ';'.join([str(count) + '. bg_question: ' + q.background_question.strip()
                        for count, q in enumerate(bg_questions, 1)])

    for idx in range(1, len(pages) + 1):
        if len(questions) > 0:
            header += ';' + ';'.join(['page' + str(idx) + '_' + str(count) + '. slider_question: ' +
                                      question.question.strip() for count, question in enumerate(questions, 1)])

    for idx in range(1, len(pages) + 1):
        if len(embody_questions) > 0:
            header += ';' + ';'.join(['page' + str(idx) + '_' + str(count) + '. embody_question: ' +
                                      question.picture.strip() for count, question in enumerate(embody_questions, 1)])

    csv += header + '\r\n'

    csv += generate_answers(participants, pages, questions, embody_questions)

    filename = "experiment_{}_{}.csv".format(
        exp_id, date.today().strftime("%Y-%m-%d"))

    return saved_data_as_file(filename, csv)


@timeit
def generate_answers(participants, pages, questions, embody_questions):

    csv = ''
    answer_row = ''

    for participant in participants:



        # list only finished answer sets
        if int(participant.answer_counter) == 0:
            continue

        try:
            # append user session id
            answer_row += participant.session + ';'

            # append background question answers
            bg_answers = background_question_answer.query.filter_by(
                answer_set_idanswer_set=participant.idanswer_set).all()
            bg_answers_list = [str(a.answer).strip() for a in bg_answers]
            answer_row += ';'.join(bg_answers_list) + ';'

            # append slider answers
            slider_answers = answer.query.filter_by(
                answer_set_idanswer_set=participant.idanswer_set) \
                .order_by(answer.page_idpage, answer.question_idquestion) \
                .all()
            

            pages_and_questions = {}

            for p in pages:
                questions_list = [(p.idpage, a.idquestion) for a in questions]
                pages_and_questions[p.idpage] = questions_list

            _questions = [
                item for sublist in pages_and_questions.values() for item in sublist]

            answers_list = map_answers_to_questions(slider_answers, _questions)

            # typecast elemnts to string
            answers_list = [str(a).strip() for a in answers_list]

            answer_row += ';'.join(answers_list) + \
                ';' if slider_answers else len(
                    questions) * len(pages) * ';'

            # append embody answers (coordinates)
            # save embody answers as bitmap images
            embody_answers = embody_answer.query.filter_by(
                answer_set_idanswer_set=participant.idanswer_set) \
                .order_by(embody_answer.page_idpage) \
                .all()

            pages_and_questions = {}

            for p in pages:
                questions_list = [(p.idpage, a.idembody) for a in embody_questions]
                pages_and_questions[p.idpage] = questions_list

            _questions = [
                item for sublist in pages_and_questions.values() for item in sublist]

            _embody_answers = map_answers_to_questions(embody_answers, _questions)

            answers_list = []

            for answer_data in _embody_answers:

                if not answer_data:
                    answers_list.append('')
                    continue

                try:
                    coordinates = json.loads(answer_data.coordinates)
                    em_height = coordinates.get('height', 600) + 2
                    em_width = coordinates.get('width', 200) + 2

                    coordinates_to_bitmap = [
                        [0 for x in range(em_height)] for y in range(em_width)]

                    coordinates = list(
                        zip(coordinates.get('x'), coordinates.get('y')))

                    for point in coordinates:

                        try:
                            # for every brush stroke, increment the pixel 
                            # value for every brush stroke
                            coordinates_to_bitmap[point[0]][point[1]] += 0.1
                        except IndexError:
                            continue

                    answers_list.append(json.dumps(coordinates_to_bitmap))

                except ValueError as err:
                    app.logger(err)

            answer_row += ';'.join(answers_list) if embody_answers else \
                len(embody_questions) * len(pages) * ';'

            # old way to save only visited points:
            # answers_list = [json.dumps(
            #   list(zip( json.loads(a.coordinates)['x'],
            #   json.loads(a.coordinates)['y']))) for a in embody_answers]

        except TypeError as err:
            print(err)

        csv += answer_row + '\r\n'
        answer_row = ''
    return csv


@app.route('/researcher_info')
@login_required
def researcher_info():
    return render_template('researcher_info.html')


# EOF
