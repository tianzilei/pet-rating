from app import app, db
from flask import render_template, request
from app.models import background_question, experiment
from app.models import background_question_answer
from app.models import page, question
from app.models import background_question_option
from app.models import answer_set, answer, forced_id
from flask import session
from app.forms import LoginForm, RegisterForm
from flask import flash, redirect
from flask import url_for
from wtforms_sqlalchemy.fields import QuerySelectField
from app.forms import Answers, Questions
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from app.forms import BackgroundQuestionForm
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from app.forms import TestForm, TestForm1, TestForm2, TaskForm
from collections import OrderedDict
from sqlalchemy import func, desc
from app.forms import ContinueTaskForm
from sqlalchemy import and_
from app.models import user, trial_randomization
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from sqlalchemy import update
from app.forms import StartWithIdForm
import secrets
from app.forms import CreateExperimentForm, CreateBackgroundQuestionForm, CreateQuestionForm, UploadStimuliForm, EditBackgroundQuestionForm, EditQuestionForm, EditExperimentForm, UploadResearchBulletinForm
from app.forms import EditPageForm, RemoveExperimentForm
import os
import random
from flask import Flask, make_response
import pyexcel as pe
import io
from io import BytesIO
import csv
from flask import send_file
from flask import make_response
from flask_babel import Babel
from app import babel
from datetime import datetime
from app.forms import GenerateIdForm
import math
from flask_babel import _
from flask_babel import lazy_gettext as _l

#Stimuli upload folder setting
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
        



    return render_template('consent.html', exp_id=exp_id, experiment_info=experiment_info, instruction_paragraphs=instruction_paragraphs, consent_paragraphs=consent_paragraphs)


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

    #start session
    session['exp_id'] = request.args.get('exp_id', None)
    session['agree'] = request.args.get('agree', None)
    
  
    #If user came via the route for "I have already a participant ID that I wish to use, Use that ID, otherwise generate a random ID
    
    if 'begin_with_id' in session:

        session['user'] = session['begin_with_id']
        session.pop('begin_with_id', None)

    else:
        
        #lets generate a random id. If the same id is allready in db, lets generate a new one and finally use that in session['user']
        
        random_id = secrets.token_hex(3)
        check_id = answer_set.query.filter_by(session=random_id).first()

        while check_id is not None:
        
            #flash("ID already existed; generated a new one")
            random_id = secrets.token_hex(3)
            check_id = answer_set.query.filter_by(session=random_id).first()

        
        
        session['user'] = random_id
    
    
    #create answer set for the participant in the database
    the_time = datetime.now()
    the_time = the_time.replace(microsecond=0)
    participant_answer_set = answer_set(experiment_idexperiment=session['exp_id'], session=session['user'], agreement = session['agree'], answer_counter = '0', registration_time=the_time, last_answer_time=the_time)
    db.session.add(participant_answer_set)
    db.session.commit()
    
    
    
    #If trial randomization is set to 'On' for the experiment, create a randomized trial order for this participant
    #identification is based on the uniquie answer set id

    exp_status = experiment.query.filter_by(idexperiment=session['exp_id']).first()

    if exp_status.randomization == 'On':
    
        session['randomization'] = 'On'
        
        #flash("answer_set_id")
        #flash(participant_answer_set.idanswer_set)
        
        #create a list of page id:s for the experiment
        experiment_pages = page.query.filter_by(experiment_idexperiment=session['exp_id']).all()
        original_id_order_list = [(int(o.idpage)) for o in experiment_pages]
        
        
        #flash("original Page id order:")
        #for a in range(len(original_id_order_list)):
            
            #flash(original_id_order_list[a])
        
        #create a randomized page id list    
        helper_list = original_id_order_list 
        randomized_order_list = []
    
        for i in range(len(helper_list)):
    
            element = random.choice(helper_list)
            helper_list.remove(element)
            randomized_order_list.append(element)
       
        
        #Input values into trial_randomization table where the original page_ids have a corresponding randomized counterpart
        experiment_pages = page.query.filter_by(experiment_idexperiment=session['exp_id']).all()
        original_id_order_list = [(int(o.idpage)) for o in experiment_pages]
        
        for c in range(len(original_id_order_list)):
    
            random_page = trial_randomization(page_idpage=original_id_order_list[c], randomized_idpage=randomized_order_list[c], answer_set_idanswer_set = participant_answer_set.idanswer_set, experiment_idexperiment = session['exp_id'])
            db.session.add(random_page)
            db.session.commit()
    
    if exp_status.randomization == "Off":
        
        session['randomization'] = "Off"
    
    
    
    
    #store participants session id in session list as answer_set

    #old: was missing experiment id so made duplicates
    #session_id_for_participant = answer_set.query.filter_by(session=session['user']).first()
    
    #store participants session id in session list as answer_set, based on experiment id and session id
    session_id_for_participant = answer_set.query.filter(and_(answer_set.session==session['user'], answer_set.experiment_idexperiment==session['exp_id'])).first()
    session['answer_set'] = session_id_for_participant.idanswer_set
    
    #collect experiments mediatype from db to session['type']. 
    #This is later used in task.html to determine page layout based on stimulus type
    mediatype = page.query.filter_by(experiment_idexperiment=session['exp_id']).first()

    if mediatype:
        session['type'] = mediatype.type
    else:
        flash('No pages or mediatype set for experiment')
        return redirect('/')
    
    
    if 'user' in session:
        user = session['user']
        #flash('Session started for user {}'.format(user))
        return redirect('/register')
      
    return "Session start failed return <a href = '/login'></b>" + "Home</b></a>"


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    
    form = RegisterForm(request.form)
    questions_and_options = {}
    questions = background_question.query.filter_by(experiment_idexperiment=session['exp_id']).all()

    for q in questions:    
    
        options = background_question_option.query.filter_by(background_question_idbackground_question=q.idbackground_question).all()
        options_list = [(o.option, o.idbackground_question_option) for o in options]
        questions_and_options[q.idbackground_question, q.background_question]  = options_list
    
 
    form.questions1 = questions_and_options
    
    if request.method == 'POST'and form.validate():
    
        data = request.form.to_dict()
        for key, value in data.items():

            
            #tähän db insertit

            #flash(key)
            #flash(value)
            #Input registration page answers to database
            participant_background_question_answers = background_question_answer(answer_set_idanswer_set=session['answer_set'], answer=value, background_question_idbackground_question=key)
            db.session.add(participant_background_question_answers)
            db.session.commit()

        return redirect('/instructions')
   
    
    return render_template('register.html', form=form)


@app.route('/task_completed')
def task_completed():
    
    session.pop('user', None)
    session.pop('exp_id', None)    
    session.pop('agree', None)
    session.pop('answer_set', None)
    session.pop('type', None)
    session.pop('randomization', None)

    
    return render_template('task_completed.html')


@app.route('/continue_task', methods=['GET', 'POST'])
def continue_task():
    
    
    exp_id = request.args.get('exp_id', None)
    form = ContinueTaskForm()
    

    if form.validate_on_submit():
        
        #check if participant ID is found from db and that the answer set is linked to the correct experiment
        participant = answer_set.query.filter(and_(answer_set.session==form.participant_id.data, answer_set.experiment_idexperiment==exp_id)).first()
        if participant is None:
            flash('Invalid ID')
            return redirect(url_for('continue_task', exp_id=exp_id))        
        
        #flash('Login requested for participant {}'.format(form.participant_id.data))
        
        #if correct participant_id is found with the correct experiment ID; start session for that user
        session['exp_id'] = exp_id
        session['user'] = form.participant_id.data 
        session['answer_set'] = participant.idanswer_set
        mediatype = page.query.filter_by(experiment_idexperiment=session['exp_id']).first()
        
        rand = experiment.query.filter_by(idexperiment=session['exp_id']).first()
        
        session['randomization'] = rand.randomization
    
        if mediatype:
            session['type'] = mediatype.type
        else:
            flash('No pages or mediatype set for experiment')
            return redirect('/')


        #If participant has done just the registration redirect to the first page of the experiment        
        if participant.answer_counter == 0:
            #flash("Ei vastauksia ohjataan ekalle sivulle")
            return redirect( url_for('task', page_num=1))
        
        
        redirect_to_page = participant.answer_counter + 1
        
        
        #flash("redirect to page:")
        #flash(redirect_to_page)

        experiment_page_count = db.session.query(page).filter_by(experiment_idexperiment=session['exp_id']).count()
        
        #If participant has ansvered all pages allready redirect to task completed page
        if experiment_page_count == participant.answer_counter:
            
            return redirect( url_for('task_completed'))
        
        
        return redirect( url_for('task', page_num=redirect_to_page))
        
    return render_template('continue_task.html', exp_id=exp_id, form=form)


@app.route('/begin_with_id', methods=['GET', 'POST'])
def begin_with_id():
    
    
    exp_id = request.args.get('exp_id', None)
    form = StartWithIdForm()
    experiment_info = experiment.query.filter_by(idexperiment=exp_id).first()
    
    instruction_paragraphs = str(experiment_info.short_instruction)
    instruction_paragraphs = instruction_paragraphs.split('<br>')
    
    consent_paragraphs = str(experiment_info.consent_text)
    consent_paragraphs = consent_paragraphs.split('<br>')
    
    

    if form.validate_on_submit():
        
        variable = form.participant_id.data
        
        #check if participant ID is found from db with this particular ID. If a match is found inform about error
        participant = answer_set.query.filter(and_(answer_set.session==variable, answer_set.experiment_idexperiment==exp_id)).first()
        is_id_valid = forced_id.query.filter(and_(forced_id.pregenerated_id==variable, forced_id.experiment_idexperiment==exp_id)).first()
        
        if participant is not None:
            flash(_('ID already in use'))
            return redirect(url_for('begin_with_id', exp_id=exp_id))        
        
        #if there was not a participant already in DB:
        if participant is None:
    
            if is_id_valid is None:

                                
                flash(_('No such ID set for this experiment'))
                return redirect(url_for('begin_with_id', exp_id=exp_id))        

            else:
                
                #save the participant ID in session list for now, this is deleted after the session has been started in participant_session-view
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
        
        #check if participant ID is found from db with this particular ID. If a match is found inform about error
        participant = answer_set.query.filter(and_(answer_set.session==form.participant_id.data, answer_set.experiment_idexperiment==exp_id)).first()
        if participant is not None:
            flash('ID already in use')
            return redirect(url_for('admin_dryrun', exp_id=exp_id))        
        
        #if there was not a participant already in DB:
        if participant is None:
            #save the participant ID in session list for now, this is deleted after the session has been started in participant_session-view
            session['begin_with_id'] = form.participant_id.data
            return render_template('consent.html', exp_id=exp_id, experiment_info=experiment_info)

        
    return render_template('admin_dryrun.html', exp_id=exp_id, form=form)



@app.route('/create_task')
def create_task():
    return render_template('create_task.html')


@app.route('/instructions')
def instructions():
    
    participant_id = session['user']
    instructions = experiment.query.filter_by(idexperiment = session['exp_id']).first()
    
    instruction_paragraphs = str(instructions.instruction)
    instruction_paragraphs = instruction_paragraphs.split('<br>')

    
    
    return render_template('instructions.html', instruction_paragraphs=instruction_paragraphs, participant_id=participant_id)


@app.route('/task/<int:page_num>', methods=['GET', 'POST'])
def task(page_num):

    
    experiment_info = experiment.query.filter_by(idexperiment=session['exp_id']).first()
    rating_instruction = experiment_info.single_sentence_instruction
    stimulus_size = experiment_info.stimulus_size
    
    #for text stimuli the size needs to be calculated since the template element utilises h1-h6 tags.
    #A value of stimulus size 12 gives h1 and value of 1 gives h6
    stimulus_size_text = 7-math.ceil((int(stimulus_size)/2))
    
    pages = page.query.filter_by(experiment_idexperiment=session['exp_id']).paginate(per_page=1, page=page_num, error_out=True)
    progress_bar_percentage = round((pages.page/pages.pages)*100)

    #this variable is feeded to the template as empty if trial randomization is set to "off"
    randomized_stimulus = ""



    #if trial randomization is on we will still use the same functionality that is used otherwise
    #but we will pass the randomized pair of the page_id from trial randomization table to the task.html
    if session['randomization'] == 'On':
        
    
        randomized_page_id = trial_randomization.query.filter(and_(trial_randomization.answer_set_idanswer_set==session['answer_set'], trial_randomization.page_idpage==pages.items[0].idpage)).first()
        #answer.query.filter(and_(answer.answer_set_idanswer_set==session['answer_set'], answer.page_idpage==session['current_idpage'])).first()
        #flash("randomized page:")
        #flash(randomized_page_id.randomized_idpage)
        #set the stimulus to be shown if randomization is on
        randomized_stimulus = page.query.filter_by(idpage=randomized_page_id.randomized_idpage).first()
        

        
    for p in pages.items:
        session['current_idpage'] = p.idpage
    
    #slider set
    form = TaskForm(request.form)
    categories_and_scales = {}
    categories = question.query.filter_by(experiment_idexperiment=session['exp_id']).all()

    for cat in categories:    
        
        scale_list = [(cat.left, cat.right)]
        categories_and_scales[cat.idquestion, cat.question]  = scale_list
    
    form.categories1 = categories_and_scales
    

    #slider set form handling
    if request.method == 'POST'and form.validate():
        

        #Lets check if there are answers in database already for this page_id (eg. if user returned to previous page and tried to answer again)
        #If so flash ("Page has been answered already. Answers discarded"), else insert values in to db
        #this has to be done separately for trial randomization "on" and "off" situations        
        
        if session['randomization'] == 'On':
        
            check_answer = answer.query.filter(and_(answer.answer_set_idanswer_set==session['answer_set'], answer.page_idpage==randomized_page_id.randomized_idpage)).first()
        
        if session['randomization'] == 'Off':
        
            check_answer = answer.query.filter(and_(answer.answer_set_idanswer_set==session['answer_set'], answer.page_idpage==session['current_idpage'])).first()
        


        if check_answer is None:
            
            the_time = datetime.now()
            the_time = the_time.replace(microsecond=0)
            
            update_answer_counter = answer_set.query.filter_by(idanswer_set=session['answer_set']).first()
            update_answer_counter.answer_counter = int(update_answer_counter.answer_counter) + 1 
            update_answer_counter.last_answer_time = the_time
        
            #flash("vastauksia:")
            #flash(update_answer_counter.answer_counter)
            db.session.commit()
        
            data = request.form.to_dict()
            for key, value in data.items():
            
                #flash(key)
                #flash(value)
                #flash(session['current_idpage'])
            
            
                #Insert slider values to database
                
                
                #If trial randomization is set to 'Off' the values are inputted for session['current_idpage']
                #Otherwise the values are set for the corresponding id found in the trial randomization table
                
                if session['randomization'] == 'Off':
                
                    participant_answer = answer(question_idquestion=key, answer_set_idanswer_set=session['answer_set'], answer=value, page_idpage=session['current_idpage'])
                    db.session.add(participant_answer)
                    db.session.commit()

                else:

                    participant_answer = answer(question_idquestion=key, answer_set_idanswer_set=session['answer_set'], answer=value, page_idpage=randomized_page_id.randomized_idpage)
                    db.session.add(participant_answer)
                    db.session.commit()
                    

        else:
                flash("Page has been answered already. Answers discarded")
        
        page_num=pages.next_num
        
        if pages.has_next:
            return redirect( url_for('task', page_num=pages.next_num))
        
        return redirect ( url_for('task_completed'))

    
    return render_template('task.html', pages=pages, progress_bar_percentage=progress_bar_percentage, form=form, randomized_stimulus=randomized_stimulus, rating_instruction=rating_instruction, stimulus_size=stimulus_size, stimulus_size_text=stimulus_size_text)



@app.route('/quit_task')
def quit_task():
    
    user_id = session['user']
    session.pop('user', None)
    session.pop('exp_id', None)    
    session.pop('agree', None)
    session.pop('answer_set', None)
    session.pop('type', None)
    
    return render_template('quit_task.html', user_id=user_id)


@app.route('/researcher_login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        #flash("allready logged in")
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user_details = user.query.filter_by(username=form.username.data).first()
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


@app.route('/experiment_statistics')
@login_required
def experiment_statistics():
    
    exp_id = request.args.get('exp_id', None)
    
    experiment_info = experiment.query.filter_by(idexperiment = exp_id).all()
    participants = answer_set.query.filter_by(experiment_idexperiment= exp_id).all()
    
    
    #Rating task headers
    question_headers = question.query.filter_by(experiment_idexperiment=exp_id).all()
    stimulus_headers = page.query.filter_by(experiment_idexperiment=exp_id).all()
    




    pages = page.query.filter_by(experiment_idexperiment=exp_id).all()
    questions = question.query.filter_by(experiment_idexperiment=exp_id).all()
    pages_and_questions = {}

    for p in pages:
        
        questions_list = [(p.idpage, a.idquestion) for a in questions]
        pages_and_questions[p.idpage] = questions_list 



        
    #List of answers per participant in format question Stimulus ID/Question ID
    #those are in answer table as page_idpage and question_idquestion respectively
    
    
    
    """
    pages = page.query.filter_by(experiment_idexperiment=exp_id).all()
    
    participants_and_answers = {}
    
    #participants on kaikki expin osallistujat
    for participant in participants:
 
            
        #kaikki yhden khn vastaukset ko experimentille koska answer_setin id matchaa answereiden kanssa
             
    
        flash(participant.session)
        for p in pages:
        
            answers = answer.query.filter_by(answer_set_idanswer_set=participant.idanswer_set).all()
            #kaikki yhden participantin vastaukset pagelle
            answers_for_page = answer.query.filter(and_(answer.answer_set_idanswer_set==participant.idanswer_set, answer.page_idpage==p.idpage)).all()
            
            
            for ans in answers:
            
                
                
                if ans.page_idpage == p.idpage:
                
                    #flash(ans.page_idpage)
                    flash("X")
                    
                    
                    
                    
                else:
                    
                    flash("NA")
            
            #pages on kaikki experimentin paget
          
                      
            
            for a in answers:

                if p.idpage == a.page_idpage:
                    flash("match")
                
                else:
                    flash("no match")
                 flash("participant:")
                flash(participant.session)
                flash("stimulus:")
                flash(a.page_idpage)
                flash("Kysymys")
                flash(a.question_idquestion)
                flash("vastaus:")
                flash(a.answer)
            
                
                
                
            #answers_list = (a.idanswer, a.question_idquestion, a.answer_set_idanswer_set, a.answer, a.page_idpage)

            #participants_and_answers[participant.session] = answers_list 

    
            """
    
    participants_and_answers = {}
    
    for participant in participants:
 
        answers = answer.query.filter_by(answer_set_idanswer_set=participant.idanswer_set).all()     
        answers_list = [(a.idanswer, a.question_idquestion, a.answer_set_idanswer_set, a.answer, a.page_idpage) for a in answers]    
        participants_and_answers[participant.session] = answers_list 
    
    

    #Background question answers
        
    bg_questions = background_question.query.filter_by(experiment_idexperiment=exp_id).all()
    bg_answers_for_participants = {}

    for participant in participants:
        
        bg_answers = background_question_answer.query.filter_by(answer_set_idanswer_set=participant.idanswer_set).all() 
        bg_answers_list = [(a.answer) for a in bg_answers] 
        bg_answers_for_participants[participant.session] = bg_answers_list 
     

    #started and finished ratings counters    
    started_ratings = answer_set.query.filter_by(experiment_idexperiment=exp_id).count()
    experiment_page_count = page.query.filter_by(experiment_idexperiment=exp_id).count()
    finished_ratings = answer_set.query.filter(and_(answer_set.answer_counter==experiment_page_count, answer_set.experiment_idexperiment==exp_id)).count()
    
    
    
    return render_template('experiment_statistics.html', experiment_info=experiment_info, participants_and_answers=participants_and_answers, pages_and_questions=pages_and_questions, bg_questions=bg_questions, bg_answers_for_participants=bg_answers_for_participants, started_ratings=started_ratings, finished_ratings=finished_ratings, question_headers=question_headers, stimulus_headers=stimulus_headers)



#EDIT FUNCTIONS

@app.route('/create_experiment', methods=['GET', 'POST'])
@login_required
def create_experiment():
    
    form = CreateExperimentForm(request.form)   


    if request.method == 'POST' and form.validate():
        
        
        the_time = datetime.now()
        the_time = the_time.replace(microsecond=0)
        
        new_exp = experiment(name=request.form['name'], instruction=request.form['instruction'], language=request.form['language'], status='Hidden', randomization='Off', single_sentence_instruction=request.form['single_sentence_instruction'], short_instruction=request.form['short_instruction'], creator_name=request.form['creator_name'], is_archived='False', creation_time=the_time, stimulus_size='7', consent_text=request.form['consent_text'], use_forced_id='Off')
        db.session.add(new_exp)
        db.session.commit()        
        
        #flash("lol")
        #flash(new_exp.idexperiment)
        
        exp_id = new_exp.idexperiment

        #data = request.form.to_dict()
        #for key, value in data.items():
            #tähän db insertit

            #flash(key)
            #flash(value)
            #flash('{}'.format(form.name.data))
        
            #Input registration page answers to database
           # participant_background_question_answers = background_question_answer(answer_set_idanswer_set=session['answer_set'], answer=value, background_question_idbackground_question=key)
           # db.session.add(participant_background_question_answers)
           # db.session.commit()

        return redirect(url_for('create_experiment_bgquestions', exp_id=exp_id))

    return render_template('create_experiment.html', form=form)



@app.route('/create_experiment_bgquestions', methods=['GET', 'POST'])
@login_required
def create_experiment_bgquestions():
    
    exp_id = request.args.get('exp_id', None)
    form = CreateBackgroundQuestionForm(request.form)
    
    if request.method == 'POST' and form.validate():
        
        #data = request.form.to_dict()
        
        #flash(data)
        #flash(form.bg_questions_and_options.data)
        

        str = form.bg_questions_and_options.data

        #Split the form data into a list that separates questions followed by the corresponding options
        str_list = str.split('/n')

        #Iterate through the questions and options list
        for a in range(len(str_list)):
        
            #Split the list cells further into questions and options
            list = str_list[a].split(';')
        
            #flash(list[0])
            #flash("id oikein?")
            #flash(add_bgquestion.idbackground_question)
        
        
            #Input the first item of the list as a question in db and the items followed by that as options for that question
            for x in range(len(list)):
            
                if x == 0:
                    #flash("Kysymys")
                    #flash(list[x])
                    add_bgquestion = background_question(background_question=list[x], experiment_idexperiment=exp_id)
                    db.session.add(add_bgquestion)
                    db.session.commit()

                else:
                    #flash("optio")
                    #flash(list[x])
                    add_bgq_option = background_question_option(background_question_idbackground_question=add_bgquestion.idbackground_question, option=list[x])
                    db.session.add(add_bgq_option)
                    db.session.commit()
        
        return redirect(url_for('create_experiment_questions', exp_id=exp_id))    

    return render_template('create_experiment_bgquestions.html', form=form, exp_id=exp_id)


@app.route('/create_experiment_questions', methods=['GET', 'POST'])
@login_required
def create_experiment_questions():
    
    exp_id = request.args.get('exp_id', None)
    
    form = CreateQuestionForm(request.form)
    
    if request.method == 'POST' and form.validate():

        str = form.questions_and_options.data

        str_list = str.split('/n')

        for a in range(len(str_list)): 

            list = str_list[a].split(';')
                     
            #If there are the wrong amount of values for any of the the slider input values
            #redirect back to the form
            if len(list) != 3:
                

                flash("Error Each slider must have 3 parameters separated by ; Some slider has:")
                flash(len(list))
                    
                return redirect(url_for('create_experiment_questions', exp_id=exp_id))

        #If all the slider inputs were of length 3 items
        #we can input them to db
        for a in range(len(str_list)): 

            list = str_list[a].split(';')
       
            #flash("Question:")
            #flash(list[0])
            #flash("Left:")
            #flash(list[1])
            #flash("Right:")
            #flash(list[2])

            add_question = question(experiment_idexperiment=exp_id, question=list[0], left=list[1], right=list[2])
            db.session.add(add_question)
            db.session.commit()
                    
        
        return redirect(url_for('create_experiment_upload_stimuli', exp_id=exp_id))    

    return render_template('create_experiment_questions.html', form=form)


@app.route('/create_experiment_upload_stimuli', methods=['GET', 'POST'])
@login_required
def create_experiment_upload_stimuli():
    
    exp_id = request.args.get('exp_id', None)
    
    form = UploadStimuliForm(request.form)
    
    if request.method == 'POST' and form.validate():
    
        #flash("validated")    
        #flash(form.type.data)
        #flash(form.text.data)
        
        
        #If stimulus type is text lets parse the information and insert it to database
        
        if form.type.data == 'text':
        
            #flash("db insert text")
            
            string = form.text.data
            str_list = string.split('/n')

            for a in range(len(str_list)):

                #flash("lisättiin:")
                #flash(str_list[a])
                add_text_stimulus = page(experiment_idexperiment=exp_id, type='text', text=str_list[a], media='none')
                db.session.add(add_text_stimulus)
                db.session.commit()

                #flash("Succes!")
                
            return redirect(url_for('view_experiment', exp_id=exp_id))  
                
                
        
        else:

            #Upload stimuli into /static/experiment_stimuli/exp_id folder
            #Create the pages for the stimuli by inserting experiment_id, stimulus type, text and names of the stimulus files (as a path to the folder)
            path = 'static/experiment_stimuli/' + str(exp_id)
        
            target = os.path.join(APP_ROOT, path)
            #flash(target)
            
            if not os.path.isdir(target):
                os.mkdir(target)
                #flash("make dir")
        
        
            #This returns a list of filenames: request.files.getlist("file")
        
            for file in request.files.getlist("file"):
            
                #save files in the correct folder
                #flash(file.filename)
                filename = file.filename
                destination = "/".join([target, filename])
                #flash("destination")
                #flash(destination)
                file.save(destination)
                
                #add pages to the db
                db_path = path +  str('/') + str(filename)
                
                #flash("db path")
                #flash(db_path)
                
                new_page = page(experiment_idexperiment=exp_id, type=form.type.data, media=db_path)
                
                db.session.add(new_page)
                db.session.commit()
                
                #flash("Succes!")
                
            return redirect(url_for('view_experiment', exp_id=exp_id))
            
        return redirect(url_for('create_experiment_upload_stimuli', exp_id=exp_id))

    return render_template('create_experiment_upload_stimuli.html', form=form)


@app.route('/view_experiment')
@login_required
def view_experiment():
    
    #crap:3lines
    exp_id = request.args.get('exp_id', None)
    media = page.query.filter_by(experiment_idexperiment=exp_id).all()
    mtype = page.query.filter_by(experiment_idexperiment=exp_id).first()
    
    #experiment info    
    experiment_info = experiment.query.filter_by(idexperiment = exp_id).all()
    
    #background questions
    questions_and_options = {}
    questions = background_question.query.filter_by(experiment_idexperiment=exp_id).all()

    for q in questions:    
    
        options = background_question_option.query.filter_by(background_question_idbackground_question=q.idbackground_question).all()
        options_list = [(o.option, o.idbackground_question_option) for o in options]
        questions_and_options[q.idbackground_question, q.background_question]  = options_list
 
    questions1 = questions_and_options
    
    #sliderset
    categories_and_scales = {}
    categories = question.query.filter_by(experiment_idexperiment=exp_id).all()

    for cat in categories:    
        
        scale_list = [(cat.left, cat.right)]
        categories_and_scales[cat.idquestion, cat.question]  = scale_list
 
    categories1 = categories_and_scales
    
    
    return render_template('view_experiment.html', exp_id=exp_id, media=media, mtype=mtype, experiment_info=experiment_info, categories1=categories1, questions1=questions1)


@app.route('/edit_experiment', methods=['GET', 'POST'])
@login_required
def edit_experiment():

    exp_id = request.args.get('exp_id', None)
        
    current_experiment = experiment.query.filter_by(idexperiment=exp_id).first()
    
    form = EditExperimentForm(request.form, obj=current_experiment)
    form.language.default = current_experiment.language
    
    if request.method == 'POST' and form.validate():
        
        form.populate_obj(current_experiment)
        db.session.commit()
        
        return redirect(url_for('view_experiment', exp_id=exp_id))
    
  
    return render_template('edit_experiment.html', form=form, exp_id=exp_id)





@app.route('/edit_bg_question', methods=['GET', 'POST'])
@login_required
def edit_bg_question():
    
    
    bg_question_id = request.args.get('idbackground_question', None)


    #Search for the right question and for the right options. Form a string of those separated with ";" and insert the
    #formed string into the edit form        
    current_bg_question = background_question.query.filter_by(idbackground_question=bg_question_id).first()
    exp_id=current_bg_question.experiment_idexperiment
    question_string = current_bg_question.background_question
    options  = background_question_option.query.filter_by(background_question_idbackground_question=bg_question_id).all()    
    
    for o in range(len(options)):    
        
        question_string = str(question_string) + str("; ") + str(options[o].option)
    
    form = EditBackgroundQuestionForm(request.form)
    form.bg_questions_and_options.data = question_string

    #After user chooses to update the question and options lets replace the old question and options with the ones from the form
    if request.method == 'POST' and form.validate():

        
        #Explode the string with new values from the form 
        form_values = form.new_values.data
        form_values_list = form_values.split(';')
        
        #Check and remove possible whitespaces from string beginnings with lstrip
        for x in range(len(form_values_list)):
            
            form_values_list[x] = form_values_list[x].lstrip()
        
        #Cycle through strings and update db
        for x in range(len(form_values_list)):
        
            #Replace question and update the object to database
            if x == 0:
                
                
                #flash("delete kys:")
                #flash(current_bg_question.background_question)
                #flash("insert kys:")
                current_bg_question.background_question  = form_values_list[x] 
                #flash(current_bg_question.background_question)
                #flash(current_bg_question.idbackground_question)
                #flash(current_bg_question.experiment_idexperiment)
                
                db.session.commit()
                
                #Delete old options from db
                for o in options:
                    
                    db.session.delete(o)
                    db.session.commit()
            
            #Insert new options to db
            else:
        
               
                #flash("insert opt:")
                #flash(form_values_list[x])
                new_option = background_question_option(background_question_idbackground_question=current_bg_question.idbackground_question, option=form_values_list[x])
                db.session.add(new_option)
                db.session.commit()
        
        
        return redirect(url_for('view_experiment', exp_id=exp_id))
    
  
    return render_template('edit_bg_question.html', form=form, exp_id=exp_id)



@app.route('/edit_question', methods=['GET', 'POST'])
@login_required
def edit_question():
    
    
    question_id = request.args.get('idquestion', None)
    
    current_question = question.query.filter_by(idquestion=question_id).first()
    
    form = EditQuestionForm(request.form, obj=current_question)
    
    
    if request.method == 'POST' and form.validate():
        
        form.populate_obj(current_question)
        db.session.commit()
        
        return redirect(url_for('view_experiment', exp_id=current_question.experiment_idexperiment))
  
    return render_template('edit_question.html', form=form)



@app.route('/add_bg_question', methods=['GET', 'POST'])
@login_required
def add_bg_question():
    
    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('view_experiment', exp_id=exp_id))
        
    else:

        
        
        form = CreateBackgroundQuestionForm(request.form)
        
        if request.method == 'POST' and form.validate():
            
            str = form.bg_questions_and_options.data
    
            #Split the form data into a list that separates questions followed by the corresponding options
            str_list = str.split('/n')
    
            #Iterate through the questions and options list
            for a in range(len(str_list)):
            
                #Split the list cells further into questions and options
                list = str_list[a].split(';')
            
                #Input the first item of the list as a question in db and the items followed by that as options for that question
                for x in range(len(list)):
                
                    if x == 0:
                        #flash("Kysymys")
                        #flash(list[x])
                        add_bgquestion = background_question(background_question=list[x], experiment_idexperiment=exp_id)
                        db.session.add(add_bgquestion)
                        db.session.commit()
    
                    else:
                        #flash("optio")
                        #flash(list[x])
                        add_bgq_option = background_question_option(background_question_idbackground_question=add_bgquestion.idbackground_question, option=list[x])
                        db.session.add(add_bgq_option)
                        db.session.commit()
            
            return redirect(url_for('view_experiment', exp_id=exp_id))    
    
        return render_template('add_bg_question.html', form=form)



@app.route('/add_questions', methods=['GET', 'POST'])
@login_required
def add_questions():
    
    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('view_experiment', exp_id=exp_id))
        
    else:
    
        form = CreateQuestionForm(request.form)
        
        if request.method == 'POST' and form.validate():
    
            str = form.questions_and_options.data
            str_list = str.split('/n')
    
            for a in range(len(str_list)): 
    
                list = str_list[a].split(';')
                         
                #If there are the right amount of values for the slider input values
                if len(list) == 3:
                    
                    #flash("Question:")
                    #flash(list[0])
                    #flash("Left:")
                    #flash(list[1])
                    #flash("Right:")
                    #flash(list[2])
    
                    add_question = question(experiment_idexperiment=exp_id, question=list[0], left=list[1], right=list[2])
                    db.session.add(add_question)
                    db.session.commit()
                        
                    #If slider has too many or too litlle parameters give an error and redirect back to input form
                else:
                    flash("Error Each slider must have 3 parameters separated by ; Some slider has:")
                    flash(len(list))
                        
                    return redirect(url_for('create_experiment_questions', exp_id=exp_id))
            
            return redirect(url_for('view_experiment', exp_id=exp_id))    
    
        return render_template('add_questions.html', form=form)



#Remove functions
    

@app.route('/remove_bg_question')
@login_required
def remove_bg_question():

    exp_id = request.args.get('exp_id', None)


    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('view_experiment', exp_id=exp_id))
        
    else:
        
    
        remove_id = request.args.get('idbackground_question', None)
        
        remove_options = background_question_option.query.filter_by(background_question_idbackground_question=remove_id).all()
        
        for a in range(len(remove_options)): 
            
            #flash(remove_options[a].idbackground_question_option)
        
            db.session.delete(remove_options[a])
            db.session.commit()
    
            
        remove_question = background_question.query.filter_by(idbackground_question=remove_id).first()
        
        db.session.delete(remove_question)
        db.session.commit()
  
    return redirect(url_for('view_experiment', exp_id=exp_id))




@app.route('/remove_question')
@login_required
def remove_question():

    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('view_experiment', exp_id=exp_id))
        
    else:


        remove_id = request.args.get('idquestion', None)
        remove_question = question.query.filter_by(idquestion=remove_id).first()
        
        db.session.delete(remove_question)
        db.session.commit()
  
    return redirect(url_for('view_experiment', exp_id=exp_id))


@app.route('/remove_experiment', methods=['GET', 'POST'])
@login_required
def remove_experiment():

    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('view_experiment', exp_id=exp_id))
        
    else:

    
    
        form = RemoveExperimentForm(request.form)
        
        if request.method == 'POST' and form.validate():
    
            if form.remove.data == 'DELETE':
    
                
                #This removes all experiment data from the database!
                
                
                #Remove research bulletin if it exists
                empty_filevariable = experiment.query.filter_by(idexperiment=exp_id).first()
    
                if empty_filevariable.research_notification_filename is not None:
    
                    target = os.path.join(APP_ROOT, empty_filevariable.research_notification_filename)
                    
                    if os.path.exists(target):                   
                        os.remove(target)
                
                
 
                
                #Tables
                
                
                remove_forced_id = forced_id.query.filter_by(experiment_idexperiment=exp_id).all()
                
                for b in range(len(remove_forced_id)):
                    db.session.delete(remove_forced_id[b])
                    db.session.commit()

                
                #background_question_option & background_question & background question answers:
                remove_background_question = background_question.query.filter_by(experiment_idexperiment=exp_id).all()
                
                #cycle through all bg questions and delete their options
                for a in range(len(remove_background_question)):
                
                    remove_background_question_option = background_question_option.query.filter_by(background_question_idbackground_question=remove_background_question[a].idbackground_question).all() 
                
                    for b in range(len(remove_background_question_option)):
                        
                        db.session.delete(remove_background_question_option[b])
                        db.session.commit()
                
                
                #Remove all background questions and all answers given to each bg question
                for a in range(len(remove_background_question)):
                    
                    remove_background_question_answers = background_question_answer.query.filter_by(background_question_idbackground_question=remove_background_question[a].idbackground_question).all()
                    
                    for b in range(len(remove_background_question_answers)):
                        
                        db.session.delete(remove_background_question_answers[b])
                        db.session.commit()
                    
                    db.session.delete(remove_background_question[a])
                    db.session.commit()
                    
    
               
                #Remove all questions and answers 
                remove_question = question.query.filter_by(experiment_idexperiment=exp_id).all()
               
                for a in range(len(remove_question)):
                    
                    remove_question_answers = answer.query.filter_by(question_idquestion=remove_question[a].idquestion).all()
                    
                    for b in range(len(remove_question_answers)):
                        
                        db.session.delete(remove_question_answers[b])
                        db.session.commit()
                    
                    db.session.delete(remove_question[a])
                    db.session.commit()
               
               
                #Remove all pages and datafiles
                remove_pages = page.query.filter_by(experiment_idexperiment=exp_id).all()
                
                for a in range(len(remove_pages)):
                
                    if remove_pages[a].type == 'text':
                        
                        db.session.delete(remove_pages[a])
                        db.session.commit()
                        
                    else:
                        
                        target = os.path.join(APP_ROOT, remove_pages[a].media)
    
                        if os.path.exists(target):                   
                            os.remove(target)
        
                    #Now that the files are removed we can delete the page
                    db.session.delete(remove_pages[a])
                    db.session.commit()
                    
                    
                #Remove all answer_sets and trial_randomization orders
                remove_answer_set = answer_set.query.filter_by(experiment_idexperiment=exp_id).all()
                
                for a in range(len(remove_answer_set)):
                    
                    remove_trial_randomizations = trial_randomization.query.filter_by(answer_set_idanswer_set=remove_answer_set[a].idanswer_set).all()
                    
                    for b in range(len(remove_trial_randomizations)):
                        
                        db.session.delete(remove_trial_randomizations[b])
                        db.session.commit()
                    
                    db.session.delete(remove_answer_set[a])
                    db.session.commit()
    
                
                #Remove experiment table
                remove_experiment = experiment.query.filter_by(idexperiment=exp_id).first()
                db.session.delete(remove_experiment)
                db.session.commit()
                
                
                flash("Experiment was removed from database!")
                
                return redirect(url_for('index'))
                
            else:
                
                flash("Experiment was not removed!")
                
                return redirect(url_for('view_experiment', exp_id=exp_id))
                
    
        
        return render_template('remove_experiment.html', form=form, exp_id=exp_id)



@app.route('/remove_page')
@login_required
def remove_page():

    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('view_experiment', exp_id=exp_id))
        
    else:

    
        remove_id = request.args.get('idpage', None)
        remove_page = page.query.filter_by(idpage=remove_id).first()
        experiment_pages = page.query.filter_by(experiment_idexperiment=exp_id).all()
        
        #if stimulustype is text, the stimulus itself is text on the database, other stimulus types are real files
        #on the server and need to be deleted    
        if remove_page.type != 'text':
            
            #helper variable
            do_not_delete_file = 'False'
                
            #if the file to be deleted is in duplicate use of another page then we won't delete the file
            for a in range(len(experiment_pages)):
    
                #flash("in da for")
                    
                if experiment_pages[a].media == remove_page.media and experiment_pages[a].idpage != remove_page.idpage:
    
                    #flash("in da if")
                    do_not_delete_file = 'True'
    
            #If no other page is using the file then lets remove it
            if do_not_delete_file == 'False':
                #remove old file            
                target = os.path.join(APP_ROOT, remove_page.media)
                #flash("Remove:")
                #flash(target)
                os.remove(target)
        
            db.session.delete(remove_page)
            db.session.commit()
      
            return redirect(url_for('view_experiment', exp_id=exp_id))
        
        if remove_page.type == 'text':
            
            db.session.delete(remove_page)
            db.session.commit()
            
            return redirect(url_for('view_experiment', exp_id=exp_id))
        
        return redirect(url_for('view_experiment', exp_id=exp_id))


@app.route('/publish_experiment')
@login_required
def publish_experiment():

    exp_id = request.args.get('exp_id', None)
        
    publish_experiment = experiment.query.filter_by(idexperiment = exp_id).first()
    
    publish_experiment.status = 'Public'
    
    flash("Changed status to Public")
    
    db.session.commit()
  
    return redirect(url_for('view_experiment', exp_id=exp_id))


@app.route('/hide_experiment')
@login_required
def hide_experiment():

    exp_id = request.args.get('exp_id', None)
        
    hide_experiment = experiment.query.filter_by(idexperiment = exp_id).first()
    
    hide_experiment.status = 'Hidden'
    
    flash("Changed status to Hidden")
    
    db.session.commit()
  
    return redirect(url_for('view_experiment', exp_id=exp_id))


@app.route('/private_experiment')
@login_required
def private_experiment():

    exp_id = request.args.get('exp_id', None)
        
    private_experiment = experiment.query.filter_by(idexperiment = exp_id).first()
    
    private_experiment.status = 'Private'
    
    flash("Changed status to Private")
    
    db.session.commit()
  
    return redirect(url_for('view_experiment', exp_id=exp_id))



@app.route('/enable_randomization')
@login_required
def enable_randomization():

    exp_id = request.args.get('exp_id', None)
        
    enable_randomization = experiment.query.filter_by(idexperiment = exp_id).first()
    
    enable_randomization.randomization = 'On'
    
    flash("Enabled trial randomization")
    
    db.session.commit()
  
    return redirect(url_for('view_experiment', exp_id=exp_id))


@app.route('/disable_randomization')
@login_required
def disable_randomization():

    exp_id = request.args.get('exp_id', None)
        
    disable_randomization = experiment.query.filter_by(idexperiment = exp_id).first()
    
    disable_randomization.randomization = 'Off'
    
    flash("Disabled trial randomization")
    
    db.session.commit()
  
    return redirect(url_for('view_experiment', exp_id=exp_id))


@app.route('/enable_forced_id')
@login_required
def enable_forced_id():

    exp_id = request.args.get('exp_id', None)
        
    enable_forced_id = experiment.query.filter_by(idexperiment = exp_id).first()
    
    enable_forced_id.use_forced_id = 'On'
    
    flash("Enabled forced ID login")
    
    db.session.commit()
  
    return redirect(url_for('view_experiment', exp_id=exp_id))


@app.route('/disable_forced_id')
@login_required
def disable_forced_id():

    exp_id = request.args.get('exp_id', None)
        
    disable_forced_id = experiment.query.filter_by(idexperiment = exp_id).first()
    
    disable_forced_id.use_forced_id = 'Off'
    
    flash("Disabled forced ID login")
    
    db.session.commit()
  
    return redirect(url_for('view_experiment', exp_id=exp_id))


@app.route('/view_forced_id_list', methods=['GET', 'POST'])
@login_required
def view_forced_id_list():

    exp_id = request.args.get('exp_id', None)
    
    id_list = forced_id.query.filter_by(experiment_idexperiment=exp_id).all()
    
    
    form = GenerateIdForm(request.form)
        
    if request.method == 'POST' and form.validate():

        
        for i in range(int(request.form['number'])): 
        
            random_id = str(request.form['string']) + str(secrets.token_hex(3))
            check_answer_set = answer_set.query.filter_by(session=random_id).first()
            check_forced_id = forced_id.query.filter_by(pregenerated_id=random_id).first()
            
            
            #here we check if the generated id is found from given answers from the whole database in answer_set table
            #or from forced_id table. If so another id is generated instead to avoid a duplicate
            if check_answer_set is not None or check_forced_id is not None:
            
                #flash("ID already existed; generated a new one")
                random_id = secrets.token_hex(3)
                check_answer_set = answer_set.query.filter_by(session=random_id).first()
                check_forced_id = forced_id.query.filter_by(pregenerated_id=random_id).first()   
                
            input_id = forced_id(experiment_idexperiment=exp_id, pregenerated_id=random_id)
            db.session.add(input_id)
            db.session.commit()
        

        

        return redirect(url_for('view_forced_id_list', exp_id=exp_id))
    
    
    
    
    
    
  
    return render_template('view_forced_id_list.html', exp_id=exp_id, id_list=id_list)










@app.route('/edit_stimuli', methods=['GET', 'POST'])
@login_required
def edit_stimuli():

    exp_id = request.args.get('exp_id', None)
    page_id = request.args.get('idpage', None)
    edit_page = page.query.filter_by(idpage=page_id).first()
    
    
    
    form = EditPageForm(request.form, obj=edit_page)
    
    if request.method == 'POST' and form.validate():
        

        #If the stimulus type is not text, then the old stimulus file is deleted from os and replaced
        if edit_page.type != 'text':

            #remove old file            
            target = os.path.join(APP_ROOT, edit_page.media)
            #flash("Remove:")
            #flash(target)
            os.remove(target)

            #upload new file
            
            path = 'static/experiment_stimuli/' + str(exp_id)
        
            target = os.path.join(APP_ROOT, path)
            #flash(target)
            
            if not os.path.isdir(target):
                os.mkdir(target)
                #flash("make dir")
        
        
            #This returns a list of filenames: request.files.getlist("file")
        
            for file in request.files.getlist("file"):
            
                #save files in the correct folder
                #flash(file.filename)
                filename = file.filename
                destination = "/".join([target, filename])
                #flash("destination")
                #flash(destination)
                file.save(destination)
                
                #update db object
                db_path = path +  str('/') + str(filename)
                
                #flash("db path")
                #flash(db_path)
                
                edit_page.media=db_path
                                
                db.session.commit()
                
                #flash("Succes!")

            
        #If editing text stimulus no need for filehandling    
        else:

             form.populate_obj(edit_page)
             db.session.commit()
                           
            
        
        return redirect(url_for('view_experiment', exp_id=exp_id))
  
    return render_template('edit_stimuli.html', form=form, edit_page=edit_page)


@app.route('/add_stimuli', methods=['GET', 'POST'])
@login_required
def add_stimuli():

    exp_id = request.args.get('exp_id', None)
    
    
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    
    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('view_experiment', exp_id=exp_id))
        
    else:


        #If there are no pages set for the experiment lets reroute user to create experiment stimuli upload instead
    
        is_there_any_stimuli = page.query.filter_by(experiment_idexperiment = exp_id).first()
    
        if is_there_any_stimuli is None:
        
            return redirect(url_for('create_experiment_upload_stimuli', exp_id=exp_id))

        
        
        stimulus_type = request.args.get('stimulus_type', None)
           
        form = UploadStimuliForm(request.form)
    
        if request.method == 'POST':
        
            
            if stimulus_type == 'text':
            
                #flash("db insert text")
                
                string = form.text.data
                str_list = string.split('/n')
    
                for a in range(len(str_list)):
    
                    #flash("lisättiin:")
                    #flash(str_list[a])
                    add_text_stimulus = page(experiment_idexperiment=exp_id, type='text', text=str_list[a], media='none')
                    db.session.add(add_text_stimulus)
                    db.session.commit()
    
                    #flash("Succes!")
                    
                return redirect(url_for('view_experiment', exp_id=exp_id))  
                    
                    
            
            else:
    
                #Upload stimuli into /static/experiment_stimuli/exp_id folder
                #Create the pages for the stimuli by inserting experiment_id, stimulus type, text and names of the stimulus files (as a path to the folder)
                path = 'static/experiment_stimuli/' + str(exp_id)
            
                target = os.path.join(APP_ROOT, path)
                #flash(target)
                
                if not os.path.isdir(target):
                    os.mkdir(target)
                    #flash("make dir")
            
            
                #This returns a list of filenames: request.files.getlist("file")
            
                for file in request.files.getlist("file"):
                
                    #save files in the correct folder
                    #flash(file.filename)
                    filename = file.filename
                    destination = "/".join([target, filename])
                    #flash("destination")
                    #flash(destination)
                    file.save(destination)
                    
                    #add pages to the db
                    db_path = path +  str('/') + str(filename)
                    
                    #flash("db path")
                    #flash(db_path)
                    
                    new_page = page(experiment_idexperiment=exp_id, type=form.type.data, media=db_path)
                    
                    db.session.add(new_page)
                    db.session.commit()
                    
                    #flash("Succes!")
                    
                return redirect(url_for('view_experiment', exp_id=exp_id))
                
            return redirect(url_for('view_experiment', exp_id=exp_id))
            
      
        return render_template('add_stimuli.html', form=form, stimulus_type=stimulus_type)



@app.route('/upload_research_notification', methods=['GET', 'POST'])
@login_required
def upload_research_notification():
    
    exp_id = request.args.get('exp_id', None)
    
    form = UploadResearchBulletinForm(request.form)
    
    if request.method == 'POST':

        path = 'static/experiment_stimuli/' + str(exp_id)
            
        target = os.path.join(APP_ROOT, path)
        #flash(target)
                
        if not os.path.isdir(target):
            os.mkdir(target)
            #flash("make dir")
            
            
        #This returns a list of filenames: request.files.getlist("file")
    
        for file in request.files.getlist("file"):
        
            #save files in the correct folder
            #flash(file.filename)
            filename = file.filename
            destination = "/".join([target, filename])
            #flash("destination")
            #flash(destination)
            file.save(destination)
            
            #add pages to the db
            db_path = path +  str('/') + str(filename)
            
            #flash("db path")
            #flash(db_path)
            
            
            bulletin = experiment.query.filter_by(idexperiment=exp_id).first()
            
            bulletin.research_notification_filename = db_path
            db.session.commit()
            
            #flash("Succes!")
            
        return redirect(url_for('view_experiment', exp_id=exp_id))

    
    return render_template('upload_research_notification.html', exp_id=exp_id, form=form)


@app.route('/remove_research_notification')
@login_required
def remove_research_notification():
    
    exp_id = request.args.get('exp_id', None)
    
    empty_filevariable = experiment.query.filter_by(idexperiment=exp_id).first()
    
    target = os.path.join(APP_ROOT, empty_filevariable.research_notification_filename)
    
    if os.path.exists(target):                   
        os.remove(target)
 
    
    empty_filevariable.research_notification_filename = None
    
    db.session.commit()
    
    return redirect(url_for('view_experiment', exp_id=exp_id))



@app.route('/view_research_notification')
def view_research_notification():
    
    exp_id = request.args.get('exp_id', None)
    image = experiment.query.filter_by(idexperiment=exp_id).first()
    
    research_notification_filename = image.research_notification_filename
    
    return render_template('view_research_notification.html', research_notification_filename=research_notification_filename)






@app.route('/download_csv')
@login_required
def download_csv():

    exp_id = request.args.get('exp_id', None)
    
    """
    with open('export_new.csv', 'w', newline='') as f:
        
        thewriter = csv.writer(f)
        
        thewriter.writerow(['1','2','3','4'])
        thewriter.writerow(['a','b','c','d'])
    """
    
    
    
    return redirect(url_for('experiment_statistics', exp_id=exp_id))


@app.route('/researcher_info')
@login_required
def researcher_info():

  
    return render_template('researcher_info.html')





#TEST PAGE
    
@app.route('/test_page')
def test_page():

    flash('Please log in to access this page.')
    
    session.clear()
  
    return render_template('test_page.html')

