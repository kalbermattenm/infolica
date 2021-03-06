from pyramid.view import view_config
import pyramid.httpexceptions as exc
from .. import models
import transaction
from ..models import Constant
from ..exceptions.custom_error import CustomError
from ..scripts.utils import Utils

###########################################################
# SERVICES EXTERNES 
###########################################################

""" GET service by id"""
@view_config(route_name='service_by_id', request_method='GET', renderer='json')
def service_by_id_view(request):
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    service_id = request.matchdict['id']

    record = request.dbsession.query(models.Service)\
        .filter(models.Service.id==service_id).first()

    return Utils.serialize_one(record)


""" GET services"""
@view_config(route_name='services', request_method='GET', renderer='json')
@view_config(route_name='services_s', request_method='GET', renderer='json')
def services_view(request):
    # Check connected
    if not Utils.check_connected(request):
        raise exc.HTTPForbidden()

    records = request.dbsession.query(models.Service).all()

    return Utils.serialize_many(records)


""" Add preavis affaire"""
@view_config(route_name='services', request_method='POST', renderer='json')
@view_config(route_name='services_s', request_method='POST', renderer='json')
def services_new_view(request):
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['fonction_admin']):
        raise exc.HTTPForbidden()

    model = models.Service()
    model = Utils.set_model_record(model, request.params)

    with transaction.manager:
        request.dbsession.add(model)
        # Commit transaction
        transaction.commit()
        return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(models.Service.__tablename__))


""" UPDATE service """
@view_config(route_name='services', request_method='PUT', renderer='json')
@view_config(route_name='services_s', request_method='PUT', renderer='json')
def services_update_view(request):
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['fonction_admin']):
        raise exc.HTTPForbidden()

    service_id = request.params['id'] if 'id' in request.params else None
    record = request.dbsession.query(models.Service).filter(
        models.Service.id == service_id).first()

    if not record:
        raise CustomError(
            CustomError.RECORD_WITH_ID_NOT_FOUND.format(models.Service.__tablename__, service_id))

    record = Utils.set_model_record(record, request.params)

    with transaction.manager:
        transaction.commit()
        return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(models.Service.__tablename__))


# """ DELETE preavis affaire"""
# @view_config(route_name='preavis_by_id', request_method='DELETE', renderer='json')
# def preavis_delete_view(request):
    # Check authorization
    # if not Utils.has_permission(request, request.registry.settings['fonction_admin']):
    #     raise HTTPForbidden()

#     service_id = request.matchdict['id']

#     record = request.dbsession.query(models.Service).filter(
#         models.Service.id == service_id).first()

#     if not record:
#         raise CustomError(
#             CustomError.RECORD_WITH_ID_NOT_FOUND.format(models.Service.__tablename__, service_id))

#     
#         with transaction.manager:
#             request.dbsession.delete(record)
#             # Commit transaction
#             transaction.commit()
#             return Utils.get_data_save_response(Constant.SUCCESS_DELETE.format(models.Service.__tablename__))

#     except Exception as e:
#         raise e
