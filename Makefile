OBS_PROJECT := EA4-experimental
OBS_PACKAGE := ea-nginx-passenger
DISABLE_BUILD := arch=i586 repository=CentOS_6.5_standard repository=CentOS_7
include $(EATOOLS_BUILD_DIR)obs.mk
