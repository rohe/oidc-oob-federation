#!/usr/bin/env python3
import argparse
import importlib
import os
import sys
from urllib.parse import quote_plus

from fedoidcmsg.test_utils import create_federation_entities
from fedoidcmsg.test_utils import create_compounded_metadata_statement
from fedoidcmsg.test_utils import make_signing_sequence
from fedoidcrp import oidc
from fedoidcservice.service import factory

from oidcmsg.key_jar import init_key_jar
from oidcmsg.message import Message
from oidcrp import RPHandler

for _dir in ['sms/registration', 'private', 'public', 'static']:
    if not os.path.isdir(_dir):
        os.makedirs(_dir)

parser = argparse.ArgumentParser()
parser.add_argument('-p', dest='port', default=80, type=int)
parser.add_argument('-t', dest='tls', action='store_true')
parser.add_argument('-k', dest='insecure', action='store_true')
parser.add_argument(dest="config")
args = parser.parse_args()

folder = os.path.abspath(os.curdir)

sys.path.insert(0, ".")
config = importlib.import_module(args.config)
cprp = importlib.import_module('cprp')

if args.port:
    _base_url = "{}:{}".format(config.BASEURL, args.port)
else:
    _base_url = config.BASEURL

_kj = init_key_jar(**config.RP_CONFIG['jwks'])

if args.insecure:
    verify_ssl = False
else:
    verify_ssl = True

rph = RPHandler(base_url=_base_url, hash_seed="BabyDriver", keyjar=_kj,
                jwks_path=config.RP_CONFIG['jwks_url_path'],
                client_configs=config.CLIENTS, service_factory=factory,
                client_cls=oidc.RP, verify_ssl=verify_ssl)

client = rph.init_client('')

print(client.service_context.federation_entity.entity_id)

client.service_context.redirect_uris = ['https://entity.example.com/cb']
_srv = client.service['registration']

reg_req = _srv.construct()

SUNET_RP = client.service_context.federation_entity

# The kind of keys the federation entities has
FED_KEYDEF = [{"type": "EC", "crv": "P-256", "use": ["sig"]}]

# Identifiers for all the entities
ALL = ['https://edugain.org', 'https://swamid.sunet.se']

# Create the federation entities
FEDENT = create_federation_entities(ALL, FED_KEYDEF, root_dir='../')
SWAMID = FEDENT['https://swamid.sunet.se']
EDUGAIN = FEDENT['https://edugain.org']

FEDENT[SUNET_RP.iss] = SUNET_RP

try:
    _sms = make_signing_sequence([SUNET_RP.iss, SWAMID.iss, EDUGAIN.iss],
                                 FEDENT, 'registration', lifetime=86400)
except Exception as err:
    print(err)
else:
    fp = open('sms/registration/{}'.format(quote_plus(EDUGAIN.iss)), 'w')
    fp.write(_sms)
    fp.close()
