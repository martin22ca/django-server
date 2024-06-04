from django.urls import path
from gsalud.views.configsViews import config_list, getFilterOptions, set_config_cols, config_cols
from gsalud.views.dailySetupViews import post_assignment, post_db, post_lots

urlpatterns = [
    path('', config_list),
    path('cols', config_cols),
    path('setCols', set_config_cols),
    path('filters', getFilterOptions),
    path('assignment', post_assignment),
    path('lots', post_lots),
    path('db', post_db)
]
