from datetime import datetime
from pyramid.view import view_config
import pyramid.httpexceptions as exc
from .. import models
import transaction
from ..models import Constant
from ..exceptions.custom_error import CustomError
from ..scripts.utils import Utils

""" Return all types clients"""
@view_config(route_name='types_clients', request_method='GET', renderer='json')
@view_config(route_name='types_clients_s', request_method='GET', renderer='json')
def types_clients_view(request):
    query = request.dbsession.query(models.ClientType).all()
    return Utils.serialize_many(query)


""" Return all clients"""
@view_config(route_name='clients', request_method='GET', renderer='json')
@view_config(route_name='clients_s', request_method='GET', renderer='json')
def clients_view(request):
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    query = request.dbsession.query(models.Client).all()
    return Utils.serialize_many(query)

""" Return client by id"""
@view_config(route_name='client_by_id', request_method='GET', renderer='json')
def client_by_id_view(request):
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    id = request.matchdict['id']
    query = request.dbsession.query(models.Client).filter(
        models.Client.id == id).first()
    return Utils.serialize_one(query)


""" Search clients"""
@view_config(route_name='recherche_clients', request_method='POST', renderer='json')
@view_config(route_name='recherche_clients_s', request_method='POST', renderer='json')
def clients_search_view(request):
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    settings = request.registry.settings
    search_limit = int(settings['search_limit'])
    conditions = Utils.get_search_conditions(models.Client, request.params)

    # Check date_sortie is null
    conditions = [] if not conditions or len(
        conditions) == 0 else conditions

    conditions.append(models.Client.sortie == None)

    query = request.dbsession.query(models.Client).order_by(models.Client.nom, models.Client.prenom).filter(
        *conditions).limit(search_limit).all()
    return Utils.serialize_many(query)


""" Add new client"""
@view_config(route_name='clients', request_method='POST', renderer='json')
@view_config(route_name='clients_s', request_method='POST', renderer='json')
def clients_new_view(request):
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['client_edition']):
        raise exc.HTTPForbidden()

    # Get client instance
    model = Utils.set_model_record(models.Client(), request.params)

    with transaction.manager:
        request.dbsession.add(model)
        request.dbsession.flush()
        transaction.commit()
        return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(models.Client.__tablename__))


""" Update client"""
@view_config(route_name='clients', request_method='PUT', renderer='json')
@view_config(route_name='clients_s', request_method='PUT', renderer='json')
def clients_update_view(request):
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['client_edition']):
        raise exc.HTTPForbidden()

    # Get client_id
    id_client = request.params['id'] if 'id' in request.params else None

    model = request.dbsession.query(models.Client).filter(
        models.Client.id == id_client).first()

    # If result is empty
    if not model:
        raise CustomError(CustomError.RECORD_WITH_ID_NOT_FOUND.format(
            models.Client.__tablename__, id_client))

    # Read params client
    model = Utils.set_model_record(model, request.params)

    with transaction.manager:

        transaction.commit()
        return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(models.Client.__tablename__))


""" Delete client"""
@view_config(route_name='clients', request_method='DELETE', renderer='json')
@view_config(route_name='clients_s', request_method='DELETE', renderer='json')
def clients_delete_view(request):
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['client_edition']):
        raise exc.HTTPForbidden()

    # Get client_id
    id_client = request.params['id'] if 'id' in request.params else None

    model = request.dbsession.query(models.Client).filter(
        models.Client.id == id_client).first()

    # If result is empty
    if not model:
        raise CustomError(CustomError.RECORD_WITH_ID_NOT_FOUND.format(
            models.Client.__tablename__, id_client))

    model.sortie = datetime.utcnow()

    with transaction.manager:

        transaction.commit()
        return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(models.Client.__tablename__))