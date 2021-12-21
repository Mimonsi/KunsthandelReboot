from flask import Blueprint, render_template, url_for, request, abort, flash, redirect
from flask_babel import gettext

from kunsthandel import db
from kunsthandel.generic_type.forms import EditGenericTypeForm
from kunsthandel.main.utils import role_required
from kunsthandel.models import Role, Type, Location, Origin

generic_type = Blueprint("generic_type", __name__)

MODELS = {
    "types": Type,
    "locations": Location,
    "origins": Origin
}


@generic_type.route("/<string:model_name>", methods=["GET"])
@role_required(Role.User)
def overview(model_name):
    page = request.args.get("page", type=int)
    try:
        model = MODELS[model_name].query.paginate(page=page, per_page=50)
    except KeyError:
        abort(404, gettext("Model not found"))
    return render_template("generic_type_overview.html", title=gettext("User account overview"), model=model,
                           model_name=model_name)


@generic_type.route("/<string:model_name>/create", methods=["GET", "POST"])
@role_required(Role.Editor)
def create(model_name):
    form = EditGenericTypeForm()
    try:
        model = MODELS[model_name](name=form.name.data)
    except KeyError:
        abort(404, gettext("Model not found"))
    if request.method == "POST":
        if form.validate_on_submit():
            db.session.add(model)
            db.session.commit()
            flash(gettext("%(model_name)s with ID %(id)s has been successfully created", model_name=model.model_name, id=model.id), "success")
            return redirect(url_for("generic_type.overview", model_name=model_name))
        else:
            legend_text = gettext("Create new %(model_name)s", model_name=model_name)
            return render_template("generic_type_edit.html", title=legend_text, legend_text=legend_text, form=form), 400
    else:  # GET
        legend_text = gettext("Create new %(model_name)s", model_name=model_name)
        return render_template("generic_type_edit.html", title=legend_text, legend_text=legend_text, form=form)


@generic_type.route("/<string:model_name>/<int:id>/edit", methods=["GET", "POST"])
@role_required(Role.Editor)
def edit(model_name, id):
    try:
        model = MODELS[model_name].query.get_or_404(id)
    except KeyError:
        abort(404, gettext("Model not found"))
    form = EditGenericTypeForm()
    form.submit.label.text = gettext("Update")
    if request.method == "POST":
        if form.validate_on_submit():
            model.name = form.name.data
            db.session.commit()
            flash(gettext("%(model_name)s with ID %(id)s has been successfully updated", model_name=model.model_name(), id=id), "success")
            return redirect(url_for("generic_type.overview", model_name=model_name()))
        else:
            legend_text = gettext("Details for %(model_name)s with ID %(id)s", model_name=model.model_name(), id=model.id)
            return render_template("generic_type_edit.html", title=gettext("Edit %(model_name)s", model_name=model.model_name()), legend_text=legend_text, model=model, model_name=model_name, form=form), 400
    else:  # GET
        form.name.data = model.name
        legend_text = gettext("Details for %(model_name)s with ID %(id)s", model_name=model.model_name(), id=id)
        return render_template("generic_type_edit.html", title=gettext("Edit %(model_name)s", model_name=model.model_name()), legend_text=legend_text, model=model, model_name=model_name, form=form)


@generic_type.route("/<string:model_name>/<int:id>", methods=["GET"])
@role_required(Role.User)
def details(model_name, id):
    try:
        model = MODELS[model_name].query.get_or_404(id)
    except KeyError:
        abort(404, gettext("Model not found"))
    legend_text = gettext("Details for %(model_name)s with ID %(id)s", model_name=model.model_name(), id=id)
    return render_template("generic_type.html", model_name=model_name, model=model,
                           title=gettext("%(model_name)s Details", model_name=model.model_name()), legend_text=legend_text)


@generic_type.route("/<string:model_name>/<int:id>/delete", methods=["POST"])
@role_required(Role.Editor)
def delete(model_name, id):
    try:
        model = MODELS[model_name].query.get_or_404(id)
    except KeyError:
        abort(404, gettext("Model not found"))
    dataset = MODELS[model_name].query.get_or_404(id)
    db.session.delete(dataset)
    db.session.commit()
    flash(gettext("The dataset has been deleted successfully"), "success")
    return redirect(url_for("generic_type.overview", model_name=model_name))
