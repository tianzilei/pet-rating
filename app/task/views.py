


import math
from datetime import datetime

from flask import (
    Flask, 
    render_template, 
    request, 
    session, 
    flash, 
    redirect, 
    url_for, 
    Blueprint
)

from sqlalchemy import and_ 
from flask_babel import _, lazy_gettext as _l

from app import db
from app.models import experiment
from app.models import page, question
from app.models import answer_set, answer 
from app.models import user, trial_randomization
from app.forms import Answers, TaskForm, ContinueTaskForm

task_blueprint = Blueprint("task", __name__, 
                template_folder='templates',
                static_folder='static',
                url_prefix='/task')


def get_randomized_page(pages):

    #this variable is feeded to the template as empty if trial randomization is set to "off"
    randomized_stimulus = ""

    #if trial randomization is on we will still use the same functionality that is used otherwise
    #but we will pass the randomized pair of the page_id from trial randomization table to the task.html
    randomized_page_id = trial_randomization.query.filter(and_(
            trial_randomization.answer_set_idanswer_set==session['answer_set'], 
            trial_randomization.page_idpage==pages.items[0].idpage
        )).first()

    return randomized_page_id


def add_slider_answer(key, value, randomized_page_id):
    '''Insert slider value to database. If trial randomization is set to 'Off' 
    the values are inputted for session['current_idpage']. Otherwise the values 
    are set for the corresponding id found in the trial randomization table'''

    page_idpage = session['current_idpage'] if session['randomization'] == 'Off' else randomized_page_id.randomized_idpage 
    participant_answer = answer(question_idquestion=key, answer_set_idanswer_set=session['answer_set'], answer=value, page_idpage=page_idpage)
    db.session.add(participant_answer)
    db.session.commit()


@task_blueprint.route('/<int:page_num>', methods=['POST'])
def task_answer(page_num):

    form = TaskForm(request.form)
    pages = page.query.filter_by(experiment_idexperiment=session['exp_id']).paginate(per_page=1, page=page_num, error_out=True)

    # TODO: determine wheter handling POST data from slider or embody!!!

    if form.validate():
        #Lets check if there are answers in database already for this page_id (eg. if user returned to previous page and tried to answer again)
        #If so flash ("Page has been answered already. Answers discarded"), else insert values in to db
        #this has to be done separately for trial randomization "on" and "off" situations        

        if session['randomization'] == 'On':
            randomized_page_id = get_randomized_page(pages)
            check_answer = answer.query.filter(and_(answer.answer_set_idanswer_set==session['answer_set'], answer.page_idpage==randomized_page_id.randomized_idpage)).first()
        else:
            check_answer = answer.query.filter(and_(answer.answer_set_idanswer_set==session['answer_set'], answer.page_idpage==session['current_idpage'])).first()

        if check_answer is None:
            the_time = datetime.now()
            the_time = the_time.replace(microsecond=0)
            
            update_answer_counter = answer_set.query.filter_by(idanswer_set=session['answer_set']).first()
            update_answer_counter.answer_counter = int(update_answer_counter.answer_counter) + 1 
            update_answer_counter.last_answer_time = the_time
            db.session.commit()
        
            data = request.form.to_dict()
            for key, value in data.items():
                add_slider_answer(key, value, randomized_page_id)

        else:
            flash("Page has been answered already. Answers discarded")
        
        page_num=pages.next_num
        
        if not pages.has_next:
            return redirect ( url_for('task.completed'))

    return redirect( url_for('task.task', page_num=pages.next_num))


@task_blueprint.route('/<int:page_num>', methods=['GET'])
def task(page_num):

    experiment_info = experiment.query.filter_by(idexperiment=session['exp_id']).first()
    rating_instruction = experiment_info.single_sentence_instruction
    stimulus_size = experiment_info.stimulus_size
    
    #for text stimuli the size needs to be calculated since the template element utilises h1-h6 tags.
    #A value of stimulus size 12 gives h1 and value of 1 gives h6
    stimulus_size_text = 7-math.ceil((int(stimulus_size)/2))

    print(stimulus_size_text)
    
    pages = page.query.filter_by(experiment_idexperiment=session['exp_id']).paginate(per_page=1, page=page_num, error_out=True)
    progress_bar_percentage = round((pages.page/pages.pages)*100)

    #this variable is feeded to the template as empty if trial randomization is set to "off"
    randomized_stimulus = ""

    # if trial randomization is on we will still use the same functionality that is used otherwise
    # but we will pass the randomized pair of the page_id from trial randomization table to the task.html
    if session['randomization'] == 'On':

        #set the stimulus to be shown if randomization is on
        randomized_page_id = get_randomized_page(pages)
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

    return render_template(
                        'task.html', 
                        pages=pages, 
                        progress_bar_percentage=progress_bar_percentage, 
                        form=form, 
                        randomized_stimulus=randomized_stimulus, 
                        rating_instruction=rating_instruction, 
                        stimulus_size=stimulus_size, 
                        stimulus_size_text=stimulus_size_text
                        )


@task_blueprint.route('/completed')
def completed():
    
    session.pop('user', None)
    session.pop('exp_id', None)    
    session.pop('agree', None)
    session.pop('answer_set', None)
    session.pop('type', None)
    session.pop('randomization', None)

    return render_template('task_completed.html')


@task_blueprint.route('/continue', methods=['GET', 'POST'])
def continue_task():
    
    exp_id = request.args.get('exp_id', None)
    form = ContinueTaskForm()
    
    if form.validate_on_submit():
        
        #check if participant ID is found from db and that the answer set is linked to the correct experiment
        participant = answer_set.query.filter(and_(answer_set.session==form.participant_id.data, answer_set.experiment_idexperiment==exp_id)).first()
        if participant is None:
            flash('Invalid ID')
            return redirect(url_for('task.continue_task', exp_id=exp_id))        
        
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
            
            return redirect( url_for('task.completed'))
        
        return redirect( url_for('task.task', page_num=redirect_to_page))
        
    return render_template('continue_task.html', exp_id=exp_id, form=form)


@task_blueprint.route('/quit')
def quit():
    
    user_id = session['user']
    session.pop('user', None)
    session.pop('exp_id', None)    
    session.pop('agree', None)
    session.pop('answer_set', None)
    session.pop('type', None)
    
    return render_template('quit_task.html', user_id=user_id)


# TODO: removable?
@task_blueprint.route('/create')
def create():
    return render_template('create_task.html')


