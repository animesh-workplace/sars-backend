from django.conf.urls import url
from .modules.upload import UserFileUploadHandlerAPI
from .modules.metadata_info import UserMetadataInfoAPI
from .modules.metadata_stats import UserMetadataStatsAPI
from .modules.metadata_upload import UserMetadataUploadAPI

urlpatterns = [
    url(r'^metadata-info/$', UserMetadataInfoAPI.as_view(), name='metadata-info'),
    url(r'^file-upload/$', UserFileUploadHandlerAPI.as_view(), name='file-upload'),
    url(r'^metadata-stats/$', UserMetadataStatsAPI.as_view(), name='metadata-stats'),
    url(r'^metadata-upload/$', UserMetadataUploadAPI.as_view(), name='metadata-upload'),
]
