from pyramid.view import view_config
import pyramid.httpexceptions as exc
from ..scripts.utils import Utils
from ..models import Constant
import transaction
from ..exceptions.custom_error import CustomError
from .. import models

""" Return all suivi_mandats"""
@view_config(route_name='suivi_mandats', request_method='GET', renderer='json')
@view_config(route_name='suivi_mandats_s', request_method='GET', renderer='json')
def suivi_mandats_view(request):
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    query = request.dbsession.query(models.SuiviMandat).all()
    return Utils.serialize_many(query)


""" Return suivi_mandats by id"""
@view_config(route_name='suivi_mandat_by_id', request_method='GET', renderer='json')
def suivi_mandats_by_id_view(request):
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.id = request.matchdict['id']
    query = request.dbsession.query(models.SuiviMandat).filter(
        models.SuiviMandat.id == id).first()
    return Utils.serialize_one(query)


""" Return suivi_mandats by affaire_id"""
@view_config(route_name='affaire_suivi_mandats_by_affaire_id', request_method='GET', renderer='json')
def affaire_suivi_mandats_by_affaire_id_view(request):
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    affaire_id = request.id = request.matchdict['id']
    query = request.dbsession.query(models.SuiviMandat).filter(
        models.SuiviMandat.affaire_id == affaire_id).first()

    if query is None:
        return None

    return Utils.serialize_one(query)


""" Add new suivi_mandats"""
@view_config(route_name='suivi_mandats', request_method='POST', renderer='json')
@view_config(route_name='suivi_mandats_s', request_method='POST', renderer='json')
def suivi_mandats_new_view(request):
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_suivi_edition']):
        raise exc.HTTPForbidden()

    record = models.SuiviMandat()
    record = Utils.set_model_record(record, request.params)

    with transaction.manager:
        request.dbsession.add(record)
        request.dbsession.flush()
        # Commit transaction
        transaction.commit()
        return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(models.SuiviMandat.__tablename__))


""" Update suivi_mandats"""
@view_config(route_name='suivi_mandats', request_method='PUT', renderer='json')
@view_config(route_name='suivi_mandats_s', request_method='PUT', renderer='json')
def suivi_mandats_update_view(request):
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_suivi_edition']):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.params['id'] if 'id' in request.params else None

    # Get controle mutation record
    record = request.dbsession.query(models.SuiviMandat).filter(
        models.SuiviMandat.id == id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(models.SuiviMandat.__tablename__, id))

    record = Utils.set_model_record(record, request.params)

    with transaction.manager:
        # Commit transaction
        transaction.commit()
        return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(models.SuiviMandat.__tablename__))


""" Delete suivi_mandats"""
@view_config(route_name='suivi_mandats', request_method='DELETE', renderer='json')
@view_config(route_name='suivi_mandats_s', request_method='DELETE', renderer='json')
def suivi_mandats_delete_view(request):
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_suivi_edition']):
        raise exc.HTTPForbidden()

    # Get controle mutation id
    id = request.params['id'] if 'id' in request.params else None

    # Get controle mutation record
    record = request.dbsession.query(models.SuiviMandat).filter(
        models.SuiviMandat.id == id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(models.SuiviMandat.__tablename__, id))

    with transaction.manager:
        request.dbsession.delete(record)
        # Commit transaction
        transaction.commit()
        return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(models.SuiviMandat.__tablename__))
