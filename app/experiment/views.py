

import os
import secrets

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

from wtforms import Form
from sqlalchemy import and_, update
from flask_login import login_required

from app import app, db 
from app.routes import APP_ROOT
from app.models import background_question, experiment
from app.models import background_question_answer
from app.models import page, question
from app.models import background_question_option
from app.models import answer_set, answer, forced_id
from app.models import user, trial_randomization
from app.forms import (
    CreateBackgroundQuestionForm, 
    CreateQuestionForm, UploadStimuliForm, EditBackgroundQuestionForm, 
    EditQuestionForm, EditExperimentForm, UploadResearchBulletinForm, 
    EditPageForm, RemoveExperimentForm, GenerateIdForm
)

#Stimuli upload folder setting
#APP_ROOT = os.path.dirname(os.path.abspath(__file__))

experiment_blueprint = Blueprint("experiment", __name__, 
                template_folder='templates',
                #static_folder='static',
                url_prefix='/experiment')


@experiment_blueprint.route('/view')
@login_required
def view():
    
    #crap:3lines
    exp_id = request.args.get('exp_id', None)
    media = page.query.filter_by(experiment_idexperiment=exp_id).all()

    ## TODO: mtype can be multiple!
    ## is this even necessary anymore?
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


# Experiment info:

@experiment_blueprint.route('/remove', methods=['GET', 'POST'])
@login_required
def remove():

    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")
        return redirect(url_for('experiment.view', exp_id=exp_id))
        
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
                return redirect(url_for('experiment.view', exp_id=exp_id))
        
        return render_template('remove_experiment.html', form=form, exp_id=exp_id)


@experiment_blueprint.route('/publish')
@login_required
def publish():
    exp_id = request.args.get('exp_id', None)
    publish_experiment = experiment.query.filter_by(idexperiment = exp_id).first()
    publish_experiment.status = 'Public'
    flash("Changed status to Public")
    db.session.commit()
    return redirect(url_for('experiment.view', exp_id=exp_id))


@experiment_blueprint.route('/hide')
@login_required
def hide():
    exp_id = request.args.get('exp_id', None)
    hide_experiment = experiment.query.filter_by(idexperiment = exp_id).first()
    hide_experiment.status = 'Hidden'
    flash("Changed status to Hidden")
    db.session.commit()
    return redirect(url_for('experiment.view', exp_id=exp_id))


@experiment_blueprint.route('/private')
@login_required
def private():
    exp_id = request.args.get('exp_id', None)
    private_experiment = experiment.query.filter_by(idexperiment = exp_id).first()
    private_experiment.status = 'Private'
    flash("Changed status to Private")
    db.session.commit()
    return redirect(url_for('experiment.view', exp_id=exp_id))


@experiment_blueprint.route('/randomization')
@login_required
def randomization():
    exp_id = request.args.get('exp_id', None)
    status = request.args.get('set')

    if status == 'On':
        flash("Enabled trial randomization")
    elif status == 'Off':
        flash("Disabled trial randomization")

    experiment.query.filter_by(idexperiment = exp_id).first().randomization = status
    db.session.commit()
  
    return redirect(url_for('experiment.view', exp_id=exp_id))


@experiment_blueprint.route('/set_forced_id')
@login_required
def set_forced_id():
    '''By using forced ID login subjects can only participate to a rating task
    by logging in with a pregenerated ID.'''

    exp_id = request.args.get('exp_id', None)
    status = request.args.get('set')

    if status == 'On':
        flash("Enabled forced ID login")
    elif status == 'Off':
        flash("Disabled forced ID login")

    experiment.query.filter_by(idexperiment = exp_id).first().use_forced_id = status
    db.session.commit()
  
    return redirect(url_for('experiment.view', exp_id=exp_id))


@experiment_blueprint.route('/view_forced_id_list', methods=['GET', 'POST'])
@login_required
def view_forced_id_list():
    '''Forced ID login for participants'''

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


@experiment_blueprint.route('/upload_research_notification', methods=['GET', 'POST'])
@login_required
def upload_research_notification():
    '''Upload research bulletin'''

    exp_id = request.args.get('exp_id', None)
    form = UploadResearchBulletinForm(request.form)
    
    if request.method == 'POST':
        path = 'static/experiment_stimuli/' + str(exp_id)
        target = os.path.join(APP_ROOT, path)
                
        if not os.path.isdir(target):
            os.mkdir(target)
            
        #This returns a list of filenames: request.files.getlist("file")
        for file in request.files.getlist("file"):
            #save files in the correct folder
            filename = file.filename
            destination = "/".join([target, filename])
            file.save(destination)
            
            #add pages to the db
            db_path = path +  str('/') + str(filename)
            bulletin = experiment.query.filter_by(idexperiment=exp_id).first()
            bulletin.research_notification_filename = db_path
            db.session.commit()
            
        return redirect(url_for('experiment.view', exp_id=exp_id))

    return render_template('upload_research_notification.html', exp_id=exp_id, form=form)


@experiment_blueprint.route('/remove_research_notification')
@login_required
def remove_research_notification():
    '''Remove research bulletin'''
    
    exp_id = request.args.get('exp_id', None)
    empty_filevariable = experiment.query.filter_by(idexperiment=exp_id).first()
    target = os.path.join(APP_ROOT, empty_filevariable.research_notification_filename)
    
    if os.path.exists(target):                   
        os.remove(target)
    
    empty_filevariable.research_notification_filename = None
    db.session.commit()
    
    return redirect(url_for('experiment.view', exp_id=exp_id))


@experiment_blueprint.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    '''Edit experiment details'''

    exp_id = request.args.get('exp_id', None)
    current_experiment = experiment.query.filter_by(idexperiment=exp_id).first()
    
    form = EditExperimentForm(request.form, obj=current_experiment)
    form.language.default = current_experiment.language
    
    if request.method == 'POST' and form.validate():
        
        form.populate_obj(current_experiment)
        db.session.commit()
        
        return redirect(url_for('experiment.view', exp_id=exp_id))
    
    return render_template('edit_experiment.html', form=form, exp_id=exp_id)





# Background questions:

@experiment_blueprint.route('/add_bg_question', methods=['GET', 'POST'])
@login_required
def add_bg_question():
    
    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('experiment.view', exp_id=exp_id))
        
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
            
            return redirect(url_for('experiment.view', exp_id=exp_id))    
    
        return render_template('add_bg_question.html', form=form)


@experiment_blueprint.route('/edit_bg_question', methods=['GET', 'POST'])
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
        
        return redirect(url_for('experiment.view', exp_id=exp_id))
    
    return render_template('edit_bg_question.html', form=form, exp_id=exp_id)


@experiment_blueprint.route('/remove_bg_question')
@login_required
def remove_bg_question():

    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('experiment.view', exp_id=exp_id))
        
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
  
    return redirect(url_for('experiment.view', exp_id=exp_id))






# Rating set:

@experiment_blueprint.route('/set_embody')
@login_required
def set_embody():
    '''Enable/disable embody tool'''
    
    exp_id = request.args.get('exp_id', None)
    
    exp = experiment.query.filter_by(idexperiment = exp_id).first()
    exp.embody_enabled = (True if exp.embody_enabled == False else False)
    db.session.commit() 
    
    return redirect(url_for('experiment.view', exp_id=exp_id))


@experiment_blueprint.route('/add_questions', methods=['GET', 'POST'])
@login_required
def add_questions():
    
    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('experiment.view', exp_id=exp_id))
        
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
                        
                    return redirect(url_for('create.experiment_questions', exp_id=exp_id))
            
            return redirect(url_for('experiment.view', exp_id=exp_id))    
    
        return render_template('add_questions.html', form=form)


@experiment_blueprint.route('/edit_question', methods=['GET', 'POST'])
@login_required
def edit_question():
    
    question_id = request.args.get('idquestion', None)
    current_question = question.query.filter_by(idquestion=question_id).first()
    form = EditQuestionForm(request.form, obj=current_question)
    
    if request.method == 'POST' and form.validate():
        
        form.populate_obj(current_question)
        db.session.commit()
        
        return redirect(url_for('experiment.view', exp_id=current_question.experiment_idexperiment))
  
    return render_template('edit_question.html', form=form)


@experiment_blueprint.route('/remove_question')
@login_required
def remove_question():

    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
        flash("Experiment is public. Cannot modify structure.")
        return redirect(url_for('experiment.view', exp_id=exp_id))
        
    else:

        remove_id = request.args.get('idquestion', None)
        remove_question = question.query.filter_by(idquestion=remove_id).first()
        
        db.session.delete(remove_question)
        db.session.commit()
  
    return redirect(url_for('experiment.view', exp_id=exp_id))





# Stimuli:

@experiment_blueprint.route('/add_stimuli', methods=['GET', 'POST'])
@login_required
def add_stimuli():

    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()
    
    if exp_status.status != 'Hidden':
        flash("Experiment is public. Cannot modify structure.")
        return redirect(url_for('experiment.view', exp_id=exp_id))
    else:
        #If there are no pages set for the experiment lets reroute user to create experiment stimuli upload instead
    
        is_there_any_stimuli = page.query.filter_by(experiment_idexperiment = exp_id).first()
    
        if is_there_any_stimuli is None:
            return redirect(url_for('create.experiment_upload_stimuli', exp_id=exp_id))
        
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
                    
                return redirect(url_for('experiment.view', exp_id=exp_id))  
            
            else:
                #Upload stimuli into /static/experiment_stimuli/exp_id folder
                #Create the pages for the stimuli by inserting experiment_id, stimulus type, text and names of the stimulus files (as a path to the folder)
                path = 'static/experiment_stimuli/' + str(exp_id)
                target = os.path.join(APP_ROOT, path)
                
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
                    
                return redirect(url_for('experiment.view', exp_id=exp_id))
                
            return redirect(url_for('experiment.view', exp_id=exp_id))

        return render_template('add_stimuli.html', form=form, stimulus_type=stimulus_type)


@experiment_blueprint.route('/edit_stimuli', methods=['GET', 'POST'])
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
                           
        return redirect(url_for('experiment.view', exp_id=exp_id))
  
    return render_template('edit_stimuli.html', form=form, edit_page=edit_page)


@experiment_blueprint.route('/remove_stimuli')
@login_required
def remove_stimuli():

    exp_id = request.args.get('exp_id', None)
    exp_status = experiment.query.filter_by(idexperiment=exp_id).first()

    if exp_status.status != 'Hidden':
    
        flash("Experiment is public. Cannot modify structure.")

        return redirect(url_for('experiment.view', exp_id=exp_id))
        
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
                if experiment_pages[a].media == remove_page.media and experiment_pages[a].idpage != remove_page.idpage:
                    do_not_delete_file = 'True'
    
            #If no other page is using the file then lets remove it
            if do_not_delete_file == 'False':
                target = os.path.join(APP_ROOT, remove_page.media)
                os.remove(target)
        
            db.session.delete(remove_page)
            db.session.commit()
      
            return redirect(url_for('experiment.view', exp_id=exp_id))
        
        if remove_page.type == 'text':
            
            db.session.delete(remove_page)
            db.session.commit()
            
            return redirect(url_for('experiment.view', exp_id=exp_id))
        
        return redirect(url_for('experiment.view', exp_id=exp_id))



# Misc:

@experiment_blueprint.route('/statistics')
@login_required
def statistics():

    # TODO: Answers are in normal order although questions might be in randomized order
    
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


