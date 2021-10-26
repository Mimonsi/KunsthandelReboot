from flask import Blueprint, render_template, url_for, request, abort, flash
from flask_babel import gettext

from kunsthandel import db
from kunsthandel.generic_type.forms import EditGenericTypeForm
from kunsthandel.main.utils import role_required
from kunsthandel.models import Item, Image, Role, Type, Location, Origin

generic_type = Blueprint('generic_type', __name__)


@generic_type.route('/<string:model_name>/')
@generic_type.route('/<string:model_name>/overview')
@role_required(Role.User)
def overview(model_name):
    page = request.args.get('page', type=int)
    global model
    if model_name == "types":
        model = Type.query.paginate(page=page, per_page=50)
    elif model_name == "locations":
        model = Location.query.paginate(page=page, per_page=50)
    elif model_name == "origins":
        model = Origin.query.paginate(page=page, per_page=50)
    else:
        abort(404)
    return render_template("generic_type_overview.html", title=gettext("User account overview:"), model=model, model_name=model_name)


@generic_type.route('/<string:model_name>/create', methods=['GET', 'POST'])
def create(model_name):
    global model
    form = EditGenericTypeForm()
    if form.validate_on_submit():
        if model_name == "types":
            model = Type(name=form.name.data)
        elif model_name == "locations":
            model = Location(name=form.name.data)
        elif model_name == "origins":
            model = Origin(name=form.name.data)
        db.session.add(model)
        db.session.commit()
        flash(gettext("%s with ID %s has been successfully created") % (model.model_name(), str(model.id)), "success")
    elif request.method == 'GET':
        pass
    legend_text = gettext("Create new dataset")
    return render_template("generic_type_edit.html", title=legend_text, legend_text=legend_text, form=form)


@generic_type.route('/<string:model_name>/<int:id>/edit', methods=['GET', 'POST'])
def edit(model_name, id):
    global model
    if model_name == "types":
        model = Type.query.get_or_404(id)
    elif model_name == "locations":
        model = Location.query.get_or_404(id)
    elif model_name == "origins":
        model = Origin.query.get_or_404(id)
    form = EditGenericTypeForm()
    form.submit.label.text = gettext("Update")
    if form.validate_on_submit():
        model.name = form.name.data
        db.session.commit()
        flash(gettext("%s with ID %s has been successfully updated") % (model.model_name(), str(model.id)), "success")
    elif request.method == 'GET':
        form.name.data = model.name
    legend_text = gettext("Details for %s with ID %s") % (model.model_name(), str(id))
    return render_template("generic_type_edit.html", title=legend_text, legend_text=legend_text, model=model, form=form)



@generic_type.route('/<string:model_name>/<int:id>')
def details(model_name, id):
    global model
    if model_name == "types":
        model = Type.query.get_or_404(id)
    elif model_name == "locations":
        model = Location.query.get_or_404(id)
    elif model_name == "origins":
        model = Origin.query.get_or_404(id)
    else:
        abort(404)
    legend_text = gettext("Details for %s with ID %s") % (model.model_name(), str(id))
    return render_template("generic_type_details.html", model_name=model_name, model=model, title=legend_text, legend_text=legend_text)