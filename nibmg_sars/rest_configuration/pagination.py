from rest_framework import pagination

class NIBMG_SARS_Server_APIPagination(pagination.LimitOffsetPagination):
	default_limit   = 10
	max_limit       = 20
