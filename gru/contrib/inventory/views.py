import json

import yaml
from flask import Blueprint, render_template, make_response, abort, request, redirect, url_for, current_app

from gru.config import settings
from gru.utils.pagination import Paginator


# Create blueprint
blueprint = Blueprint('inventory', __name__, template_folder='templates')


# Helper functions
def get_group(group_field_name):
    """
    Lookup a group_by field definition from the settings file
    :param group_field_name: the name of the group to aggregate by
    """
    grouping_fields = settings.get('inventory.group_by')
    for group in grouping_fields:
        if group.get('field') == group_field_name:
            return group
    abort(404)


def get_page():
    page = request.args.get('page')
    if page:
        try:
            return int(page)
        except ValueError:
            abort(404)
    else:
        return 1


def get_serializer():
    return request.args.get('fmt')


def serialized(obj, status=200):
    fmt = get_serializer()
    if fmt == 'json':
        ser = json.dumps
        ct = 'application/json'
    elif fmt == 'yaml':
        ser = yaml.safe_dump
        ct = 'text/plain+yaml'  # For interop with browsers
    elif fmt is None:
        return None
    else:
        abort(404)
    data = ser(obj)
    resp = make_response(data, 200)
    resp.headers['Content-Type'] = ct
    return resp


# Authentication
@blueprint.before_request
def authenticate_pre_request():
    """
    All endoints require authentication, if that's configured
    """
    auth = current_app.plugins.authentication_backend
    if not auth.is_logged_in():
        return redirect(auth.get_login_url(request.path))


# Actual views
@blueprint.route('/group/<group>')
def group_breakdown(group):
    """
    Breakdown host counts into aggregated groups by field name
    """
    group_def = get_group(group)
    ctx = {
        'title': group_def.get('title'),
        'group_field': group,
        'group_title': group_def.get('title'),
        'categories': current_app.plugins.inventory_provider.host_group_breakdown(group)
    }
    return render_template('inventory/breakdown.html', **ctx)


@blueprint.route('/group/<group>/<field>')
def host_list(group, field):
    """
    List hosts by filtering a given field and value.
    """
    page = get_page()
    paginator = Paginator(page)
    list_kwargs = paginator.page_kwargs()
    group_def = get_group(group)
    # Calculate pagination
    sort_by = settings.get('inventory.host_table_sort_by', None)
    if sort_by:
        list_kwargs['sort_by'] = sort_by
    result = current_app.plugins.inventory_provider.list(group, field, **list_kwargs)
    total_results = result.total_hosts
    if page > paginator.total_pages(total_results):
        abort(404)
    if get_serializer():
        return serialized({
            'total': total_results,
            'results': map(lambda h: h.host_data, result.hosts),
            'paging': paginator.serialize(total_results)
        })
    return render_template('inventory/host_list.html', **{
        'title': '%s - %s' % (group_def.get('title'), field),
        'group_field': group,
        'field': field,
        'group_title': group_def.get('title'),
        'host_list': result.hosts,
        'total': total_results,
        'paginator': paginator
    })


@blueprint.route('/search')
def host_search_form():
    """
    Redirect to search results page
    """
    return redirect(url_for('.host_search', query=request.args.get('q')))


@blueprint.route('/search/<query>')
def host_search(query):
    """
    Kibana-like search (with query_string).
    """
    page = get_page()
    paginator = Paginator(page)
    result = current_app.plugins.inventory_provider.host_search(query, **paginator.page_kwargs())
    total_results = result.total_hosts
    if page > paginator.total_pages(total_results) and total_results > 0:
        abort(404)
    if get_serializer():
        return serialized({
            'total': total_results,
            'search_query': query,
            'results': map(lambda h: h.host_data, result.hosts),
            'paging': paginator.serialize(total_results)
        })
    return render_template('inventory/host_search.html', **{
        'title': 'Search: {}'.format(query),
        'search_query': query,
        'host_list': result.hosts,
        'total': total_results,
        'paginator': paginator
    })


@blueprint.route('/hosts/<host_id>', methods=['GET'])
def host_info(host_id):
    """
    A per-host page.
    """
    host_id = host_id.lower()
    model = current_app.plugins.inventory_provider.get_host_by_id(host_id)
    if not model:
        abort(404)
    if get_serializer():
        return serialized(model.to_dict())
    host_widgets = []
    for widget in current_app.plugins.host_widgets:
        if widget.qualify(model):
            rendered = widget._render_blocks(model)
            host_widgets.append(rendered)
    return render_template('inventory/host_info.html', **{
        'title': host_id,
        'host_id': host_id,
        'host': model,
        'host_widgets': host_widgets
    })
