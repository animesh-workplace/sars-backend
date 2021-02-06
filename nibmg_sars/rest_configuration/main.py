import datetime

REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
		'rest_framework.authentication.SessionAuthentication',
	),
	'DEFAULT_PERMISSION_CLASSES': (
		'rest_framework.permissions.IsAuthenticatedOrReadOnly',
	),
	'DEFAULT_PAGINATION_CLASS': 'nibmg_sars.rest_configuration.pagination.NIBMG_SARS_Server_APIPagination',
	'DEFAULT_FILTER_BACKENDS': (
			'rest_framework.filters.SearchFilter',
			'rest_framework.filters.OrderingFilter',
	),
	'SEARCH_PARAM': 'q',
	'ORDERING_PARAM': 'ordering',
	'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}


JWT_AUTH = {
	'JWT_AUTH_COOKIE'                   : 'c_uid',
	'JWT_ALLOW_REFRESH'                 : True,
	'JWT_ENCODE_HANDLER'                : 'rest_framework_jwt.utils.jwt_encode_handler',
	'JWT_DECODE_HANDLER'                : 'rest_framework_jwt.utils.jwt_decode_handler',
	'JWT_PAYLOAD_HANDLER'               : 'rest_framework_jwt.utils.jwt_payload_handler',
	'JWT_EXPIRATION_DELTA'              : datetime.timedelta(days=1),
	'JWT_AUTH_HEADER_PREFIX'            : 'JWT',
	'JWT_REFRESH_EXPIRATION_DELTA'      : datetime.timedelta(days=1),
	'JWT_RESPONSE_PAYLOAD_HANDLER'      : 'nibmg_sars.rest_configuration.utils.jwt_response_payload_handler',
	'JWT_PAYLOAD_GET_USER_ID_HANDLER'   : 'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',
}
