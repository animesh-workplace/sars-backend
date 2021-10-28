from django.urls import path, include, re_path
from .modules.landing_stats import LandingStatsAPI
from .modules.upload import UserFileUploadHandlerAPI
from .modules.download_info import UserDownloadInfoAPI
from .modules.metadata_upload import UserMetadataUploadAPI
from .modules.metadata_stats import UserMetadataStatsAPI, UserMetadataStateStatsAPI
from .modules.metadata_info import UserMetadataInfoAPI, UserMetadataOnlyNameInfoAPI

urlpatterns = [
    path('landing-stats/', LandingStatsAPI.as_view(), name='landing-stats'),
    path('metadata-info/', UserMetadataInfoAPI.as_view(), name='metadata-info'),
    path('file-upload/', UserFileUploadHandlerAPI.as_view(), name='file-upload'),
    path('metadata-stats/', UserMetadataStatsAPI.as_view(), name='metadata-stats'),
    path('metadata-upload/', UserMetadataUploadAPI.as_view(), name='metadata-upload'),
    path('metadata-download/', UserDownloadInfoAPI.as_view(), name='metadata-download'),
    path('metadata-info-name/', UserMetadataOnlyNameInfoAPI.as_view(), name='metadata-info-name'),
    path('metadata-stats-state/', UserMetadataStateStatsAPI.as_view(), name='metadata-stats-state'),
]
