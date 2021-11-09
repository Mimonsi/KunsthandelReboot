from flask import Blueprint, render_template, url_for, request, abort, flash
from flask_babel import gettext

from kunsthandel import db
from kunsthandel.generic_type.forms import EditGenericTypeForm
from kunsthandel.main.utils import role_required
from kunsthandel.models import Item, Image, Role, Type, Location, Origin

generic_type = Blueprint('generic_type', __name__)

MODELS = {
    "types": Type,
    "locations": Location,
    "origins": Origin
}


@generic_type.route('/<string:model_name>/')
@generic_type.route('/<string:model_name>/overview')
@role_required(Role.User)
def overview(model_name):
    page = request.args.get('page', type=int)
    try:
        model = MODELS[model_name].query.paginate(page=page, per_page=50)
    except KeyError:
        abort(404, "Model not found")
        return
    return render_template("generic_type_overview.html", title=gettext("User account overview"), model=model,
                           model_name=model_name)


@generic_type.route('/<string:model_name>/create', methods=['GET', 'POST'])
@role_required(Role.Editor)
def create(model_name):
    form = EditGenericTypeForm()
    if form.validate_on_submit():
        try:
            model = MODELS[model_name](name=form.name.data)
        except KeyError:
            abort(404, "Model not found")
            return
        db.session.add(model)
        db.session.commit()
        flash(gettext("%s with ID %s has been successfully created") % (gettext(model.model_name()), str(model.id)),
              "success")
    elif request.method == 'GET':
        pass
    legend_text = gettext("Create new %s") % gettext(model_name)
    return render_template("generic_type_edit.html", title=legend_text, legend_text=legend_text, form=form)


@generic_type.route('/<string:model_name>/<int:id>/edit', methods=['GET', 'POST'])
@role_required(Role.Editor)
def edit(model_name, id):
    try:
        model = MODELS[model_name].query.get_or_404(id)
    except KeyError:
        abort(404, "Model not found")
        return
    form = EditGenericTypeForm()
    form.submit.label.text = gettext("Update")
    if form.validate_on_submit():
        model.name = form.name.data
        db.session.commit()
        flash(gettext("%s with ID %s has been successfully updated") % (gettext(model.model_name()), str(model.id)),
              "success")
    elif request.method == 'GET':
        form.name.data = model.name
    legend_text = gettext("Details for %s with ID %s") % (gettext(model.model_name()), str(id))
    return render_template("generic_type_edit.html", title=gettext("Edit %s") % gettext(model.model_name()),
                           legend_text=legend_text, model=model, form=form)


@generic_type.route('/<string:model_name>/<int:id>')
@role_required(Role.Editor)
def details(model_name, id):
    try:
        model = MODELS[model_name].query.get_or_404(id)
    except KeyError:
        abort(404, "Model not found")
        return
    legend_text = gettext("Details for %s with ID %s") % (gettext(model.model_name()), str(id))
    return render_template("generic_type_details.html", model_name=model_name, model=model,
                           title=gettext("%s Details") % gettext(model.model_name()), legend_text=legend_text)
