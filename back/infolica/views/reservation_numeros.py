# -*- coding: utf-8 -*--
from pyramid.view import view_config
import pyramid.httpexceptions as exc

from infolica.models.constant import Constant
from infolica.models.models import Numero
from infolica.scripts.utils import Utils
from infolica.views.numero import numeros_new_view, affaire_numero_new_view
from infolica.views.numero import numeros_etat_histo_new_view
from infolica.views.numero_relation import numeros_relations_new_view


def savePointMO(request, affaire_id, cadastre_id, numero_type, n_numeros, etat_id):
    settings = request.registry.settings
    cadastres_ChauxDeFonds_Eplatures_id = settings['cadastres_ChauxDeFonds_Eplatures_id'].split(",")
    cadastres_ChauxDeFonds_Eplatures_id = [
        int(cadastres_ChauxDeFonds_Eplatures_id[0]),
        int(cadastres_ChauxDeFonds_Eplatures_id[1])
    ]
    cadastres_BrotPlamboz_Plamboz_id = settings['cadastres_BrotPlamboz_Plamboz_id'].split(",")
    cadastres_BrotPlamboz_Plamboz_id = [
        int(cadastres_BrotPlamboz_Plamboz_id[0]),
        int(cadastres_BrotPlamboz_Plamboz_id[1])
    ]
    cadastres_Neuchatel_Coudre_id = settings['cadastres_Neuchatel_Coudre_id'].split(",")
    cadastres_Neuchatel_Coudre_id = [
        int(cadastres_Neuchatel_Coudre_id[0]),
        int(cadastres_Neuchatel_Coudre_id[1])
    ]
    cadastres_Sauge_StAubin_id = settings['cadastres_Sauge_StAubin_id'].split(",")
    cadastres_Sauge_StAubin_id = [int(cadastres_Sauge_StAubin_id[0]), int(cadastres_Sauge_StAubin_id[1])]

    # Corriger la liste des cadastres où la réservation de numéros se fait sur deux cadastres
    if cadastre_id == cadastres_ChauxDeFonds_Eplatures_id[0] or cadastre_id == cadastres_ChauxDeFonds_Eplatures_id[1]:
        # Cadastre de la Chaux-de-Fonds et des Eplatures
        ln = max(
            Utils.last_number(request, cadastres_ChauxDeFonds_Eplatures_id[0], [numero_type]),
            Utils.last_number(request, cadastres_ChauxDeFonds_Eplatures_id[1], [numero_type])
        )
    elif cadastre_id == cadastres_BrotPlamboz_Plamboz_id[0] or cadastre_id == cadastres_BrotPlamboz_Plamboz_id[1]:
        # Cadastre de Brot-Plamboz et Plamboz
        ln = max(
            Utils.last_number(request, cadastres_BrotPlamboz_Plamboz_id[0], [numero_type]),
            Utils.last_number(request, cadastres_BrotPlamboz_Plamboz_id[1], [numero_type])
        )
    elif cadastre_id == cadastres_Neuchatel_Coudre_id[0] or cadastre_id == cadastres_Neuchatel_Coudre_id[1]:
        # Cadastre de Neuchâtel et de la Coudre
        ln = max(
            Utils.last_number(request, cadastres_Neuchatel_Coudre_id[0], [numero_type]),
            Utils.last_number(request, cadastres_Neuchatel_Coudre_id[1], [numero_type])
        )
    elif cadastre_id == cadastres_Sauge_StAubin_id[0] or cadastre_id == cadastres_Sauge_StAubin_id[1]:
        # Cadastre de Sauge et de Saint-Aubin
        ln = max(
            Utils.last_number(request, cadastres_Sauge_StAubin_id[0], [numero_type]),
            Utils.last_number(request, cadastres_Sauge_StAubin_id[1], [numero_type])
        )
    else:
        ln = Utils.last_number(request, cadastre_id, [numero_type])

    for i in range(n_numeros):
        # enregistrer un nouveau numéro
        params = Utils._params(
            cadastre_id=cadastre_id, type_id=numero_type, etat_id=etat_id, numero=ln + i+1)
        numero_id = numeros_new_view(request, params)
        # enregistrer le lien affaire-numéro
        params = Utils._params(
            affaire_id=affaire_id, numero_id=numero_id, actif=True, type_id=2)
        affaire_numero_new_view(request, params)


@view_config(route_name='reservation_numeros', request_method='POST', renderer='json')
@view_config(route_name='reservation_numeros_s', request_method='POST', renderer='json')
def reservation_numeros_new_view(request):
    """
    Add new numeros in affaire
    """
    # Check authorization
    if not Utils.has_permission(request, request.registry.settings['affaire_numero_edition']):
        raise exc.HTTPForbidden()

    # Récupère les id des biens-fonds de la config
    settings = request.registry.settings
    numero_bf_id = int(settings['numero_bf_id'])
    numero_ddp_id = int(settings['numero_ddp_id'])
    numero_ppe_id = int(settings['numero_ppe_id'])
    numero_pcop_id = int(settings['numero_pcop_id'])
    numero_pfp3_id = int(settings['numero_pfp3_id'])
    numero_bat_id = int(settings['numero_bat_id'])
    numero_pcs_id = int(settings['numero_pcs_id'])
    numero_paux_id = int(settings['numero_paux_id'])
    # numero_pdet_id = int(settings['numero_pdet_id'])
    numero_dp_id = int(settings['numero_dp_id'])

    # Récupère les id des états des biens-fonds de la config
    numero_projet_id = int(settings['numero_projet_id'])
    numero_vigueur_id = int(settings['numero_vigueur_id'])
    # numero_abandonne_id = int(settings['numero_abandonne_id'])
    # numero_supprime_id = int(settings['numero_supprime_id'])

    # Get affaire_id
    affaire_id = request.params['affaire_id'] if 'affaire_id' in request.params else None
    cadastre_id = int(request.params['cadastre_id']) if 'cadastre_id' in request.params else None
    plan_id = request.params['plan_id'] if 'plan_id' in request.params else None

    # Get first available number (BF, DDP, PPE, PCOP)
    ln = Utils.last_number(request, cadastre_id, [numero_bf_id, numero_ddp_id, numero_ppe_id, numero_pcop_id])

    c = 0
    # Biens-fonds
    if 'bf' in request.params:
        for i in range(int(request.params['bf'])):
            c += 1
            # enregistrer un nouveau numéro
            params = Utils._params(
                cadastre_id=cadastre_id, type_id=numero_bf_id, etat_id=numero_projet_id, numero=ln + c)
            numero_id = numeros_new_view(request, params)
            # enregistrer le lien affaire-numéro
            params = Utils._params(
                affaire_id=affaire_id, numero_id=numero_id, actif=True, type_id=2)
            affaire_numero_new_view(request, params)
            # enregistrer l'historique de l'état
            params = Utils._params(numero_id=numero_id, numero_etat_id=1)
            numeros_etat_histo_new_view(request, params)

    if 'ddp' in request.params:
        for i in range(int(request.params['ddp'])):
            c += 1
            # enregistrer un nouveau numéro
            params = Utils._params(
                cadastre_id=cadastre_id, type_id=numero_ddp_id, etat_id=numero_projet_id, numero=ln + c)
            numero_id = numeros_new_view(request, params)
            # enregistrer le lien affaire-numéro
            params = Utils._params(
                affaire_id=affaire_id, numero_id=numero_id, actif=True, type_id=2)
            affaire_numero_new_view(request, params)
            # enregistrer l'historique de l'état
            params = Utils._params(numero_id=numero_id, numero_etat_id=1)
            numeros_etat_histo_new_view(request, params)
            # enregistrer le DDP sur un bien-fonds de base
            numero_id_base = request.params['ddp_base'] if 'ddp_base' in request.params else None
            params = Utils._params(
                numero_id_base=numero_id_base,
                numero_id_associe=numero_id,
                relation_type_id=2,
                affaire_id=affaire_id
            )
            numeros_relations_new_view(request, params)

    if 'ppe' in request.params:
        unite_start_idx = Utils.get_index_from_unite(
            request.params["ppe_unite"].upper()) if "ppe_unite" in request.params else 0
        for i in range(int(request.params['ppe'])):
            c += 1
            # enregistrer un nouveau numéro
            suffixe = Utils.get_unite_from_index(unite_start_idx + i)
            params = Utils._params(
                cadastre_id=cadastre_id,
                type_id=numero_ppe_id,
                etat_id=numero_projet_id,
                numero=ln + c,
                suffixe=suffixe
            )
            numero_id = numeros_new_view(request, params)
            # enregistrer le lien affaire-numéro
            params = Utils._params(
                affaire_id=affaire_id,
                numero_id=numero_id,
                actif=True,
                type_id=2
            )
            affaire_numero_new_view(request, params)
            # enregistrer l'historique de l'état
            params = Utils._params(numero_id=numero_id, numero_etat_id=1)
            numeros_etat_histo_new_view(request, params)
            # enregistrer le DDP sur un bien-fonds de base
            numero_id_base = request.params['ppe_base'] if 'ppe_base' in request.params else None
            params = Utils._params(
                numero_id_base=numero_id_base,
                numero_id_associe=numero_id,
                relation_type_id=3,
                affaire_id=affaire_id
            )
            numeros_relations_new_view(request, params)

    if 'pcop' in request.params:
        for i in range(int(request.params['pcop'])):
            c += 1
            # enregistrer un nouveau numéro
            params = Utils._params(
                cadastre_id=cadastre_id,
                type_id=numero_pcop_id,
                etat_id=numero_projet_id,
                numero=ln + c,
                suffixe="part"
            )
            numero_id = numeros_new_view(request, params)
            # enregistrer le lien affaire-numéro
            params = Utils._params(
                affaire_id=affaire_id, numero_id=numero_id, actif=True, type_id=2)
            affaire_numero_new_view(request, params)
            # enregistrer l'historique de l'état
            params = Utils._params(numero_id=numero_id, numero_etat_id=1)
            numeros_etat_histo_new_view(request, params)
            # enregistrer le DDP sur un bien-fonds de base
            numero_id_base = request.params['pcop_base'] if 'pcop_base' in request.params else None
            params = Utils._params(
                numero_id_base=numero_id_base,
                numero_id_associe=numero_id,
                relation_type_id=4,
                affaire_id=affaire_id
            )
            numeros_relations_new_view(request, params)

    if 'pfp3' in request.params:
        savePointMO(
            request,
            affaire_id,
            cadastre_id,
            numero_pfp3_id,
            int(request.params["pfp3"]),
            etat_id=numero_vigueur_id
        )

    if 'bat' in request.params:
        savePointMO(
            request, affaire_id,
            cadastre_id,
            numero_bat_id,
            int(request.params["bat"]),
            etat_id=numero_vigueur_id
        )

    if 'dp' in request.params:
        savePointMO(
            request,
            affaire_id,
            cadastre_id,
            numero_dp_id,
            int(request.params["dp"]),
            etat_id=numero_vigueur_id
        )

    if 'paux' in request.params:
        savePointMO(
            request,
            affaire_id,
            cadastre_id,
            numero_paux_id,
            int(request.params["paux"]),
            etat_id=numero_vigueur_id
        )

    if 'pcs' in request.params:
        ln = Utils.last_number(request, cadastre_id, [7], plan_id=plan_id)
        for i in range(int(request.params['pcs'])):
            # enregistrer un nouveau numéro
            params = Utils._params(
                cadastre_id=cadastre_id,
                type_id=numero_pcs_id,
                etat_id=numero_vigueur_id,
                numero=ln + i+1,
                plan_id=plan_id
            )
            numero_id = numeros_new_view(request, params)
            # enregistrer le lien affaire-numéro
            params = Utils._params(
                affaire_id=affaire_id, numero_id=numero_id, actif=True, type_id=2)
            affaire_numero_new_view(request, params)

    return Utils.get_data_save_response(Constant.SUCCESS_SAVE.format(Numero.__tablename__))
