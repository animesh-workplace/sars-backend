from django.conf.urls import url
from .modules.upload import UserFileUploadHandlerAPI
from .modules.download_info import UserDownloadInfoAPI
from .modules.metadata_upload import UserMetadataUploadAPI
from .modules.metadata_stats import UserMetadataStatsAPI, UserMetadataStateStatsAPI
from .modules.metadata_info import UserMetadataInfoAPI, UserMetadataOnlyNameInfoAPI

urlpatterns = [
    url(r'^metadata-info/$', UserMetadataInfoAPI.as_view(), name='metadata-info'),
    url(r'^file-upload/$', UserFileUploadHandlerAPI.as_view(), name='file-upload'),
    url(r'^metadata-stats/$', UserMetadataStatsAPI.as_view(), name='metadata-stats'),
    url(r'^metadata-upload/$', UserMetadataUploadAPI.as_view(), name='metadata-upload'),
    url(r'^metadata-download/$', UserDownloadInfoAPI.as_view(), name='metadata-download'),
    url(r'^metadata-info-name/$', UserMetadataOnlyNameInfoAPI.as_view(), name='metadata-info-name'),
    url(r'^metadata-stats-state/$', UserMetadataStateStatsAPI.as_view(), name='metadata-stats-state'),
]