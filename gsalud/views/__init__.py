from .userViews import getUsers,registerUser
from .configsViews import config_list,getFilterOptions,set_config_cols,config_cols
from .dailySetupViews import post_assignment, post_db
from .recordsViews import getRecords,getRecordsInfos
from .providersViews import getProviders
from .admission import login,is_auth