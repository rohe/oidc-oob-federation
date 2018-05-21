#!/usr/bin/env python3
import importlib
import os
import sys
from urllib.parse import quote_plus
from urllib.parse import urlparse, quote_plus

from fedoidcendpoint.endpoint_context import EndpointContext
from fedoidcmsg import ProviderConfigurationResponse
from fedoidcmsg.test_utils import create_compounded_metadata_statement
from fedoidcmsg.test_utils import create_federation_entities
from fedoidcmsg.test_utils import make_signing_sequence
from oidcmsg.key_jar import init_key_jar
from oidcmsg.message import Message
from oidcop.cherrypy import OpenIDProvider

for _dir in ['sms/discovery', 'sms/response','private', 'public', 'static']:
    if not os.path.isdir(_dir):
        os.makedirs(_dir)

folder = os.path.abspath(os.curdir)
sys.path.insert(0, ".")
config = importlib.import_module(sys.argv[1])

_provider_config = config.CONFIG['provider']
_server_info_config = _provider_config['server_info']
_jwks_config = _provider_config['jwks']

_kj = init_key_jar(**_jwks_config)

endpoint_context = EndpointContext(_server_info_config, keyjar=_kj,
                                   cwd=folder)

for endp in endpoint_context.endpoint.values():
    p = urlparse(endp.endpoint_path)
    _vpath = p.path.split('/')
    if _vpath[0] == '':
        endp.vpath = _vpath[1:]
    else:
        endp.vpath = _vpath

op = OpenIDProvider(config, endpoint_context)
_info = ProviderConfigurationResponse(**op.endpoint_context.provider_info)

SUNET_OP = op.endpoint_context.federation_entity

# The kind of keys the federation entities has
FED_KEYDEF = [{"type": "EC", "crv": "P-256", "use": ["sig"]}]

# Identifiers for all the entities
ALL = ['https://edugain.org', 'https://swamid.sunet.se']

# Create the federation entities
FEDENT = create_federation_entities(ALL, FED_KEYDEF, root_dir='../')
SWAMID = FEDENT['https://swamid.sunet.se']
EDUGAIN = FEDENT['https://edugain.org']

FEDENT[SUNET_OP.iss] = SUNET_OP

_sms = create_compounded_metadata_statement(
    [SUNET_OP.iss, SWAMID.iss, EDUGAIN.iss],
    FEDENT,
    {SWAMID.iss: Message(), SUNET_OP.iss: _info}, 'discovery', lifetime=86400)

fp = open('sms/discovery/{}'.format(quote_plus(EDUGAIN.iss)), 'w')
fp.write(_sms)
fp.close()

try:
    _sms = make_signing_sequence([SUNET_OP.iss, SWAMID.iss, EDUGAIN.iss],
                                 FEDENT, 'response', lifetime=86400)
except Exception as err:
    print(err)

fp = open('sms/response/{}'.format(quote_plus(EDUGAIN.iss)), 'w')
fp.write(_sms)
fp.close()
